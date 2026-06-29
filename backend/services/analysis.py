"""Analysis services: aggregate statistics used by the dashboard & charts."""
from collections import Counter, defaultdict  # 逐行注释：导入本行所需的模块或对象。
from datetime import date, timedelta  # 逐行注释：导入本行所需的模块或对象。
from math import log1p  # 逐行注释：导入本行所需的模块或对象。
from statistics import median  # 逐行注释：导入本行所需的模块或对象。

from sqlalchemy import func  # 逐行注释：导入本行所需的模块或对象。

from extensions import db  # 逐行注释：导入本行所需的模块或对象。
from models import City, District, Property  # 逐行注释：导入本行所需的模块或对象。
from services.property_details import get_property_details  # 逐行注释：导入本行所需的模块或对象。


def overview() -> dict:  # 逐行注释：声明函数或方法入口。
    """Platform-wide headline numbers for the dashboard stat cards."""
    total = db.session.query(func.count(Property.id)).scalar() or 0  # 逐行注释：赋值或更新当前变量/字段。
    avg_unit = db.session.query(func.avg(Property.unit_price)).scalar() or 0  # 逐行注释：赋值或更新当前变量/字段。
    max_unit = db.session.query(func.max(Property.unit_price)).scalar() or 0  # 逐行注释：赋值或更新当前变量/字段。
    min_unit = db.session.query(func.min(Property.unit_price)).scalar() or 0  # 逐行注释：赋值或更新当前变量/字段。
    city_count = db.session.query(func.count(City.id)).scalar() or 0  # 逐行注释：赋值或更新当前变量/字段。
    return {  # 逐行注释：返回当前逻辑的处理结果。
        "property_count": int(total),  # 逐行注释：设置当前数据项或参数。
        "city_count": int(city_count),  # 逐行注释：设置当前数据项或参数。
        "avg_unit_price": round(avg_unit),  # 逐行注释：设置当前数据项或参数。
        "max_unit_price": round(max_unit),  # 逐行注释：设置当前数据项或参数。
        "min_unit_price": round(min_unit),  # 逐行注释：设置当前数据项或参数。
    }  # 逐行注释：结束当前数据结构或调用块。


def district_ranking(city_id: int) -> list[dict]:  # 逐行注释：声明函数或方法入口。
    """Districts of a city ranked by average price/㎡ (drives the 3D map)."""
    rows = (  # 逐行注释：赋值或更新当前变量/字段。
        db.session.query(  # 逐行注释：执行本行代码逻辑。
            District.id,  # 逐行注释：设置当前数据项或参数。
            District.name,  # 逐行注释：设置当前数据项或参数。
            District.lng,  # 逐行注释：设置当前数据项或参数。
            District.lat,  # 逐行注释：设置当前数据项或参数。
            District.grid_x,  # 逐行注释：设置当前数据项或参数。
            District.grid_y,  # 逐行注释：设置当前数据项或参数。
            func.avg(Property.unit_price).label("avg_unit_price"),  # 逐行注释：设置当前数据项或参数。
            func.count(Property.id).label("property_count"),  # 逐行注释：设置当前数据项或参数。
        )  # 逐行注释：结束当前数据结构或调用块。
        .join(Property, Property.district_id == District.id)  # 逐行注释：执行本行代码逻辑。
        .filter(District.city_id == city_id)  # 逐行注释：执行本行代码逻辑。
        .group_by(District.id)  # 逐行注释：执行本行代码逻辑。
        .order_by(func.avg(Property.unit_price).desc())  # 逐行注释：执行本行代码逻辑。
        .all()  # 逐行注释：执行本行代码逻辑。
    )  # 逐行注释：结束当前数据结构或调用块。
    return [  # 逐行注释：返回当前逻辑的处理结果。
        {  # 逐行注释：执行本行代码逻辑。
            "id": r.id,  # 逐行注释：设置当前数据项或参数。
            "name": r.name,  # 逐行注释：设置当前数据项或参数。
            "lng": r.lng,  # 逐行注释：设置当前数据项或参数。
            "lat": r.lat,  # 逐行注释：设置当前数据项或参数。
            "grid_x": r.grid_x,  # 逐行注释：设置当前数据项或参数。
            "grid_y": r.grid_y,  # 逐行注释：设置当前数据项或参数。
            "avg_unit_price": round(r.avg_unit_price or 0),  # 逐行注释：设置当前数据项或参数。
            "property_count": int(r.property_count),  # 逐行注释：设置当前数据项或参数。
        }  # 逐行注释：结束当前数据结构或调用块。
        for r in rows  # 逐行注释：遍历集合中的每一项并执行处理。
    ]  # 逐行注释：结束当前数据结构或调用块。


def price_distribution(city_id: int, bucket_size: int = 10000) -> list[dict]:  # 逐行注释：声明函数或方法入口。
    """Histogram of unit prices for a city, bucketed by ``bucket_size`` 元/㎡."""
    prices = (  # 逐行注释：赋值或更新当前变量/字段。
        db.session.query(Property.unit_price)  # 逐行注释：执行本行代码逻辑。
        .join(District, Property.district_id == District.id)  # 逐行注释：执行本行代码逻辑。
        .filter(District.city_id == city_id, Property.unit_price.isnot(None))  # 逐行注释：执行本行代码逻辑。
        .all()  # 逐行注释：执行本行代码逻辑。
    )  # 逐行注释：结束当前数据结构或调用块。
    buckets: dict[int, int] = {}  # 逐行注释：赋值或更新当前变量/字段。
    for (price,) in prices:  # 逐行注释：遍历集合中的每一项并执行处理。
        key = int(price // bucket_size) * bucket_size  # 逐行注释：赋值或更新当前变量/字段。
        buckets[key] = buckets.get(key, 0) + 1  # 逐行注释：赋值或更新当前变量/字段。
    return [  # 逐行注释：返回当前逻辑的处理结果。
        {  # 逐行注释：执行本行代码逻辑。
            "range": f"{lo // 10000}-{(lo + bucket_size) // 10000}万",  # 逐行注释：设置当前数据项或参数。
            "lower": lo,  # 逐行注释：设置当前数据项或参数。
            "count": buckets[lo],  # 逐行注释：设置当前数据项或参数。
        }  # 逐行注释：结束当前数据结构或调用块。
        for lo in sorted(buckets)  # 逐行注释：遍历集合中的每一项并执行处理。
    ]  # 逐行注释：结束当前数据结构或调用块。


def price_trend(district_id: int) -> list[dict]:  # 逐行注释：声明函数或方法入口。
    """Monthly average-price series for a district."""
    from models import PriceHistory  # 逐行注释：导入本行所需的模块或对象。

    rows = (  # 逐行注释：赋值或更新当前变量/字段。
        db.session.query(PriceHistory)  # 逐行注释：执行本行代码逻辑。
        .filter(PriceHistory.district_id == district_id)  # 逐行注释：执行本行代码逻辑。
        .order_by(PriceHistory.month.asc())  # 逐行注释：执行本行代码逻辑。
        .all()  # 逐行注释：执行本行代码逻辑。
    )  # 逐行注释：结束当前数据结构或调用块。
    return [r.to_dict() for r in rows]  # 逐行注释：返回当前逻辑的处理结果。


def listing_profile(district_id: int) -> dict:  # 逐行注释：声明函数或方法入口。
    """Current listing snapshot and transaction-attribute profile for a district."""
    rows = (  # 逐行注释：赋值或更新当前变量/字段。
        db.session.query(  # 逐行注释：执行本行代码逻辑。
            Property.unit_price,  # 逐行注释：设置当前数据项或参数。
            Property.total_price,  # 逐行注释：设置当前数据项或参数。
            Property.area,  # 逐行注释：设置当前数据项或参数。
            Property.source_url,  # 逐行注释：设置当前数据项或参数。
        )  # 逐行注释：结束当前数据结构或调用块。
        .filter(Property.district_id == district_id)  # 逐行注释：执行本行代码逻辑。
        .all()  # 逐行注释：执行本行代码逻辑。
    )  # 逐行注释：结束当前数据结构或调用块。
    prices = [float(r.unit_price) for r in rows if r.unit_price]  # 逐行注释：赋值或更新当前变量/字段。
    totals = [float(r.total_price) for r in rows if r.total_price]  # 逐行注释：赋值或更新当前变量/字段。
    areas = [float(r.area) for r in rows if r.area]  # 逐行注释：赋值或更新当前变量/字段。

    listing_dates = []  # 逐行注释：赋值或更新当前变量/字段。
    monthly_counts = Counter()  # 逐行注释：赋值或更新当前变量/字段。
    monthly_prices = defaultdict(list)  # 逐行注释：赋值或更新当前变量/字段。
    ownership_counter = Counter()  # 逐行注释：赋值或更新当前变量/字段。
    right_counter = Counter()  # 逐行注释：赋值或更新当前变量/字段。
    mortgage_counter = Counter()  # 逐行注释：赋值或更新当前变量/字段。
    tax_tags = Counter()  # 逐行注释：赋值或更新当前变量/字段。
    detail_count = 0  # 逐行注释：赋值或更新当前变量/字段。

    for row in rows:  # 逐行注释：遍历集合中的每一项并执行处理。
        detail = get_property_details(row.source_url)  # 逐行注释：赋值或更新当前变量/字段。
        if not detail:  # 逐行注释：根据条件判断是否进入该分支。
            continue  # 逐行注释：跳过本轮循环剩余逻辑。
        detail_count += 1  # 逐行注释：赋值或更新当前变量/字段。

        listing_date = _parse_listing_date(detail.get("listing_date"))  # 逐行注释：赋值或更新当前变量/字段。
        if listing_date:  # 逐行注释：根据条件判断是否进入该分支。
            listing_dates.append(listing_date)  # 逐行注释：执行本行代码逻辑。
            month = listing_date.strftime("%Y-%m")  # 逐行注释：赋值或更新当前变量/字段。
            monthly_counts[month] += 1  # 逐行注释：赋值或更新当前变量/字段。
            if row.unit_price:  # 逐行注释：根据条件判断是否进入该分支。
                monthly_prices[month].append(float(row.unit_price))  # 逐行注释：执行本行代码逻辑。

        _count_clean(ownership_counter, detail.get("ownership_type"))  # 逐行注释：执行本行代码逻辑。
        _count_clean(right_counter, detail.get("property_right"))  # 逐行注释：执行本行代码逻辑。

        mortgage = _normalize_mortgage(detail.get("mortgage"))  # 逐行注释：赋值或更新当前变量/字段。
        if mortgage:  # 逐行注释：根据条件判断是否进入该分支。
            mortgage_counter[mortgage] += 1  # 逐行注释：赋值或更新当前变量/字段。

        selling_point = detail.get("selling_point") or ""  # 逐行注释：赋值或更新当前变量/字段。
        if "满五" in selling_point:  # 逐行注释：根据条件判断是否进入该分支。
            tax_tags["满五"] += 1  # 逐行注释：赋值或更新当前变量/字段。
        if any(token in selling_point for token in ("满二", "满两", "证满二", "证满两")):  # 逐行注释：根据条件判断是否进入该分支。
            tax_tags["满二"] += 1  # 逐行注释：赋值或更新当前变量/字段。
        if any(token in selling_point for token in ("有证", "房产证", "产权证")):  # 逐行注释：根据条件判断是否进入该分支。
            tax_tags["有证"] += 1  # 逐行注释：赋值或更新当前变量/字段。

    latest_month = None  # 逐行注释：赋值或更新当前变量/字段。
    monthly = []  # 逐行注释：赋值或更新当前变量/字段。
    if listing_dates:  # 逐行注释：根据条件判断是否进入该分支。
        latest = max(listing_dates)  # 逐行注释：赋值或更新当前变量/字段。
        latest_month = date(latest.year, latest.month, 1)  # 逐行注释：赋值或更新当前变量/字段。
        for month_date in _month_window(latest_month, 24):  # 逐行注释：遍历集合中的每一项并执行处理。
            month = month_date.strftime("%Y-%m")  # 逐行注释：赋值或更新当前变量/字段。
            month_prices = monthly_prices.get(month, [])  # 逐行注释：赋值或更新当前变量/字段。
            monthly.append(  # 逐行注释：执行本行代码逻辑。
                {  # 逐行注释：执行本行代码逻辑。
                    "month": month,  # 逐行注释：设置当前数据项或参数。
                    "count": int(monthly_counts.get(month, 0)),  # 逐行注释：设置当前数据项或参数。
                    "avg_unit_price": (  # 逐行注释：设置当前数据项或参数。
                        round(sum(month_prices) / len(month_prices))  # 逐行注释：执行本行代码逻辑。
                        if month_prices  # 逐行注释：根据条件判断是否进入该分支。
                        else None  # 逐行注释：处理条件不满足时的兜底分支。
                    ),  # 逐行注释：结束当前数据结构或调用块。
                }  # 逐行注释：结束当前数据结构或调用块。
            )  # 逐行注释：结束当前数据结构或调用块。

    recent_ratio = 0  # 逐行注释：赋值或更新当前变量/字段。
    if listing_dates:  # 逐行注释：根据条件判断是否进入该分支。
        latest = max(listing_dates)  # 逐行注释：赋值或更新当前变量/字段。
        recent_cutoff = latest - timedelta(days=365)  # 逐行注释：赋值或更新当前变量/字段。
        recent_ratio = sum(1 for item in listing_dates if item >= recent_cutoff) / len(  # 逐行注释：执行本行代码逻辑。
            listing_dates  # 逐行注释：执行本行代码逻辑。
        )  # 逐行注释：结束当前数据结构或调用块。

    return {  # 逐行注释：返回当前逻辑的处理结果。
        "district_id": district_id,  # 逐行注释：设置当前数据项或参数。
        "property_count": len(rows),  # 逐行注释：设置当前数据项或参数。
        "detail_count": detail_count,  # 逐行注释：设置当前数据项或参数。
        "date_count": len(listing_dates),  # 逐行注释：设置当前数据项或参数。
        "avg_unit_price": _rounded_average(prices),  # 逐行注释：设置当前数据项或参数。
        "median_unit_price": round(median(prices)) if prices else 0,  # 逐行注释：设置当前数据项或参数。
        "avg_total_price": _rounded_average(totals, digits=1),  # 逐行注释：赋值或更新当前变量/字段。
        "avg_area": _rounded_average(areas, digits=1),  # 逐行注释：赋值或更新当前变量/字段。
        "as_of_month": latest_month.strftime("%Y-%m") if latest_month else None,  # 逐行注释：设置当前数据项或参数。
        "recent_listing_ratio": round(recent_ratio * 100, 1),  # 逐行注释：设置当前数据项或参数。
        "monthly_listings": monthly,  # 逐行注释：设置当前数据项或参数。
        "ownership_distribution": _counter_items(ownership_counter),  # 逐行注释：设置当前数据项或参数。
        "property_right_distribution": _counter_items(right_counter),  # 逐行注释：设置当前数据项或参数。
        "mortgage_distribution": _counter_items(mortgage_counter),  # 逐行注释：设置当前数据项或参数。
        "tax_tags": _counter_items(tax_tags, total=detail_count),  # 逐行注释：赋值或更新当前变量/字段。
    }  # 逐行注释：结束当前数据结构或调用块。


def investment_ranking(city_id: int) -> list[dict]:  # 逐行注释：声明函数或方法入口。
    """Rank districts by a potential score based on the current data snapshot.

    The current real dataset has listing dates and transaction attributes, but
    no reliable month-by-month historical growth. The score therefore combines:
      - 价格洼地 value_score       35%
      - 市场热度 heat_score        25%
      - 周边配套 facility_score    20%
      - 交易安全 safety_score      10%
      - 挂牌新鲜度 freshness_score 10%
    """
    from models import Facility  # 逐行注释：导入本行所需的模块或对象。

    rows = [  # 逐行注释：赋值或更新当前变量/字段。
        {  # 逐行注释：执行本行代码逻辑。
            "id": r.id,  # 逐行注释：设置当前数据项或参数。
            "name": r.name,  # 逐行注释：设置当前数据项或参数。
            "avg_unit_price": round(r.avg_unit_price or 0),  # 逐行注释：设置当前数据项或参数。
            "property_count": int(r.property_count or 0),  # 逐行注释：设置当前数据项或参数。
        }  # 逐行注释：结束当前数据结构或调用块。
        for r in (  # 逐行注释：遍历集合中的每一项并执行处理。
            db.session.query(  # 逐行注释：执行本行代码逻辑。
                District.id,  # 逐行注释：设置当前数据项或参数。
                District.name,  # 逐行注释：设置当前数据项或参数。
                func.avg(Property.unit_price).label("avg_unit_price"),  # 逐行注释：设置当前数据项或参数。
                func.count(Property.id).label("property_count"),  # 逐行注释：设置当前数据项或参数。
            )  # 逐行注释：结束当前数据结构或调用块。
            .join(Property, Property.district_id == District.id)  # 逐行注释：执行本行代码逻辑。
            .filter(District.city_id == city_id, Property.unit_price.isnot(None))  # 逐行注释：执行本行代码逻辑。
            .group_by(District.id)  # 逐行注释：执行本行代码逻辑。
            .all()  # 逐行注释：执行本行代码逻辑。
        )  # 逐行注释：结束当前数据结构或调用块。
        if r.avg_unit_price  # 逐行注释：根据条件判断是否进入该分支。
    ]  # 逐行注释：结束当前数据结构或调用块。
    if not rows:  # 逐行注释：根据条件判断是否进入该分支。
        return []  # 逐行注释：返回当前逻辑的处理结果。

    row_by_id = {r["id"]: r for r in rows}  # 逐行注释：赋值或更新当前变量/字段。
    prices = [r["avg_unit_price"] for r in rows]  # 逐行注释：赋值或更新当前变量/字段。
    counts = [r["property_count"] for r in rows]  # 逐行注释：赋值或更新当前变量/字段。
    p_lo, p_hi, p_mid = min(prices), max(prices), median(prices)  # 逐行注释：赋值或更新当前变量/字段。
    c_lo, c_hi = min(counts), max(counts)  # 逐行注释：赋值或更新当前变量/字段。

    facility_stats = {  # 逐行注释：赋值或更新当前变量/字段。
        district_id: {"facility_count": int(count), "facility_category_count": int(categories)}  # 逐行注释：设置当前数据项或参数。
        for district_id, count, categories in (  # 逐行注释：遍历集合中的每一项并执行处理。
            db.session.query(  # 逐行注释：执行本行代码逻辑。
                Facility.district_id,  # 逐行注释：设置当前数据项或参数。
                func.count(Facility.id),  # 逐行注释：设置当前数据项或参数。
                func.count(func.distinct(Facility.category)),  # 逐行注释：设置当前数据项或参数。
            )  # 逐行注释：结束当前数据结构或调用块。
            .filter(Facility.district_id.in_(row_by_id))  # 逐行注释：执行本行代码逻辑。
            .group_by(Facility.district_id)  # 逐行注释：执行本行代码逻辑。
            .all()  # 逐行注释：执行本行代码逻辑。
        )  # 逐行注释：结束当前数据结构或调用块。
    }  # 逐行注释：结束当前数据结构或调用块。

    transaction_stats = _transaction_scores(city_id)  # 逐行注释：赋值或更新当前变量/字段。
    max_facilities = max(  # 逐行注释：赋值或更新当前变量/字段。
        [s["facility_count"] for s in facility_stats.values()] or [0]  # 逐行注释：执行本行代码逻辑。
    )  # 逐行注释：结束当前数据结构或调用块。

    def _norm(value, lo, hi):  # 逐行注释：声明函数或方法入口。
        """将指标值按上下界归一化到 0 到 1 区间。"""
        return (value - lo) / (hi - lo) if hi > lo else 0.5  # 逐行注释：返回当前逻辑的处理结果。

    for r in rows:  # 逐行注释：遍历集合中的每一项并执行处理。
        # Low prices receive a higher value score. Areas above the city median
        # still receive a small score if they are not the most expensive.
        if r["avg_unit_price"] <= p_mid:  # 逐行注释：根据条件判断是否进入该分支。
            value_score = _norm(p_mid - r["avg_unit_price"], 0, p_mid - p_lo)  # 逐行注释：赋值或更新当前变量/字段。
        else:  # 逐行注释：处理条件不满足时的兜底分支。
            value_score = 0.35 * (1 - _norm(r["avg_unit_price"], p_mid, p_hi))  # 逐行注释：赋值或更新当前变量/字段。

        heat_score = _norm(log1p(r["property_count"]), log1p(c_lo), log1p(c_hi))  # 逐行注释：赋值或更新当前变量/字段。
        fac = facility_stats.get(r["id"], {"facility_count": 0, "facility_category_count": 0})  # 逐行注释：赋值或更新当前变量/字段。
        facility_count_score = (  # 逐行注释：赋值或更新当前变量/字段。
            fac["facility_count"] / max_facilities if max_facilities else 0  # 逐行注释：执行本行代码逻辑。
        )  # 逐行注释：结束当前数据结构或调用块。
        facility_cover_score = min(fac["facility_category_count"], 5) / 5  # 逐行注释：赋值或更新当前变量/字段。
        facility_score = 0.55 * facility_count_score + 0.45 * facility_cover_score  # 逐行注释：赋值或更新当前变量/字段。

        transaction = transaction_stats.get(r["id"], {})  # 逐行注释：赋值或更新当前变量/字段。
        safety_score = transaction.get("safety_score", 0.5)  # 逐行注释：赋值或更新当前变量/字段。
        freshness_score = transaction.get("freshness_score", 0.5)  # 逐行注释：赋值或更新当前变量/字段。
        heat_index = 0.55 * heat_score + 0.45 * facility_score  # 逐行注释：赋值或更新当前变量/字段。

        score = (  # 逐行注释：赋值或更新当前变量/字段。
            0.35 * value_score  # 逐行注释：执行本行代码逻辑。
            + 0.25 * heat_score  # 逐行注释：执行本行代码逻辑。
            + 0.20 * facility_score  # 逐行注释：执行本行代码逻辑。
            + 0.10 * safety_score  # 逐行注释：执行本行代码逻辑。
            + 0.10 * freshness_score  # 逐行注释：执行本行代码逻辑。
        )  # 逐行注释：结束当前数据结构或调用块。
        r.update(  # 逐行注释：执行本行代码逻辑。
            {  # 逐行注释：执行本行代码逻辑。
                "facility_count": fac["facility_count"],  # 逐行注释：设置当前数据项或参数。
                "facility_category_count": fac["facility_category_count"],  # 逐行注释：设置当前数据项或参数。
                "heat_index": round(heat_index * 100),  # 逐行注释：设置当前数据项或参数。
                "value_score": round(value_score * 100),  # 逐行注释：设置当前数据项或参数。
                "heat_score": round(heat_score * 100),  # 逐行注释：设置当前数据项或参数。
                "facility_score": round(facility_score * 100),  # 逐行注释：设置当前数据项或参数。
                "safety_score": round(safety_score * 100),  # 逐行注释：设置当前数据项或参数。
                "freshness_score": round(freshness_score * 100),  # 逐行注释：设置当前数据项或参数。
                "recent_listing_ratio": round(  # 逐行注释：设置当前数据项或参数。
                    transaction.get("recent_listing_ratio", 0) * 100  # 逐行注释：执行本行代码逻辑。
                ),  # 逐行注释：结束当前数据结构或调用块。
                "score": round(score * 100),  # 逐行注释：设置当前数据项或参数。
            }  # 逐行注释：结束当前数据结构或调用块。
        )  # 逐行注释：结束当前数据结构或调用块。

    rows.sort(key=lambda x: x["score"], reverse=True)  # 逐行注释：赋值或更新当前变量/字段。
    return rows  # 逐行注释：返回当前逻辑的处理结果。


def _transaction_scores(city_id: int) -> dict[int, dict]:  # 逐行注释：声明函数或方法入口。
    """Aggregate transaction safety and listing freshness by district."""
    parsed = []  # 逐行注释：赋值或更新当前变量/字段。
    safety_sum = defaultdict(float)  # 逐行注释：赋值或更新当前变量/字段。
    safety_count = defaultdict(int)  # 逐行注释：赋值或更新当前变量/字段。
    listing_dates = defaultdict(list)  # 逐行注释：赋值或更新当前变量/字段。

    rows = (  # 逐行注释：赋值或更新当前变量/字段。
        db.session.query(Property.district_id, Property.source_url)  # 逐行注释：执行本行代码逻辑。
        .join(District, Property.district_id == District.id)  # 逐行注释：执行本行代码逻辑。
        .filter(District.city_id == city_id, Property.source_url.isnot(None))  # 逐行注释：执行本行代码逻辑。
        .all()  # 逐行注释：执行本行代码逻辑。
    )  # 逐行注释：结束当前数据结构或调用块。
    for district_id, source_url in rows:  # 逐行注释：遍历集合中的每一项并执行处理。
        detail = get_property_details(source_url)  # 逐行注释：赋值或更新当前变量/字段。
        if not detail:  # 逐行注释：根据条件判断是否进入该分支。
            continue  # 逐行注释：跳过本轮循环剩余逻辑。

        safety_sum[district_id] += _safety_score(detail)  # 逐行注释：赋值或更新当前变量/字段。
        safety_count[district_id] += 1  # 逐行注释：赋值或更新当前变量/字段。

        listing_date = _parse_listing_date(detail.get("listing_date"))  # 逐行注释：赋值或更新当前变量/字段。
        if listing_date:  # 逐行注释：根据条件判断是否进入该分支。
            listing_dates[district_id].append(listing_date)  # 逐行注释：执行本行代码逻辑。
            parsed.append(listing_date)  # 逐行注释：执行本行代码逻辑。

    latest = max(parsed) if parsed else None  # 逐行注释：赋值或更新当前变量/字段。
    recent_cutoff = latest - timedelta(days=365) if latest else None  # 逐行注释：赋值或更新当前变量/字段。
    result = {}  # 逐行注释：赋值或更新当前变量/字段。
    district_ids = set(safety_count) | set(listing_dates)  # 逐行注释：赋值或更新当前变量/字段。
    for district_id in district_ids:  # 逐行注释：遍历集合中的每一项并执行处理。
        dates = listing_dates.get(district_id, [])  # 逐行注释：赋值或更新当前变量/字段。
        recent = (  # 逐行注释：赋值或更新当前变量/字段。
            sum(1 for date in dates if date >= recent_cutoff) / len(dates)  # 逐行注释：执行本行代码逻辑。
            if dates and recent_cutoff  # 逐行注释：根据条件判断是否进入该分支。
            else 0.5  # 逐行注释：处理条件不满足时的兜底分支。
        )  # 逐行注释：结束当前数据结构或调用块。
        result[district_id] = {  # 逐行注释：赋值或更新当前变量/字段。
            "safety_score": (  # 逐行注释：设置当前数据项或参数。
                safety_sum[district_id] / safety_count[district_id]  # 逐行注释：执行本行代码逻辑。
                if safety_count[district_id]  # 逐行注释：根据条件判断是否进入该分支。
                else 0.5  # 逐行注释：处理条件不满足时的兜底分支。
            ),  # 逐行注释：结束当前数据结构或调用块。
            "freshness_score": recent,  # 逐行注释：设置当前数据项或参数。
            "recent_listing_ratio": recent,  # 逐行注释：设置当前数据项或参数。
        }  # 逐行注释：结束当前数据结构或调用块。
    return result  # 逐行注释：返回当前逻辑的处理结果。


def _safety_score(detail: dict) -> float:  # 逐行注释：声明函数或方法入口。
    """根据产权、抵押和税费标签计算交易安全评分。"""
    score = 0.0  # 逐行注释：赋值或更新当前变量/字段。
    ownership = detail.get("ownership_type") or ""  # 逐行注释：赋值或更新当前变量/字段。
    right = detail.get("property_right") or ""  # 逐行注释：赋值或更新当前变量/字段。
    mortgage = detail.get("mortgage") or ""  # 逐行注释：赋值或更新当前变量/字段。
    selling_point = detail.get("selling_point") or ""  # 逐行注释：赋值或更新当前变量/字段。

    if "商品房" in ownership:  # 逐行注释：根据条件判断是否进入该分支。
        score += 0.35  # 逐行注释：赋值或更新当前变量/字段。
    elif "已购公房" in ownership:  # 逐行注释：根据条件判断是否进入该分支。
        score += 0.25  # 逐行注释：赋值或更新当前变量/字段。
    elif ownership:  # 逐行注释：根据条件判断是否进入该分支。
        score += 0.15  # 逐行注释：赋值或更新当前变量/字段。

    if "非共有" in right:  # 逐行注释：根据条件判断是否进入该分支。
        score += 0.25  # 逐行注释：赋值或更新当前变量/字段。
    elif "共有" in right:  # 逐行注释：根据条件判断是否进入该分支。
        score += 0.12  # 逐行注释：赋值或更新当前变量/字段。

    if "无抵押" in mortgage:  # 逐行注释：根据条件判断是否进入该分支。
        score += 0.25  # 逐行注释：赋值或更新当前变量/字段。
    elif mortgage:  # 逐行注释：根据条件判断是否进入该分支。
        score += 0.08  # 逐行注释：赋值或更新当前变量/字段。

    if any(token in selling_point for token in ("满五", "满二", "有证", "证满")):  # 逐行注释：根据条件判断是否进入该分支。
        score += 0.15  # 逐行注释：赋值或更新当前变量/字段。

    return min(score, 1.0)  # 逐行注释：返回当前逻辑的处理结果。


def _parse_listing_date(value):  # 逐行注释：声明函数或方法入口。
    """解析挂牌日期文本并转换为日期对象。"""
    from datetime import datetime  # 逐行注释：导入本行所需的模块或对象。

    if not value:  # 逐行注释：根据条件判断是否进入该分支。
        return None  # 逐行注释：返回当前逻辑的处理结果。
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):  # 逐行注释：遍历集合中的每一项并执行处理。
        try:  # 逐行注释：开始执行可能出现异常的逻辑。
            return datetime.strptime(value, fmt).date()  # 逐行注释：返回当前逻辑的处理结果。
        except ValueError:  # 逐行注释：捕获异常并执行错误处理。
            continue  # 逐行注释：跳过本轮循环剩余逻辑。
    return None  # 逐行注释：返回当前逻辑的处理结果。


def _rounded_average(values, digits=0):  # 逐行注释：声明函数或方法入口。
    """计算数值列表平均值并按指定位数取整。"""
    if not values:  # 逐行注释：根据条件判断是否进入该分支。
        return 0  # 逐行注释：返回当前逻辑的处理结果。
    value = sum(values) / len(values)  # 逐行注释：赋值或更新当前变量/字段。
    return round(value, digits) if digits else round(value)  # 逐行注释：返回当前逻辑的处理结果。


def _count_clean(counter, value):  # 逐行注释：声明函数或方法入口。
    """清理文本后写入计数器，忽略空值。"""
    text = (value or "").strip()  # 逐行注释：赋值或更新当前变量/字段。
    if text:  # 逐行注释：根据条件判断是否进入该分支。
        counter[text] += 1  # 逐行注释：赋值或更新当前变量/字段。


def _normalize_mortgage(value):  # 逐行注释：声明函数或方法入口。
    """将抵押信息文本归一化为前端可展示的分类。"""
    text = (value or "").strip()  # 逐行注释：赋值或更新当前变量/字段。
    if not text:  # 逐行注释：根据条件判断是否进入该分支。
        return None  # 逐行注释：返回当前逻辑的处理结果。
    if "无抵押" in text:  # 逐行注释：根据条件判断是否进入该分支。
        return "无抵押"  # 逐行注释：返回当前逻辑的处理结果。
    if "抵押" in text:  # 逐行注释：根据条件判断是否进入该分支。
        return "有抵押"  # 逐行注释：返回当前逻辑的处理结果。
    return text[:16]  # 逐行注释：返回当前逻辑的处理结果。


def _counter_items(counter, total=None, limit=8):  # 逐行注释：声明函数或方法入口。
    """把计数器转换为带数量和占比的列表。"""
    denominator = total or sum(counter.values())  # 逐行注释：赋值或更新当前变量/字段。
    if not denominator:  # 逐行注释：根据条件判断是否进入该分支。
        return []  # 逐行注释：返回当前逻辑的处理结果。
    return [  # 逐行注释：返回当前逻辑的处理结果。
        {  # 逐行注释：执行本行代码逻辑。
            "name": name,  # 逐行注释：设置当前数据项或参数。
            "count": int(count),  # 逐行注释：设置当前数据项或参数。
            "ratio": round(count / denominator * 100, 1),  # 逐行注释：设置当前数据项或参数。
        }  # 逐行注释：结束当前数据结构或调用块。
        for name, count in counter.most_common(limit)  # 逐行注释：遍历集合中的每一项并执行处理。
    ]  # 逐行注释：结束当前数据结构或调用块。


def _month_window(end_month, count):  # 逐行注释：声明函数或方法入口。
    """生成指定结束月份之前的连续月份窗口。"""
    return [_shift_months(end_month, offset) for offset in range(1 - count, 1)]  # 逐行注释：返回当前逻辑的处理结果。


def _shift_months(month, offset):  # 逐行注释：声明函数或方法入口。
    """按月偏移日期并返回月份起始日。"""
    month_index = month.year * 12 + month.month - 1 + offset  # 逐行注释：赋值或更新当前变量/字段。
    return date(month_index // 12, month_index % 12 + 1, 1)  # 逐行注释：返回当前逻辑的处理结果。
