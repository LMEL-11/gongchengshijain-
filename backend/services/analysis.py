"""Analysis services: aggregate statistics used by the dashboard & charts."""
from collections import Counter, defaultdict
from datetime import date, timedelta
from math import log1p
from statistics import median

from sqlalchemy import func

from extensions import db
from models import City, District, Property
from services.property_details import get_property_details


def overview() -> dict:
    """Platform-wide headline numbers for the dashboard stat cards."""
    # 总览卡片直接从房源表做聚合，返回的是全平台快照，不受城市/区域筛选影响。
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
    # 区域排行把 District 作为地图维度，把 Property 作为价格与数量来源，
    # 最终返回坐标、网格位置、均价和房源数，供 3D 地图和排行图共用。
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
    # 价格分布只取有效单价，并按固定桶宽落位到 lower-bound，便于前端绘制直方图。
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


def listing_profile(district_id: int) -> dict:
    """Current listing snapshot and transaction-attribute profile for a district."""
    # 挂牌画像先取区域内房源的基础价格/面积，再通过 source_url 关联交易扩展字段，
    # 将挂牌日期、产权、抵押和卖点标签汇总成前端可视化结构。
    rows = (
        db.session.query(
            Property.unit_price,
            Property.total_price,
            Property.area,
            Property.source_url,
        )
        .filter(Property.district_id == district_id)
        .all()
    )
    prices = [float(r.unit_price) for r in rows if r.unit_price]
    totals = [float(r.total_price) for r in rows if r.total_price]
    areas = [float(r.area) for r in rows if r.area]

    listing_dates = []
    monthly_counts = Counter()
    monthly_prices = defaultdict(list)
    ownership_counter = Counter()
    right_counter = Counter()
    mortgage_counter = Counter()
    tax_tags = Counter()
    detail_count = 0

    for row in rows:
        detail = get_property_details(row.source_url)
        if not detail:
            continue
        detail_count += 1

        # 挂牌日期用于构建 24 个月挂牌量和月均价走势；无法解析的日期不参与时间序列。
        listing_date = _parse_listing_date(detail.get("listing_date"))
        if listing_date:
            listing_dates.append(listing_date)
            month = listing_date.strftime("%Y-%m")
            monthly_counts[month] += 1
            if row.unit_price:
                monthly_prices[month].append(float(row.unit_price))

        _count_clean(ownership_counter, detail.get("ownership_type"))
        _count_clean(right_counter, detail.get("property_right"))

        # 交易属性统一清洗后再计数，避免“暂无数据/空字符串”等占位值污染分布。
        mortgage = _normalize_mortgage(detail.get("mortgage"))
        if mortgage:
            mortgage_counter[mortgage] += 1

        selling_point = detail.get("selling_point") or ""
        if "满五" in selling_point:
            tax_tags["满五"] += 1
        if any(token in selling_point for token in ("满二", "满两", "证满二", "证满两")):
            tax_tags["满二"] += 1
        if any(token in selling_point for token in ("有证", "房产证", "产权证")):
            tax_tags["有证"] += 1

    latest_month = None
    monthly = []
    if listing_dates:
        latest = max(listing_dates)
        latest_month = date(latest.year, latest.month, 1)
        # 以样本中最新挂牌月为右边界回看 24 个月，保证历史数据不完整时仍能对齐展示。
        for month_date in _month_window(latest_month, 24):
            month = month_date.strftime("%Y-%m")
            month_prices = monthly_prices.get(month, [])
            monthly.append(
                {
                    "month": month,
                    "count": int(monthly_counts.get(month, 0)),
                    "avg_unit_price": (
                        round(sum(month_prices) / len(month_prices))
                        if month_prices
                        else None
                    ),
                }
            )

    recent_ratio = 0
    if listing_dates:
        latest = max(listing_dates)
        recent_cutoff = latest - timedelta(days=365)
        recent_ratio = sum(1 for item in listing_dates if item >= recent_cutoff) / len(
            listing_dates
        )

    return {
        "district_id": district_id,
        "property_count": len(rows),
        "detail_count": detail_count,
        "date_count": len(listing_dates),
        "avg_unit_price": _rounded_average(prices),
        "median_unit_price": round(median(prices)) if prices else 0,
        "avg_total_price": _rounded_average(totals, digits=1),
        "avg_area": _rounded_average(areas, digits=1),
        "as_of_month": latest_month.strftime("%Y-%m") if latest_month else None,
        "recent_listing_ratio": round(recent_ratio * 100, 1),
        "monthly_listings": monthly,
        "ownership_distribution": _counter_items(ownership_counter),
        "property_right_distribution": _counter_items(right_counter),
        "mortgage_distribution": _counter_items(mortgage_counter),
        "tax_tags": _counter_items(tax_tags, total=detail_count),
    }


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

    # 先以行政区为粒度聚合房源均价和挂牌量，这是投资评分的价格/热度基础样本。
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

    # 配套设施按数量和类别覆盖度两个维度统计：数量代表密度，类别数代表生活便利性的广度。
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

    # 交易安全和挂牌新鲜度来自 PropertyTransaction 扩展信息，通过 source_url 回连房源。
    transaction_stats = _transaction_scores(city_id)
    max_facilities = max(
        [s["facility_count"] for s in facility_stats.values()] or [0]
    )

    def _norm(value, lo, hi):
        """将指标值按上下界归一化到 0 到 1 区间。"""
        return (value - lo) / (hi - lo) if hi > lo else 0.5

    for r in rows:
        # Low prices receive a higher value score. Areas above the city median
        # still receive a small score if they are not the most expensive.
        if r["avg_unit_price"] <= p_mid:
            value_score = _norm(p_mid - r["avg_unit_price"], 0, p_mid - p_lo)
        else:
            value_score = 0.35 * (1 - _norm(r["avg_unit_price"], p_mid, p_hi))

        # 使用 log1p 压缩挂牌量，避免超大商圈仅凭数量把热度分拉满。
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

        # 五项指标统一转成 0-1 后再按权重合成，返回给前端时再换算成百分制。
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

    # 这里只读取 district_id 和 source_url，再按需加载详情，避免把房源主体大字段全部取出。
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

    # “近期挂牌”以当前样本里最新挂牌日为参照，适配离线采集数据的时间截面。
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
    """根据产权、抵押和税费标签计算交易安全评分。"""
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
    """解析挂牌日期文本并转换为日期对象。"""
    from datetime import datetime

    if not value:
        return None
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _rounded_average(values, digits=0):
    """计算数值列表平均值并按指定位数取整。"""
    if not values:
        return 0
    value = sum(values) / len(values)
    return round(value, digits) if digits else round(value)


def _count_clean(counter, value):
    """清理文本后写入计数器，忽略空值。"""
    text = (value or "").strip()
    if text:
        counter[text] += 1


def _normalize_mortgage(value):
    """将抵押信息文本归一化为前端可展示的分类。"""
    text = (value or "").strip()
    if not text:
        return None
    if "无抵押" in text:
        return "无抵押"
    if "抵押" in text:
        return "有抵押"
    return text[:16]


def _counter_items(counter, total=None, limit=8):
    """把计数器转换为带数量和占比的列表。"""
    denominator = total or sum(counter.values())
    if not denominator:
        return []
    return [
        {
            "name": name,
            "count": int(count),
            "ratio": round(count / denominator * 100, 1),
        }
        for name, count in counter.most_common(limit)
    ]


def _month_window(end_month, count):
    """生成指定结束月份之前的连续月份窗口。"""
    return [_shift_months(end_month, offset) for offset in range(1 - count, 1)]


def _shift_months(month, offset):
    """按月偏移日期并返回月份起始日。"""
    month_index = month.year * 12 + month.month - 1 + offset
    return date(month_index // 12, month_index % 12 + 1, 1)
