"""Analysis services: aggregate statistics used by the dashboard & charts."""  # 保留字符串内容，作为说明文本或页面展示文案。
from collections import Counter, defaultdict  # 从 collections 导入 Counter, defaultdict，供本文件后续逻辑调用。
from datetime import date, timedelta  # 从 datetime 导入 date, timedelta，供本文件后续逻辑调用。
from math import log1p  # 从 math 导入 log1p，供本文件后续逻辑调用。
from statistics import median  # 从 statistics 导入 median，供本文件后续逻辑调用。

from sqlalchemy import func  # 从 sqlalchemy 导入 func，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import City, District, Property  # 从 models 导入 City, District, Property，供本文件后续逻辑调用。
from services.property_details import get_property_details  # 从 services.property_details 导入 get_property_details，供本文件后续逻辑调用。


def overview() -> dict:  # 定义 overview 函数，集中处理这一段业务逻辑。
    """Platform-wide headline numbers for the dashboard stat cards."""  # 保留字符串内容，作为说明文本或页面展示文案。
    # 总览卡片直接从房源表做聚合，返回的是全平台快照，不受城市/区域筛选影响。
    total = db.session.query(func.count(Property.id)).scalar() or 0  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    avg_unit = db.session.query(func.avg(Property.unit_price)).scalar() or 0  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    max_unit = db.session.query(func.max(Property.unit_price)).scalar() or 0  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    min_unit = db.session.query(func.min(Property.unit_price)).scalar() or 0  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    city_count = db.session.query(func.count(City.id)).scalar() or 0  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    return {  # 返回处理后的结果给调用方继续使用。
        "property_count": int(total),  # 保留字符串内容，作为说明文本或页面展示文案。
        "city_count": int(city_count),  # 保留字符串内容，作为说明文本或页面展示文案。
        "avg_unit_price": round(avg_unit),  # 保留字符串内容，作为说明文本或页面展示文案。
        "max_unit_price": round(max_unit),  # 保留字符串内容，作为说明文本或页面展示文案。
        "min_unit_price": round(min_unit),  # 保留字符串内容，作为说明文本或页面展示文案。
    }  # 结束当前多行数据结构或函数调用。


def district_ranking(city_id: int) -> list[dict]:  # 定义 district_ranking 函数，集中处理这一段业务逻辑。
    """Districts of a city ranked by average price/㎡ (drives the 3D map)."""  # 保留字符串内容，作为说明文本或页面展示文案。
    # 区域排行把 District 作为地图维度，把 Property 作为价格与数量来源，
    # 最终返回坐标、网格位置、均价和房源数，供 3D 地图和排行图共用。
    rows = (  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(  # 构造数据库查询，用于读取、筛选或聚合业务数据。
            District.id,  # 执行当前代码行对应的业务处理步骤。
            District.name,  # 执行当前代码行对应的业务处理步骤。
            District.lng,  # 执行当前代码行对应的业务处理步骤。
            District.lat,  # 执行当前代码行对应的业务处理步骤。
            District.grid_x,  # 执行当前代码行对应的业务处理步骤。
            District.grid_y,  # 执行当前代码行对应的业务处理步骤。
            func.avg(Property.unit_price).label("avg_unit_price"),  # 执行当前代码行对应的业务处理步骤。
            func.count(Property.id).label("property_count"),  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        .join(Property, Property.district_id == District.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .filter(District.city_id == city_id)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .group_by(District.id)  # 按指定业务维度分组，生成聚合统计结果。
        .order_by(func.avg(Property.unit_price).desc())  # 按指定字段或统计值排序，保证返回顺序符合页面展示需要。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    return [  # 返回处理后的结果给调用方继续使用。
        {  # 执行当前代码行对应的业务处理步骤。
            "id": r.id,  # 保留字符串内容，作为说明文本或页面展示文案。
            "name": r.name,  # 保留字符串内容，作为说明文本或页面展示文案。
            "lng": r.lng,  # 保留字符串内容，作为说明文本或页面展示文案。
            "lat": r.lat,  # 保留字符串内容，作为说明文本或页面展示文案。
            "grid_x": r.grid_x,  # 保留字符串内容，作为说明文本或页面展示文案。
            "grid_y": r.grid_y,  # 保留字符串内容，作为说明文本或页面展示文案。
            "avg_unit_price": round(r.avg_unit_price or 0),  # 保留字符串内容，作为说明文本或页面展示文案。
            "property_count": int(r.property_count),  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
        for r in rows  # 遍历当前数据集合，逐项完成处理。
    ]  # 结束当前多行数据结构或函数调用。


def price_distribution(city_id: int, bucket_size: int = 10000) -> list[dict]:  # 定义 price_distribution 函数，集中处理这一段业务逻辑。
    """Histogram of unit prices for a city, bucketed by ``bucket_size`` 元/㎡."""  # 保留字符串内容，作为说明文本或页面展示文案。
    # 价格分布只取有效单价，并按固定桶宽落位到 lower-bound，便于前端绘制直方图。
    prices = (  # 设置 prices 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(Property.unit_price)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .filter(District.city_id == city_id, Property.unit_price.isnot(None))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    buckets: dict[int, int] = {}  # 设置 buckets: dict[int, int 的值，供后续业务判断、查询或响应组装使用。
    for (price,) in prices:  # 遍历当前数据集合，逐项完成处理。
        key = int(price // bucket_size) * bucket_size  # 设置 key 的值，供后续业务判断、查询或响应组装使用。
        buckets[key] = buckets.get(key, 0) + 1  # 设置 buckets[key 的值，供后续业务判断、查询或响应组装使用。
    return [  # 返回处理后的结果给调用方继续使用。
        {  # 执行当前代码行对应的业务处理步骤。
            "range": f"{lo // 10000}-{(lo + bucket_size) // 10000}万",  # 保留字符串内容，作为说明文本或页面展示文案。
            "lower": lo,  # 保留字符串内容，作为说明文本或页面展示文案。
            "count": buckets[lo],  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
        for lo in sorted(buckets)  # 遍历当前数据集合，逐项完成处理。
    ]  # 结束当前多行数据结构或函数调用。


def price_trend(district_id: int) -> list[dict]:  # 定义 price_trend 函数，集中处理这一段业务逻辑。
    """Monthly average-price series for a district."""  # 保留字符串内容，作为说明文本或页面展示文案。
    from models import PriceHistory  # 从 models 导入 PriceHistory，供本文件后续逻辑调用。

    rows = (  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(PriceHistory)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .filter(PriceHistory.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .order_by(PriceHistory.month.asc())  # 按指定字段或统计值排序，保证返回顺序符合页面展示需要。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    return [r.to_dict() for r in rows]  # 返回处理后的结果给调用方继续使用。


def listing_profile(district_id: int) -> dict:  # 定义 listing_profile 函数，集中处理这一段业务逻辑。
    """Current listing snapshot and transaction-attribute profile for a district."""  # 保留字符串内容，作为说明文本或页面展示文案。
    # 挂牌画像先取区域内房源的基础价格/面积，再通过 source_url 关联交易扩展字段，
    # 将挂牌日期、产权、抵押和卖点标签汇总成前端可视化结构。
    rows = (  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(  # 构造数据库查询，用于读取、筛选或聚合业务数据。
            Property.unit_price,  # 执行当前代码行对应的业务处理步骤。
            Property.total_price,  # 执行当前代码行对应的业务处理步骤。
            Property.area,  # 执行当前代码行对应的业务处理步骤。
            Property.source_url,  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        .filter(Property.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    prices = [float(r.unit_price) for r in rows if r.unit_price]  # 设置 prices 的值，供后续业务判断、查询或响应组装使用。
    totals = [float(r.total_price) for r in rows if r.total_price]  # 设置 totals 的值，供后续业务判断、查询或响应组装使用。
    areas = [float(r.area) for r in rows if r.area]  # 设置 areas 的值，供后续业务判断、查询或响应组装使用。

    listing_dates = []  # 设置 listing_dates 的值，供后续业务判断、查询或响应组装使用。
    monthly_counts = Counter()  # 设置 monthly_counts 的值，供后续业务判断、查询或响应组装使用。
    monthly_prices = defaultdict(list)  # 设置 monthly_prices 的值，供后续业务判断、查询或响应组装使用。
    ownership_counter = Counter()  # 设置 ownership_counter 的值，供后续业务判断、查询或响应组装使用。
    right_counter = Counter()  # 设置 right_counter 的值，供后续业务判断、查询或响应组装使用。
    mortgage_counter = Counter()  # 设置 mortgage_counter 的值，供后续业务判断、查询或响应组装使用。
    tax_tags = Counter()  # 设置 tax_tags 的值，供后续业务判断、查询或响应组装使用。
    detail_count = 0  # 设置 detail_count 的值，供后续业务判断、查询或响应组装使用。

    for row in rows:  # 遍历当前数据集合，逐项完成处理。
        detail = get_property_details(row.source_url)  # 设置 detail 的值，供后续业务判断、查询或响应组装使用。
        if not detail:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            continue  # 跳过当前循环项，继续处理下一项。
        detail_count += 1  # 设置 detail_count + 的值，供后续业务判断、查询或响应组装使用。

        # 挂牌日期用于构建 24 个月挂牌量和月均价走势；无法解析的日期不参与时间序列。
        listing_date = _parse_listing_date(detail.get("listing_date"))  # 设置 listing_date 的值，供后续业务判断、查询或响应组装使用。
        if listing_date:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            listing_dates.append(listing_date)  # 执行当前代码行对应的业务处理步骤。
            month = listing_date.strftime("%Y-%m")  # 设置 month 的值，供后续业务判断、查询或响应组装使用。
            monthly_counts[month] += 1  # 设置 monthly_counts[month] + 的值，供后续业务判断、查询或响应组装使用。
            if row.unit_price:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                monthly_prices[month].append(float(row.unit_price))  # 执行当前代码行对应的业务处理步骤。

        _count_clean(ownership_counter, detail.get("ownership_type"))  # 执行当前代码行对应的业务处理步骤。
        _count_clean(right_counter, detail.get("property_right"))  # 执行当前代码行对应的业务处理步骤。

        # 交易属性统一清洗后再计数，避免“暂无数据/空字符串”等占位值污染分布。
        mortgage = _normalize_mortgage(detail.get("mortgage"))  # 设置 mortgage 的值，供后续业务判断、查询或响应组装使用。
        if mortgage:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            mortgage_counter[mortgage] += 1  # 设置 mortgage_counter[mortgage] + 的值，供后续业务判断、查询或响应组装使用。

        selling_point = detail.get("selling_point") or ""  # 设置 selling_point 的值，供后续业务判断、查询或响应组装使用。
        if "满五" in selling_point:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            tax_tags["满五"] += 1  # 设置 tax_tags["满五"] + 的值，供后续业务判断、查询或响应组装使用。
        if any(token in selling_point for token in ("满二", "满两", "证满二", "证满两")):  # 判断当前条件是否成立，决定是否进入对应处理分支。
            tax_tags["满二"] += 1  # 设置 tax_tags["满二"] + 的值，供后续业务判断、查询或响应组装使用。
        if any(token in selling_point for token in ("有证", "房产证", "产权证")):  # 判断当前条件是否成立，决定是否进入对应处理分支。
            tax_tags["有证"] += 1  # 设置 tax_tags["有证"] + 的值，供后续业务判断、查询或响应组装使用。

    latest_month = None  # 设置 latest_month 的值，供后续业务判断、查询或响应组装使用。
    monthly = []  # 设置 monthly 的值，供后续业务判断、查询或响应组装使用。
    if listing_dates:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        latest = max(listing_dates)  # 设置 latest 的值，供后续业务判断、查询或响应组装使用。
        latest_month = date(latest.year, latest.month, 1)  # 设置 latest_month 的值，供后续业务判断、查询或响应组装使用。
        # 以样本中最新挂牌月为右边界回看 24 个月，保证历史数据不完整时仍能对齐展示。
        for month_date in _month_window(latest_month, 24):  # 遍历当前数据集合，逐项完成处理。
            month = month_date.strftime("%Y-%m")  # 设置 month 的值，供后续业务判断、查询或响应组装使用。
            month_prices = monthly_prices.get(month, [])  # 设置 month_prices 的值，供后续业务判断、查询或响应组装使用。
            monthly.append(  # 执行当前代码行对应的业务处理步骤。
                {  # 执行当前代码行对应的业务处理步骤。
                    "month": month,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "count": int(monthly_counts.get(month, 0)),  # 保留字符串内容，作为说明文本或页面展示文案。
                    "avg_unit_price": (  # 保留字符串内容，作为说明文本或页面展示文案。
                        round(sum(month_prices) / len(month_prices))  # 执行当前代码行对应的业务处理步骤。
                        if month_prices  # 判断当前条件是否成立，决定是否进入对应处理分支。
                        else None  # 执行当前代码行对应的业务处理步骤。
                    ),  # 结束当前多行数据结构或函数调用。
                }  # 结束当前多行数据结构或函数调用。
            )  # 结束当前多行数据结构或函数调用。

    recent_ratio = 0  # 设置 recent_ratio 的值，供后续业务判断、查询或响应组装使用。
    if listing_dates:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        latest = max(listing_dates)  # 设置 latest 的值，供后续业务判断、查询或响应组装使用。
        recent_cutoff = latest - timedelta(days=365)  # 设置 recent_cutoff 的值，供后续业务判断、查询或响应组装使用。
        recent_ratio = sum(1 for item in listing_dates if item >= recent_cutoff) / len(  # 设置 recent_ratio 的值，供后续业务判断、查询或响应组装使用。
            listing_dates  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。

    return {  # 返回处理后的结果给调用方继续使用。
        "district_id": district_id,  # 保留字符串内容，作为说明文本或页面展示文案。
        "property_count": len(rows),  # 保留字符串内容，作为说明文本或页面展示文案。
        "detail_count": detail_count,  # 保留字符串内容，作为说明文本或页面展示文案。
        "date_count": len(listing_dates),  # 保留字符串内容，作为说明文本或页面展示文案。
        "avg_unit_price": _rounded_average(prices),  # 保留字符串内容，作为说明文本或页面展示文案。
        "median_unit_price": round(median(prices)) if prices else 0,  # 保留字符串内容，作为说明文本或页面展示文案。
        "avg_total_price": _rounded_average(totals, digits=1),  # 设置 "avg_total_price": _rounded_average(totals, digits 的值，供后续业务判断、查询或响应组装使用。
        "avg_area": _rounded_average(areas, digits=1),  # 设置 "avg_area": _rounded_average(areas, digits 的值，供后续业务判断、查询或响应组装使用。
        "as_of_month": latest_month.strftime("%Y-%m") if latest_month else None,  # 保留字符串内容，作为说明文本或页面展示文案。
        "recent_listing_ratio": round(recent_ratio * 100, 1),  # 保留字符串内容，作为说明文本或页面展示文案。
        "monthly_listings": monthly,  # 保留字符串内容，作为说明文本或页面展示文案。
        "ownership_distribution": _counter_items(ownership_counter),  # 保留字符串内容，作为说明文本或页面展示文案。
        "property_right_distribution": _counter_items(right_counter),  # 保留字符串内容，作为说明文本或页面展示文案。
        "mortgage_distribution": _counter_items(mortgage_counter),  # 保留字符串内容，作为说明文本或页面展示文案。
        "tax_tags": _counter_items(tax_tags, total=detail_count),  # 设置 "tax_tags": _counter_items(tax_tags, total 的值，供后续业务判断、查询或响应组装使用。
    }  # 结束当前多行数据结构或函数调用。


def investment_ranking(city_id: int) -> list[dict]:  # 定义 investment_ranking 函数，集中处理这一段业务逻辑。
    """Rank districts by a potential score based on the current data snapshot.

    The current real dataset has listing dates and transaction attributes, but
    no reliable month-by-month historical growth. The score therefore combines:
      - 价格洼地 value_score       35%
      - 市场热度 heat_score        25%
      - 周边配套 facility_score    20%
      - 交易安全 safety_score      10%
      - 挂牌新鲜度 freshness_score 10%
    """
    from models import Facility  # 从 models 导入 Facility，供本文件后续逻辑调用。

    # 先以行政区为粒度聚合房源均价和挂牌量，这是投资评分的价格/热度基础样本。
    rows = [  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        {  # 执行当前代码行对应的业务处理步骤。
            "id": r.id,  # 保留字符串内容，作为说明文本或页面展示文案。
            "name": r.name,  # 保留字符串内容，作为说明文本或页面展示文案。
            "avg_unit_price": round(r.avg_unit_price or 0),  # 保留字符串内容，作为说明文本或页面展示文案。
            "property_count": int(r.property_count or 0),  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
        for r in (  # 遍历当前数据集合，逐项完成处理。
            db.session.query(  # 构造数据库查询，用于读取、筛选或聚合业务数据。
                District.id,  # 执行当前代码行对应的业务处理步骤。
                District.name,  # 执行当前代码行对应的业务处理步骤。
                func.avg(Property.unit_price).label("avg_unit_price"),  # 执行当前代码行对应的业务处理步骤。
                func.count(Property.id).label("property_count"),  # 执行当前代码行对应的业务处理步骤。
            )  # 结束当前多行数据结构或函数调用。
            .join(Property, Property.district_id == District.id)  # 把关联表纳入查询，获取跨表维度的数据。
            .filter(District.city_id == city_id, Property.unit_price.isnot(None))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
            .group_by(District.id)  # 按指定业务维度分组，生成聚合统计结果。
            .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
        )  # 结束当前多行数据结构或函数调用。
        if r.avg_unit_price  # 判断当前条件是否成立，决定是否进入对应处理分支。
    ]  # 结束当前多行数据结构或函数调用。
    if not rows:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return []  # 返回处理后的结果给调用方继续使用。

    row_by_id = {r["id"]: r for r in rows}  # 设置 row_by_id 的值，供后续业务判断、查询或响应组装使用。
    prices = [r["avg_unit_price"] for r in rows]  # 设置 prices 的值，供后续业务判断、查询或响应组装使用。
    counts = [r["property_count"] for r in rows]  # 设置 counts 的值，供后续业务判断、查询或响应组装使用。
    p_lo, p_hi, p_mid = min(prices), max(prices), median(prices)  # 设置 p_lo, p_hi, p_mid 的值，供后续业务判断、查询或响应组装使用。
    c_lo, c_hi = min(counts), max(counts)  # 设置 c_lo, c_hi 的值，供后续业务判断、查询或响应组装使用。

    # 配套设施按数量和类别覆盖度两个维度统计：数量代表密度，类别数代表生活便利性的广度。
    facility_stats = {  # 设置 facility_stats 的值，供后续业务判断、查询或响应组装使用。
        district_id: {"facility_count": int(count), "facility_category_count": int(categories)}  # 执行当前代码行对应的业务处理步骤。
        for district_id, count, categories in (  # 遍历当前数据集合，逐项完成处理。
            db.session.query(  # 构造数据库查询，用于读取、筛选或聚合业务数据。
                Facility.district_id,  # 执行当前代码行对应的业务处理步骤。
                func.count(Facility.id),  # 执行当前代码行对应的业务处理步骤。
                func.count(func.distinct(Facility.category)),  # 执行当前代码行对应的业务处理步骤。
            )  # 结束当前多行数据结构或函数调用。
            .filter(Facility.district_id.in_(row_by_id))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
            .group_by(Facility.district_id)  # 按指定业务维度分组，生成聚合统计结果。
            .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
        )  # 结束当前多行数据结构或函数调用。
    }  # 结束当前多行数据结构或函数调用。

    # 交易安全和挂牌新鲜度来自 PropertyTransaction 扩展信息，通过 source_url 回连房源。
    transaction_stats = _transaction_scores(city_id)  # 设置 transaction_stats 的值，供后续业务判断、查询或响应组装使用。
    max_facilities = max(  # 设置 max_facilities 的值，供后续业务判断、查询或响应组装使用。
        [s["facility_count"] for s in facility_stats.values()] or [0]  # 执行当前代码行对应的业务处理步骤。
    )  # 结束当前多行数据结构或函数调用。

    def _norm(value, lo, hi):  # 定义 _norm 函数，集中处理这一段业务逻辑。
        """将指标值按上下界归一化到 0 到 1 区间。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return (value - lo) / (hi - lo) if hi > lo else 0.5  # 返回处理后的结果给调用方继续使用。

    for r in rows:  # 遍历当前数据集合，逐项完成处理。
        # Low prices receive a higher value score. Areas above the city median
        # still receive a small score if they are not the most expensive.
        if r["avg_unit_price"] <= p_mid:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            value_score = _norm(p_mid - r["avg_unit_price"], 0, p_mid - p_lo)  # 设置 value_score 的值，供后续业务判断、查询或响应组装使用。
        else:  # 处理前面条件都未命中的兜底分支。
            value_score = 0.35 * (1 - _norm(r["avg_unit_price"], p_mid, p_hi))  # 设置 value_score 的值，供后续业务判断、查询或响应组装使用。

        # 使用 log1p 压缩挂牌量，避免超大商圈仅凭数量把热度分拉满。
        heat_score = _norm(log1p(r["property_count"]), log1p(c_lo), log1p(c_hi))  # 设置 heat_score 的值，供后续业务判断、查询或响应组装使用。
        fac = facility_stats.get(r["id"], {"facility_count": 0, "facility_category_count": 0})  # 设置 fac 的值，供后续业务判断、查询或响应组装使用。
        facility_count_score = (  # 设置 facility_count_score 的值，供后续业务判断、查询或响应组装使用。
            fac["facility_count"] / max_facilities if max_facilities else 0  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        facility_cover_score = min(fac["facility_category_count"], 5) / 5  # 设置 facility_cover_score 的值，供后续业务判断、查询或响应组装使用。
        facility_score = 0.55 * facility_count_score + 0.45 * facility_cover_score  # 设置 facility_score 的值，供后续业务判断、查询或响应组装使用。

        transaction = transaction_stats.get(r["id"], {})  # 设置 transaction 的值，供后续业务判断、查询或响应组装使用。
        safety_score = transaction.get("safety_score", 0.5)  # 设置 safety_score 的值，供后续业务判断、查询或响应组装使用。
        freshness_score = transaction.get("freshness_score", 0.5)  # 设置 freshness_score 的值，供后续业务判断、查询或响应组装使用。
        heat_index = 0.55 * heat_score + 0.45 * facility_score  # 设置 heat_index 的值，供后续业务判断、查询或响应组装使用。

        # 五项指标统一转成 0-1 后再按权重合成，返回给前端时再换算成百分制。
        score = (  # 设置 score 的值，供后续业务判断、查询或响应组装使用。
            0.35 * value_score  # 执行当前代码行对应的业务处理步骤。
            + 0.25 * heat_score  # 执行当前代码行对应的业务处理步骤。
            + 0.20 * facility_score  # 执行当前代码行对应的业务处理步骤。
            + 0.10 * safety_score  # 执行当前代码行对应的业务处理步骤。
            + 0.10 * freshness_score  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        r.update(  # 执行当前代码行对应的业务处理步骤。
            {  # 执行当前代码行对应的业务处理步骤。
                "facility_count": fac["facility_count"],  # 保留字符串内容，作为说明文本或页面展示文案。
                "facility_category_count": fac["facility_category_count"],  # 保留字符串内容，作为说明文本或页面展示文案。
                "heat_index": round(heat_index * 100),  # 保留字符串内容，作为说明文本或页面展示文案。
                "value_score": round(value_score * 100),  # 保留字符串内容，作为说明文本或页面展示文案。
                "heat_score": round(heat_score * 100),  # 保留字符串内容，作为说明文本或页面展示文案。
                "facility_score": round(facility_score * 100),  # 保留字符串内容，作为说明文本或页面展示文案。
                "safety_score": round(safety_score * 100),  # 保留字符串内容，作为说明文本或页面展示文案。
                "freshness_score": round(freshness_score * 100),  # 保留字符串内容，作为说明文本或页面展示文案。
                "recent_listing_ratio": round(  # 保留字符串内容，作为说明文本或页面展示文案。
                    transaction.get("recent_listing_ratio", 0) * 100  # 执行当前代码行对应的业务处理步骤。
                ),  # 结束当前多行数据结构或函数调用。
                "score": round(score * 100),  # 保留字符串内容，作为说明文本或页面展示文案。
            }  # 结束当前多行数据结构或函数调用。
        )  # 结束当前多行数据结构或函数调用。

    rows.sort(key=lambda x: x["score"], reverse=True)  # 设置 rows.sort(key 的值，供后续业务判断、查询或响应组装使用。
    return rows  # 返回处理后的结果给调用方继续使用。


def _transaction_scores(city_id: int) -> dict[int, dict]:  # 定义 _transaction_scores 函数，集中处理这一段业务逻辑。
    """Aggregate transaction safety and listing freshness by district."""  # 保留字符串内容，作为说明文本或页面展示文案。
    parsed = []  # 设置 parsed 的值，供后续业务判断、查询或响应组装使用。
    safety_sum = defaultdict(float)  # 设置 safety_sum 的值，供后续业务判断、查询或响应组装使用。
    safety_count = defaultdict(int)  # 设置 safety_count 的值，供后续业务判断、查询或响应组装使用。
    listing_dates = defaultdict(list)  # 设置 listing_dates 的值，供后续业务判断、查询或响应组装使用。

    # 这里只读取 district_id 和 source_url，再按需加载详情，避免把房源主体大字段全部取出。
    rows = (  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(Property.district_id, Property.source_url)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .filter(District.city_id == city_id, Property.source_url.isnot(None))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    for district_id, source_url in rows:  # 遍历当前数据集合，逐项完成处理。
        detail = get_property_details(source_url)  # 设置 detail 的值，供后续业务判断、查询或响应组装使用。
        if not detail:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            continue  # 跳过当前循环项，继续处理下一项。

        safety_sum[district_id] += _safety_score(detail)  # 设置 safety_sum[district_id] + 的值，供后续业务判断、查询或响应组装使用。
        safety_count[district_id] += 1  # 设置 safety_count[district_id] + 的值，供后续业务判断、查询或响应组装使用。

        listing_date = _parse_listing_date(detail.get("listing_date"))  # 设置 listing_date 的值，供后续业务判断、查询或响应组装使用。
        if listing_date:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            listing_dates[district_id].append(listing_date)  # 执行当前代码行对应的业务处理步骤。
            parsed.append(listing_date)  # 执行当前代码行对应的业务处理步骤。

    # “近期挂牌”以当前样本里最新挂牌日为参照，适配离线采集数据的时间截面。
    latest = max(parsed) if parsed else None  # 设置 latest 的值，供后续业务判断、查询或响应组装使用。
    recent_cutoff = latest - timedelta(days=365) if latest else None  # 设置 recent_cutoff 的值，供后续业务判断、查询或响应组装使用。
    result = {}  # 设置 result 的值，供后续业务判断、查询或响应组装使用。
    district_ids = set(safety_count) | set(listing_dates)  # 设置 district_ids 的值，供后续业务判断、查询或响应组装使用。
    for district_id in district_ids:  # 遍历当前数据集合，逐项完成处理。
        dates = listing_dates.get(district_id, [])  # 设置 dates 的值，供后续业务判断、查询或响应组装使用。
        recent = (  # 设置 recent 的值，供后续业务判断、查询或响应组装使用。
            sum(1 for date in dates if date >= recent_cutoff) / len(dates)  # 设置 sum(1 for date in dates if date > 的值，供后续业务判断、查询或响应组装使用。
            if dates and recent_cutoff  # 判断当前条件是否成立，决定是否进入对应处理分支。
            else 0.5  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        result[district_id] = {  # 设置 result[district_id 的值，供后续业务判断、查询或响应组装使用。
            "safety_score": (  # 保留字符串内容，作为说明文本或页面展示文案。
                safety_sum[district_id] / safety_count[district_id]  # 执行当前代码行对应的业务处理步骤。
                if safety_count[district_id]  # 判断当前条件是否成立，决定是否进入对应处理分支。
                else 0.5  # 执行当前代码行对应的业务处理步骤。
            ),  # 结束当前多行数据结构或函数调用。
            "freshness_score": recent,  # 保留字符串内容，作为说明文本或页面展示文案。
            "recent_listing_ratio": recent,  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
    return result  # 返回处理后的结果给调用方继续使用。


def _safety_score(detail: dict) -> float:  # 定义 _safety_score 函数，集中处理这一段业务逻辑。
    """根据产权、抵押和税费标签计算交易安全评分。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    score = 0.0  # 设置 score 的值，供后续业务判断、查询或响应组装使用。
    ownership = detail.get("ownership_type") or ""  # 设置 ownership 的值，供后续业务判断、查询或响应组装使用。
    right = detail.get("property_right") or ""  # 设置 right 的值，供后续业务判断、查询或响应组装使用。
    mortgage = detail.get("mortgage") or ""  # 设置 mortgage 的值，供后续业务判断、查询或响应组装使用。
    selling_point = detail.get("selling_point") or ""  # 设置 selling_point 的值，供后续业务判断、查询或响应组装使用。

    if "商品房" in ownership:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        score += 0.35  # 设置 score + 的值，供后续业务判断、查询或响应组装使用。
    elif "已购公房" in ownership:  # 在前一个条件不成立时，继续判断这个补充分支。
        score += 0.25  # 设置 score + 的值，供后续业务判断、查询或响应组装使用。
    elif ownership:  # 在前一个条件不成立时，继续判断这个补充分支。
        score += 0.15  # 设置 score + 的值，供后续业务判断、查询或响应组装使用。

    if "非共有" in right:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        score += 0.25  # 设置 score + 的值，供后续业务判断、查询或响应组装使用。
    elif "共有" in right:  # 在前一个条件不成立时，继续判断这个补充分支。
        score += 0.12  # 设置 score + 的值，供后续业务判断、查询或响应组装使用。

    if "无抵押" in mortgage:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        score += 0.25  # 设置 score + 的值，供后续业务判断、查询或响应组装使用。
    elif mortgage:  # 在前一个条件不成立时，继续判断这个补充分支。
        score += 0.08  # 设置 score + 的值，供后续业务判断、查询或响应组装使用。

    if any(token in selling_point for token in ("满五", "满二", "有证", "证满")):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        score += 0.15  # 设置 score + 的值，供后续业务判断、查询或响应组装使用。

    return min(score, 1.0)  # 返回处理后的结果给调用方继续使用。


def _parse_listing_date(value):  # 定义 _parse_listing_date 函数，集中处理这一段业务逻辑。
    """解析挂牌日期文本并转换为日期对象。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    from datetime import datetime  # 从 datetime 导入 datetime，供本文件后续逻辑调用。

    if not value:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return None  # 返回处理后的结果给调用方继续使用。
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):  # 遍历当前数据集合，逐项完成处理。
        try:  # 开始执行可能抛出异常的代码块。
            return datetime.strptime(value, fmt).date()  # 返回处理后的结果给调用方继续使用。
        except ValueError:  # 捕获指定异常，并转入可控的错误处理流程。
            continue  # 跳过当前循环项，继续处理下一项。
    return None  # 返回处理后的结果给调用方继续使用。


def _rounded_average(values, digits=0):  # 定义 _rounded_average 函数，集中处理这一段业务逻辑。
    """计算数值列表平均值并按指定位数取整。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if not values:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return 0  # 返回处理后的结果给调用方继续使用。
    value = sum(values) / len(values)  # 设置 value 的值，供后续业务判断、查询或响应组装使用。
    return round(value, digits) if digits else round(value)  # 返回处理后的结果给调用方继续使用。


def _count_clean(counter, value):  # 定义 _count_clean 函数，集中处理这一段业务逻辑。
    """清理文本后写入计数器，忽略空值。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    text = (value or "").strip()  # 设置 text 的值，供后续业务判断、查询或响应组装使用。
    if text:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        counter[text] += 1  # 设置 counter[text] + 的值，供后续业务判断、查询或响应组装使用。


def _normalize_mortgage(value):  # 定义 _normalize_mortgage 函数，集中处理这一段业务逻辑。
    """将抵押信息文本归一化为前端可展示的分类。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    text = (value or "").strip()  # 设置 text 的值，供后续业务判断、查询或响应组装使用。
    if not text:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return None  # 返回处理后的结果给调用方继续使用。
    if "无抵押" in text:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return "无抵押"  # 返回处理后的结果给调用方继续使用。
    if "抵押" in text:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return "有抵押"  # 返回处理后的结果给调用方继续使用。
    return text[:16]  # 返回处理后的结果给调用方继续使用。


def _counter_items(counter, total=None, limit=8):  # 定义 _counter_items 函数，集中处理这一段业务逻辑。
    """把计数器转换为带数量和占比的列表。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    denominator = total or sum(counter.values())  # 设置 denominator 的值，供后续业务判断、查询或响应组装使用。
    if not denominator:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return []  # 返回处理后的结果给调用方继续使用。
    return [  # 返回处理后的结果给调用方继续使用。
        {  # 执行当前代码行对应的业务处理步骤。
            "name": name,  # 保留字符串内容，作为说明文本或页面展示文案。
            "count": int(count),  # 保留字符串内容，作为说明文本或页面展示文案。
            "ratio": round(count / denominator * 100, 1),  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
        for name, count in counter.most_common(limit)  # 遍历当前数据集合，逐项完成处理。
    ]  # 结束当前多行数据结构或函数调用。


def _month_window(end_month, count):  # 定义 _month_window 函数，集中处理这一段业务逻辑。
    """生成指定结束月份之前的连续月份窗口。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return [_shift_months(end_month, offset) for offset in range(1 - count, 1)]  # 返回处理后的结果给调用方继续使用。


def _shift_months(month, offset):  # 定义 _shift_months 函数，集中处理这一段业务逻辑。
    """按月偏移日期并返回月份起始日。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    month_index = month.year * 12 + month.month - 1 + offset  # 设置 month_index 的值，供后续业务判断、查询或响应组装使用。
    return date(month_index // 12, month_index % 12 + 1, 1)  # 返回处理后的结果给调用方继续使用。
