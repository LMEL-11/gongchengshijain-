"""Analysis services: aggregate statistics used by the dashboard & charts."""
from collections import defaultdict
from datetime import timedelta
from math import log1p
from statistics import median

from sqlalchemy import func

from extensions import db
from models import City, District, Property
from services.property_details import get_property_details


def overview() -> dict:
    """Platform-wide headline numbers for the dashboard stat cards."""
    total = db.session.query(func.count(Property.id)).scalar() or 0
    avg_unit = db.session.query(func.avg(Property.unit_price)).scalar() or 0
    max_unit = db.session.query(func.max(Property.unit_price)).scalar() or 0
    min_unit = db.session.query(func.min(Property.unit_price)).scalar() or 0
    city_count = db.session.query(func.count(City.id)).scalar() or 0
    return {
        "property_count": int(total),
        "city_count": int(city_count),
        "avg_unit_price": round(avg_unit),
        "max_unit_price": round(max_unit),
        "min_unit_price": round(min_unit),
    }


def district_ranking(city_id: int) -> list[dict]:
    """Districts of a city ranked by average price/㎡ (drives the 3D map)."""
    rows = (
        db.session.query(
            District.id,
            District.name,
            District.lng,
            District.lat,
            District.grid_x,
            District.grid_y,
            func.avg(Property.unit_price).label("avg_unit_price"),
            func.count(Property.id).label("property_count"),
        )
        .join(Property, Property.district_id == District.id)
        .filter(District.city_id == city_id)
        .group_by(District.id)
        .order_by(func.avg(Property.unit_price).desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "name": r.name,
            "lng": r.lng,
            "lat": r.lat,
            "grid_x": r.grid_x,
            "grid_y": r.grid_y,
            "avg_unit_price": round(r.avg_unit_price or 0),
            "property_count": int(r.property_count),
        }
        for r in rows
    ]


def price_distribution(city_id: int, bucket_size: int = 10000) -> list[dict]:
    """Histogram of unit prices for a city, bucketed by ``bucket_size`` 元/㎡."""
    prices = (
        db.session.query(Property.unit_price)
        .join(District, Property.district_id == District.id)
        .filter(District.city_id == city_id, Property.unit_price.isnot(None))
        .all()
    )
    buckets: dict[int, int] = {}
    for (price,) in prices:
        key = int(price // bucket_size) * bucket_size
        buckets[key] = buckets.get(key, 0) + 1
    return [
        {
            "range": f"{lo // 10000}-{(lo + bucket_size) // 10000}万",
            "lower": lo,
            "count": buckets[lo],
        }
        for lo in sorted(buckets)
    ]


def price_trend(district_id: int) -> list[dict]:
    """Monthly average-price series for a district."""
    from models import PriceHistory

    rows = (
        db.session.query(PriceHistory)
        .filter(PriceHistory.district_id == district_id)
        .order_by(PriceHistory.month.asc())
        .all()
    )
    return [r.to_dict() for r in rows]


def investment_ranking(city_id: int) -> list[dict]:
    """Rank districts by a potential score based on the current data snapshot.

    The current real dataset has listing dates and transaction attributes, but
    no reliable month-by-month historical growth. The score therefore combines:
      - 价格洼地 value_score       35%
      - 市场热度 heat_score        25%
      - 周边配套 facility_score    20%
      - 交易安全 safety_score      10%
      - 挂牌新鲜度 freshness_score 10%
    """
    from models import Facility

    rows = [
        {
            "id": r.id,
            "name": r.name,
            "avg_unit_price": round(r.avg_unit_price or 0),
            "property_count": int(r.property_count or 0),
        }
        for r in (
            db.session.query(
                District.id,
                District.name,
                func.avg(Property.unit_price).label("avg_unit_price"),
                func.count(Property.id).label("property_count"),
            )
            .join(Property, Property.district_id == District.id)
            .filter(District.city_id == city_id, Property.unit_price.isnot(None))
            .group_by(District.id)
            .all()
        )
        if r.avg_unit_price
    ]
    if not rows:
        return []

    row_by_id = {r["id"]: r for r in rows}
    prices = [r["avg_unit_price"] for r in rows]
    counts = [r["property_count"] for r in rows]
    p_lo, p_hi, p_mid = min(prices), max(prices), median(prices)
    c_lo, c_hi = min(counts), max(counts)

    facility_stats = {
        district_id: {"facility_count": int(count), "facility_category_count": int(categories)}
        for district_id, count, categories in (
            db.session.query(
                Facility.district_id,
                func.count(Facility.id),
                func.count(func.distinct(Facility.category)),
            )
            .filter(Facility.district_id.in_(row_by_id))
            .group_by(Facility.district_id)
            .all()
        )
    }

    transaction_stats = _transaction_scores(city_id)
    max_facilities = max(
        [s["facility_count"] for s in facility_stats.values()] or [0]
    )

    def _norm(value, lo, hi):
        return (value - lo) / (hi - lo) if hi > lo else 0.5

    for r in rows:
        # Low prices receive a higher value score. Areas above the city median
        # still receive a small score if they are not the most expensive.
        if r["avg_unit_price"] <= p_mid:
            value_score = _norm(p_mid - r["avg_unit_price"], 0, p_mid - p_lo)
        else:
            value_score = 0.35 * (1 - _norm(r["avg_unit_price"], p_mid, p_hi))

        heat_score = _norm(log1p(r["property_count"]), log1p(c_lo), log1p(c_hi))
        fac = facility_stats.get(r["id"], {"facility_count": 0, "facility_category_count": 0})
        facility_count_score = (
            fac["facility_count"] / max_facilities if max_facilities else 0
        )
        facility_cover_score = min(fac["facility_category_count"], 5) / 5
        facility_score = 0.55 * facility_count_score + 0.45 * facility_cover_score

        transaction = transaction_stats.get(r["id"], {})
        safety_score = transaction.get("safety_score", 0.5)
        freshness_score = transaction.get("freshness_score", 0.5)
        heat_index = 0.55 * heat_score + 0.45 * facility_score

        score = (
            0.35 * value_score
            + 0.25 * heat_score
            + 0.20 * facility_score
            + 0.10 * safety_score
            + 0.10 * freshness_score
        )
        r.update(
            {
                "facility_count": fac["facility_count"],
                "facility_category_count": fac["facility_category_count"],
                "heat_index": round(heat_index * 100),
                "value_score": round(value_score * 100),
                "heat_score": round(heat_score * 100),
                "facility_score": round(facility_score * 100),
                "safety_score": round(safety_score * 100),
                "freshness_score": round(freshness_score * 100),
                "recent_listing_ratio": round(
                    transaction.get("recent_listing_ratio", 0) * 100
                ),
                "score": round(score * 100),
            }
        )

    rows.sort(key=lambda x: x["score"], reverse=True)
    return rows


def _transaction_scores(city_id: int) -> dict[int, dict]:
    """Aggregate transaction safety and listing freshness by district."""
    parsed = []
    safety_sum = defaultdict(float)
    safety_count = defaultdict(int)
    listing_dates = defaultdict(list)

    rows = (
        db.session.query(Property.district_id, Property.source_url)
        .join(District, Property.district_id == District.id)
        .filter(District.city_id == city_id, Property.source_url.isnot(None))
        .all()
    )
    for district_id, source_url in rows:
        detail = get_property_details(source_url)
        if not detail:
            continue

        safety_sum[district_id] += _safety_score(detail)
        safety_count[district_id] += 1

        listing_date = _parse_listing_date(detail.get("listing_date"))
        if listing_date:
            listing_dates[district_id].append(listing_date)
            parsed.append(listing_date)

    latest = max(parsed) if parsed else None
    recent_cutoff = latest - timedelta(days=365) if latest else None
    result = {}
    district_ids = set(safety_count) | set(listing_dates)
    for district_id in district_ids:
        dates = listing_dates.get(district_id, [])
        recent = (
            sum(1 for date in dates if date >= recent_cutoff) / len(dates)
            if dates and recent_cutoff
            else 0.5
        )
        result[district_id] = {
            "safety_score": (
                safety_sum[district_id] / safety_count[district_id]
                if safety_count[district_id]
                else 0.5
            ),
            "freshness_score": recent,
            "recent_listing_ratio": recent,
        }
    return result


def _safety_score(detail: dict) -> float:
    score = 0.0
    ownership = detail.get("ownership_type") or ""
    right = detail.get("property_right") or ""
    mortgage = detail.get("mortgage") or ""
    selling_point = detail.get("selling_point") or ""

    if "商品房" in ownership:
        score += 0.35
    elif "已购公房" in ownership:
        score += 0.25
    elif ownership:
        score += 0.15

    if "非共有" in right:
        score += 0.25
    elif "共有" in right:
        score += 0.12

    if "无抵押" in mortgage:
        score += 0.25
    elif mortgage:
        score += 0.08

    if any(token in selling_point for token in ("满五", "满二", "有证", "证满")):
        score += 0.15

    return min(score, 1.0)


def _parse_listing_date(value):
    from datetime import datetime

    if not value:
        return None
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None
