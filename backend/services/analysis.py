"""Analysis services: aggregate statistics used by the dashboard & charts."""
from collections import Counter, defaultdict  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from datetime import date, timedelta  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from math import log1p  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from statistics import median  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from sqlalchemy import func  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import City, District, Property  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from services.property_details import get_property_details  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


def overview() -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Platform-wide headline numbers for the dashboard stat cards."""
    # 总览卡片直接从房源表做聚合，返回的是全平台快照，不受城市/区域筛选影响。
    total = db.session.query(func.count(Property.id)).scalar() or 0  # 创建总数统计的数据库查询对象，用于继续叠加过滤和聚合条件。
    avg_unit = db.session.query(func.avg(Property.unit_price)).scalar() or 0  # 创建avg_unit中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
    max_unit = db.session.query(func.max(Property.unit_price)).scalar() or 0  # 创建max_unit中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
    min_unit = db.session.query(func.min(Property.unit_price)).scalar() or 0  # 创建min_unit中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
    city_count = db.session.query(func.count(City.id)).scalar() or 0  # 创建city_count中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
    return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        "property_count": int(total),  # 把property_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "city_count": int(city_count),  # 把city_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "avg_unit_price": round(avg_unit),  # 把avg_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "max_unit_price": round(max_unit),  # 把max_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "min_unit_price": round(min_unit),  # 把min_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def district_ranking(city_id: int) -> list[dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Districts of a city ranked by average price/㎡ (drives the 3D map)."""
    # 区域排行把 District 作为地图维度，把 Property 作为价格与数量来源，
    # 最终返回坐标、网格位置、均价和房源数，供 3D 地图和排行图共用。
    rows = (  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
        db.session.query(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            District.id,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            District.name,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            District.lng,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            District.lat,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            District.grid_x,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            District.grid_y,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.avg(Property.unit_price).label("avg_unit_price"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.count(Property.id).label("property_count"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        .join(Property, Property.district_id == District.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .filter(District.city_id == city_id)  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .group_by(District.id)  # 按业务维度分组聚合，生成排行榜或统计指标。
        .order_by(func.avg(Property.unit_price).desc())  # 按统计值或业务字段排序，保证返回数据符合展示顺序。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return [  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "id": r.id,  # 把id字段写入响应数据，供前端页面、图表或后续接口读取。
            "name": r.name,  # 把name字段写入响应数据，供前端页面、图表或后续接口读取。
            "lng": r.lng,  # 把lng字段写入响应数据，供前端页面、图表或后续接口读取。
            "lat": r.lat,  # 把lat字段写入响应数据，供前端页面、图表或后续接口读取。
            "grid_x": r.grid_x,  # 把grid_x字段写入响应数据，供前端页面、图表或后续接口读取。
            "grid_y": r.grid_y,  # 把grid_y字段写入响应数据，供前端页面、图表或后续接口读取。
            "avg_unit_price": round(r.avg_unit_price or 0),  # 把avg_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
            "property_count": int(r.property_count),  # 把property_count字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        for r in rows  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def price_distribution(city_id: int, bucket_size: int = 10000) -> list[dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Histogram of unit prices for a city, bucketed by ``bucket_size`` 元/㎡."""
    # 价格分布只取有效单价，并按固定桶宽落位到 lower-bound，便于前端绘制直方图。
    prices = (  # 计算或更新prices中间数据，作为后续业务判断、统计或响应组装的输入。
        db.session.query(Property.unit_price)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .filter(District.city_id == city_id, Property.unit_price.isnot(None))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    buckets: dict[int, int] = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    for (price,) in prices:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        key = int(price // bucket_size) * bucket_size  # 计算或更新key中间数据，作为后续业务判断、统计或响应组装的输入。
        buckets[key] = buckets.get(key, 0) + 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return [  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "range": f"{lo // 10000}-{(lo + bucket_size) // 10000}万",  # 把range字段写入响应数据，供前端页面、图表或后续接口读取。
            "lower": lo,  # 把lower字段写入响应数据，供前端页面、图表或后续接口读取。
            "count": buckets[lo],  # 把count字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        for lo in sorted(buckets)  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def price_trend(district_id: int) -> list[dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Monthly average-price series for a district."""
    from models import PriceHistory  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

    rows = (  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
        db.session.query(PriceHistory)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .filter(PriceHistory.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .order_by(PriceHistory.month.asc())  # 按统计值或业务字段排序，保证返回数据符合展示顺序。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return [r.to_dict() for r in rows]  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def listing_profile(district_id: int) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Current listing snapshot and transaction-attribute profile for a district."""
    # 挂牌画像先取区域内房源的基础价格/面积，再通过 source_url 关联交易扩展字段，
    # 将挂牌日期、产权、抵押和卖点标签汇总成前端可视化结构。
    rows = (  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
        db.session.query(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            Property.unit_price,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            Property.total_price,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            Property.area,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            Property.source_url,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        .filter(Property.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    prices = [float(r.unit_price) for r in rows if r.unit_price]  # 初始化prices中间数据列表，用于收集清洗后的多条业务数据。
    totals = [float(r.total_price) for r in rows if r.total_price]  # 初始化totals中间数据列表，用于收集清洗后的多条业务数据。
    areas = [float(r.area) for r in rows if r.area]  # 初始化areas中间数据列表，用于收集清洗后的多条业务数据。

    listing_dates = []  # 初始化listing_dates中间数据列表，用于收集清洗后的多条业务数据。
    monthly_counts = Counter()  # 计算或更新monthly_counts中间数据，作为后续业务判断、统计或响应组装的输入。
    monthly_prices = defaultdict(list)  # 计算或更新monthly_prices中间数据，作为后续业务判断、统计或响应组装的输入。
    ownership_counter = Counter()  # 计算或更新ownership_counter中间数据，作为后续业务判断、统计或响应组装的输入。
    right_counter = Counter()  # 计算或更新right_counter中间数据，作为后续业务判断、统计或响应组装的输入。
    mortgage_counter = Counter()  # 计算或更新mortgage_counter中间数据，作为后续业务判断、统计或响应组装的输入。
    tax_tags = Counter()  # 计算或更新tax_tags中间数据，作为后续业务判断、统计或响应组装的输入。
    detail_count = 0  # 计算或更新detail_count中间数据，作为后续业务判断、统计或响应组装的输入。

    for row in rows:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        detail = get_property_details(row.source_url)  # 从请求或外部输入提取detail中间数据，用于后续校验、查询或写入。
        if not detail:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        detail_count += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        # 挂牌日期用于构建 24 个月挂牌量和月均价走势；无法解析的日期不参与时间序列。
        listing_date = _parse_listing_date(detail.get("listing_date"))  # 计算或更新listing_date中间数据，作为后续业务判断、统计或响应组装的输入。
        if listing_date:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            listing_dates.append(listing_date)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            month = listing_date.strftime("%Y-%m")  # 计算或更新month中间数据，作为后续业务判断、统计或响应组装的输入。
            monthly_counts[month] += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            if row.unit_price:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                monthly_prices[month].append(float(row.unit_price))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        _count_clean(ownership_counter, detail.get("ownership_type"))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        _count_clean(right_counter, detail.get("property_right"))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        # 交易属性统一清洗后再计数，避免“暂无数据/空字符串”等占位值污染分布。
        mortgage = _normalize_mortgage(detail.get("mortgage"))  # 计算或更新mortgage中间数据，作为后续业务判断、统计或响应组装的输入。
        if mortgage:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            mortgage_counter[mortgage] += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        selling_point = detail.get("selling_point") or ""  # 计算或更新selling_point中间数据，作为后续业务判断、统计或响应组装的输入。
        if "满五" in selling_point:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            tax_tags["满五"] += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        if any(token in selling_point for token in ("满二", "满两", "证满二", "证满两")):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            tax_tags["满二"] += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        if any(token in selling_point for token in ("有证", "房产证", "产权证")):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            tax_tags["有证"] += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    latest_month = None  # 计算或更新latest_month中间数据，作为后续业务判断、统计或响应组装的输入。
    monthly = []  # 初始化monthly中间数据列表，用于收集清洗后的多条业务数据。
    if listing_dates:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        latest = max(listing_dates)  # 计算或更新latest中间数据，作为后续业务判断、统计或响应组装的输入。
        latest_month = date(latest.year, latest.month, 1)  # 计算或更新latest_month中间数据，作为后续业务判断、统计或响应组装的输入。
        # 以样本中最新挂牌月为右边界回看 24 个月，保证历史数据不完整时仍能对齐展示。
        for month_date in _month_window(latest_month, 24):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            month = month_date.strftime("%Y-%m")  # 计算或更新month中间数据，作为后续业务判断、统计或响应组装的输入。
            month_prices = monthly_prices.get(month, [])  # 计算或更新month_prices中间数据，作为后续业务判断、统计或响应组装的输入。
            monthly.append(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                    "month": month,  # 把month字段写入响应数据，供前端页面、图表或后续接口读取。
                    "count": int(monthly_counts.get(month, 0)),  # 把count字段写入响应数据，供前端页面、图表或后续接口读取。
                    "avg_unit_price": (  # 把avg_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
                        round(sum(month_prices) / len(month_prices))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                        if month_prices  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                        else None  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
                    ),  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
                }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    recent_ratio = 0  # 计算或更新recent_ratio中间数据，作为后续业务判断、统计或响应组装的输入。
    if listing_dates:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        latest = max(listing_dates)  # 计算或更新latest中间数据，作为后续业务判断、统计或响应组装的输入。
        recent_cutoff = latest - timedelta(days=365)  # 计算或更新recent_cutoff中间数据，作为后续业务判断、统计或响应组装的输入。
        recent_ratio = sum(1 for item in listing_dates if item >= recent_cutoff) / len(  # 计算或更新recent_ratio中间数据，作为后续业务判断、统计或响应组装的输入。
            listing_dates  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        "district_id": district_id,  # 把district_id字段写入响应数据，供前端页面、图表或后续接口读取。
        "property_count": len(rows),  # 把property_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "detail_count": detail_count,  # 把detail_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "date_count": len(listing_dates),  # 把date_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "avg_unit_price": _rounded_average(prices),  # 把avg_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "median_unit_price": round(median(prices)) if prices else 0,  # 把median_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "avg_total_price": _rounded_average(totals, digits=1),  # 把avg_total_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "avg_area": _rounded_average(areas, digits=1),  # 把avg_area字段写入响应数据，供前端页面、图表或后续接口读取。
        "as_of_month": latest_month.strftime("%Y-%m") if latest_month else None,  # 把as_of_month字段写入响应数据，供前端页面、图表或后续接口读取。
        "recent_listing_ratio": round(recent_ratio * 100, 1),  # 把recent_listing_ratio字段写入响应数据，供前端页面、图表或后续接口读取。
        "monthly_listings": monthly,  # 把monthly_listings字段写入响应数据，供前端页面、图表或后续接口读取。
        "ownership_distribution": _counter_items(ownership_counter),  # 把ownership_distribution字段写入响应数据，供前端页面、图表或后续接口读取。
        "property_right_distribution": _counter_items(right_counter),  # 把property_right_distribution字段写入响应数据，供前端页面、图表或后续接口读取。
        "mortgage_distribution": _counter_items(mortgage_counter),  # 把mortgage_distribution字段写入响应数据，供前端页面、图表或后续接口读取。
        "tax_tags": _counter_items(tax_tags, total=detail_count),  # 把tax_tags字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def investment_ranking(city_id: int) -> list[dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Rank districts by a potential score based on the current data snapshot.

    The current real dataset has listing dates and transaction attributes, but
    no reliable month-by-month historical growth. The score therefore combines:
      - 价格洼地 value_score       35%
      - 市场热度 heat_score        25%
      - 周边配套 facility_score    20%
      - 交易安全 safety_score      10%
      - 挂牌新鲜度 freshness_score 10%
    """
    from models import Facility  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

    # 先以行政区为粒度聚合房源均价和挂牌量，这是投资评分的价格/热度基础样本。
    rows = [  # 初始化查询结果集合列表，用于收集清洗后的多条业务数据。
        {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "id": r.id,  # 把id字段写入响应数据，供前端页面、图表或后续接口读取。
            "name": r.name,  # 把name字段写入响应数据，供前端页面、图表或后续接口读取。
            "avg_unit_price": round(r.avg_unit_price or 0),  # 把avg_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
            "property_count": int(r.property_count or 0),  # 把property_count字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        for r in (  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            db.session.query(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                District.id,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                District.name,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                func.avg(Property.unit_price).label("avg_unit_price"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                func.count(Property.id).label("property_count"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            .join(Property, Property.district_id == District.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
            .filter(District.city_id == city_id, Property.unit_price.isnot(None))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
            .group_by(District.id)  # 按业务维度分组聚合，生成排行榜或统计指标。
            .all()  # 执行查询并取回结果，作为后续数据转换的输入。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        if r.avg_unit_price  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    if not rows:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return []  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    row_by_id = {r["id"]: r for r in rows}  # 初始化row_by_id中间数据字典，用于承载接口返回或中间聚合结果。
    prices = [r["avg_unit_price"] for r in rows]  # 初始化prices中间数据列表，用于收集清洗后的多条业务数据。
    counts = [r["property_count"] for r in rows]  # 初始化counts中间数据列表，用于收集清洗后的多条业务数据。
    p_lo, p_hi, p_mid = min(prices), max(prices), median(prices)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    c_lo, c_hi = min(counts), max(counts)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    # 配套设施按数量和类别覆盖度两个维度统计：数量代表密度，类别数代表生活便利性的广度。
    facility_stats = {  # 初始化facility_stats中间数据字典，用于承载接口返回或中间聚合结果。
        district_id: {"facility_count": int(count), "facility_category_count": int(categories)}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        for district_id, count, categories in (  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            db.session.query(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                Facility.district_id,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                func.count(Facility.id),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                func.count(func.distinct(Facility.category)),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            .filter(Facility.district_id.in_(row_by_id))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
            .group_by(Facility.district_id)  # 按业务维度分组聚合，生成排行榜或统计指标。
            .all()  # 执行查询并取回结果，作为后续数据转换的输入。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    # 交易安全和挂牌新鲜度来自 PropertyTransaction 扩展信息，通过 source_url 回连房源。
    transaction_stats = _transaction_scores(city_id)  # 计算或更新transaction_stats中间数据，作为后续业务判断、统计或响应组装的输入。
    max_facilities = max(  # 计算或更新max_facilities中间数据，作为后续业务判断、统计或响应组装的输入。
        [s["facility_count"] for s in facility_stats.values()] or [0]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    def _norm(value, lo, hi):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将指标值按上下界归一化到 0 到 1 区间。"""
        return (value - lo) / (hi - lo) if hi > lo else 0.5  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    for r in rows:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        # Low prices receive a higher value score. Areas above the city median
        # still receive a small score if they are not the most expensive.
        if r["avg_unit_price"] <= p_mid:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            value_score = _norm(p_mid - r["avg_unit_price"], 0, p_mid - p_lo)  # 计算或更新value_score中间数据，作为后续业务判断、统计或响应组装的输入。
        else:  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
            value_score = 0.35 * (1 - _norm(r["avg_unit_price"], p_mid, p_hi))  # 计算或更新value_score中间数据，作为后续业务判断、统计或响应组装的输入。

        # 使用 log1p 压缩挂牌量，避免超大商圈仅凭数量把热度分拉满。
        heat_score = _norm(log1p(r["property_count"]), log1p(c_lo), log1p(c_hi))  # 计算或更新heat_score中间数据，作为后续业务判断、统计或响应组装的输入。
        fac = facility_stats.get(r["id"], {"facility_count": 0, "facility_category_count": 0})  # 计算或更新fac中间数据，作为后续业务判断、统计或响应组装的输入。
        facility_count_score = (  # 计算或更新facility_count_score中间数据，作为后续业务判断、统计或响应组装的输入。
            fac["facility_count"] / max_facilities if max_facilities else 0  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        facility_cover_score = min(fac["facility_category_count"], 5) / 5  # 计算或更新facility_cover_score中间数据，作为后续业务判断、统计或响应组装的输入。
        facility_score = 0.55 * facility_count_score + 0.45 * facility_cover_score  # 计算或更新facility_score中间数据，作为后续业务判断、统计或响应组装的输入。

        transaction = transaction_stats.get(r["id"], {})  # 计算或更新transaction中间数据，作为后续业务判断、统计或响应组装的输入。
        safety_score = transaction.get("safety_score", 0.5)  # 计算或更新safety_score中间数据，作为后续业务判断、统计或响应组装的输入。
        freshness_score = transaction.get("freshness_score", 0.5)  # 计算或更新freshness_score中间数据，作为后续业务判断、统计或响应组装的输入。
        heat_index = 0.55 * heat_score + 0.45 * facility_score  # 计算或更新heat_index中间数据，作为后续业务判断、统计或响应组装的输入。

        # 五项指标统一转成 0-1 后再按权重合成，返回给前端时再换算成百分制。
        score = (  # 计算或更新score中间数据，作为后续业务判断、统计或响应组装的输入。
            0.35 * value_score  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            + 0.25 * heat_score  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            + 0.20 * facility_score  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            + 0.10 * safety_score  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            + 0.10 * freshness_score  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        r.update(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                "facility_count": fac["facility_count"],  # 把facility_count字段写入响应数据，供前端页面、图表或后续接口读取。
                "facility_category_count": fac["facility_category_count"],  # 把facility_category_count字段写入响应数据，供前端页面、图表或后续接口读取。
                "heat_index": round(heat_index * 100),  # 把heat_index字段写入响应数据，供前端页面、图表或后续接口读取。
                "value_score": round(value_score * 100),  # 把value_score字段写入响应数据，供前端页面、图表或后续接口读取。
                "heat_score": round(heat_score * 100),  # 把heat_score字段写入响应数据，供前端页面、图表或后续接口读取。
                "facility_score": round(facility_score * 100),  # 把facility_score字段写入响应数据，供前端页面、图表或后续接口读取。
                "safety_score": round(safety_score * 100),  # 把safety_score字段写入响应数据，供前端页面、图表或后续接口读取。
                "freshness_score": round(freshness_score * 100),  # 把freshness_score字段写入响应数据，供前端页面、图表或后续接口读取。
                "recent_listing_ratio": round(  # 把recent_listing_ratio字段写入响应数据，供前端页面、图表或后续接口读取。
                    transaction.get("recent_listing_ratio", 0) * 100  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                ),  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
                "score": round(score * 100),  # 把score字段写入响应数据，供前端页面、图表或后续接口读取。
            }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    rows.sort(key=lambda x: x["score"], reverse=True)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return rows  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _transaction_scores(city_id: int) -> dict[int, dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Aggregate transaction safety and listing freshness by district."""
    parsed = []  # 初始化parsed中间数据列表，用于收集清洗后的多条业务数据。
    safety_sum = defaultdict(float)  # 计算或更新safety_sum中间数据，作为后续业务判断、统计或响应组装的输入。
    safety_count = defaultdict(int)  # 计算或更新safety_count中间数据，作为后续业务判断、统计或响应组装的输入。
    listing_dates = defaultdict(list)  # 计算或更新listing_dates中间数据，作为后续业务判断、统计或响应组装的输入。

    # 这里只读取 district_id 和 source_url，再按需加载详情，避免把房源主体大字段全部取出。
    rows = (  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
        db.session.query(Property.district_id, Property.source_url)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .filter(District.city_id == city_id, Property.source_url.isnot(None))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    for district_id, source_url in rows:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        detail = get_property_details(source_url)  # 从请求或外部输入提取detail中间数据，用于后续校验、查询或写入。
        if not detail:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        safety_sum[district_id] += _safety_score(detail)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        safety_count[district_id] += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        listing_date = _parse_listing_date(detail.get("listing_date"))  # 计算或更新listing_date中间数据，作为后续业务判断、统计或响应组装的输入。
        if listing_date:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            listing_dates[district_id].append(listing_date)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            parsed.append(listing_date)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    # “近期挂牌”以当前样本里最新挂牌日为参照，适配离线采集数据的时间截面。
    latest = max(parsed) if parsed else None  # 计算或更新latest中间数据，作为后续业务判断、统计或响应组装的输入。
    recent_cutoff = latest - timedelta(days=365) if latest else None  # 计算或更新recent_cutoff中间数据，作为后续业务判断、统计或响应组装的输入。
    result = {}  # 初始化处理结果字典，用于承载接口返回或中间聚合结果。
    district_ids = set(safety_count) | set(listing_dates)  # 计算或更新district_ids中间数据，作为后续业务判断、统计或响应组装的输入。
    for district_id in district_ids:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        dates = listing_dates.get(district_id, [])  # 计算或更新dates中间数据，作为后续业务判断、统计或响应组装的输入。
        recent = (  # 计算或更新recent中间数据，作为后续业务判断、统计或响应组装的输入。
            sum(1 for date in dates if date >= recent_cutoff) / len(dates)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            if dates and recent_cutoff  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            else 0.5  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        result[district_id] = {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "safety_score": (  # 把safety_score字段写入响应数据，供前端页面、图表或后续接口读取。
                safety_sum[district_id] / safety_count[district_id]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                if safety_count[district_id]  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                else 0.5  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
            ),  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            "freshness_score": recent,  # 把freshness_score字段写入响应数据，供前端页面、图表或后续接口读取。
            "recent_listing_ratio": recent,  # 把recent_listing_ratio字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return result  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _safety_score(detail: dict) -> float:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """根据产权、抵押和税费标签计算交易安全评分。"""
    score = 0.0  # 计算或更新score中间数据，作为后续业务判断、统计或响应组装的输入。
    ownership = detail.get("ownership_type") or ""  # 计算或更新ownership中间数据，作为后续业务判断、统计或响应组装的输入。
    right = detail.get("property_right") or ""  # 计算或更新right中间数据，作为后续业务判断、统计或响应组装的输入。
    mortgage = detail.get("mortgage") or ""  # 计算或更新mortgage中间数据，作为后续业务判断、统计或响应组装的输入。
    selling_point = detail.get("selling_point") or ""  # 计算或更新selling_point中间数据，作为后续业务判断、统计或响应组装的输入。

    if "商品房" in ownership:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        score += 0.35  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    elif "已购公房" in ownership:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        score += 0.25  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    elif ownership:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        score += 0.15  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    if "非共有" in right:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        score += 0.25  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    elif "共有" in right:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        score += 0.12  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    if "无抵押" in mortgage:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        score += 0.25  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    elif mortgage:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        score += 0.08  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    if any(token in selling_point for token in ("满五", "满二", "有证", "证满")):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        score += 0.15  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    return min(score, 1.0)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _parse_listing_date(value):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """解析挂牌日期文本并转换为日期对象。"""
    from datetime import datetime  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

    if not value:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        try:  # 开始执行可能失败的外部访问、数据转换或数据库操作。
            return datetime.strptime(value, fmt).date()  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        except ValueError:  # 捕获异常并转换为可控的错误处理或提示信息。
            continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _rounded_average(values, digits=0):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """计算数值列表平均值并按指定位数取整。"""
    if not values:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return 0  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    value = sum(values) / len(values)  # 计算或更新value中间数据，作为后续业务判断、统计或响应组装的输入。
    return round(value, digits) if digits else round(value)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _count_clean(counter, value):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """清理文本后写入计数器，忽略空值。"""
    text = (value or "").strip()  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
    if text:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        counter[text] += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。


def _normalize_mortgage(value):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """将抵押信息文本归一化为前端可展示的分类。"""
    text = (value or "").strip()  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
    if not text:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    if "无抵押" in text:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return "无抵押"  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    if "抵押" in text:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return "有抵押"  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return text[:16]  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _counter_items(counter, total=None, limit=8):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """把计数器转换为带数量和占比的列表。"""
    denominator = total or sum(counter.values())  # 计算或更新denominator中间数据，作为后续业务判断、统计或响应组装的输入。
    if not denominator:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return []  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return [  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "name": name,  # 把name字段写入响应数据，供前端页面、图表或后续接口读取。
            "count": int(count),  # 把count字段写入响应数据，供前端页面、图表或后续接口读取。
            "ratio": round(count / denominator * 100, 1),  # 把ratio字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        for name, count in counter.most_common(limit)  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def _month_window(end_month, count):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """生成指定结束月份之前的连续月份窗口。"""
    return [_shift_months(end_month, offset) for offset in range(1 - count, 1)]  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _shift_months(month, offset):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """按月偏移日期并返回月份起始日。"""
    month_index = month.year * 12 + month.month - 1 + offset  # 计算或更新month_index中间数据，作为后续业务判断、统计或响应组装的输入。
    return date(month_index // 12, month_index % 12 + 1, 1)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
