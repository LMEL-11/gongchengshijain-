"""全国二手房数据服务（基于真实 province_data.csv）。

数据列：省份, 城市, 二手房, 新房, 租房（均为挂牌量）。
为与地图（DataV GeoJSON）的区域名匹配，名称统一做规范化处理。
"""
import csv  # 导入本行所需的模块或对象。
from functools import lru_cache  # 导入本行所需的模块或对象。
from pathlib import Path  # 导入本行所需的模块或对象。

from sqlalchemy import func  # 导入本行所需的模块或对象。

from extensions import db  # 导入本行所需的模块或对象。
from models import City, District, Property  # 导入本行所需的模块或对象。

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "province_data.csv"  # 赋值或更新当前变量/字段。
HOUSE_INFO_FILE = Path(__file__).resolve().parent.parent / "data" / "raw" / "house_info.tsv"  # 赋值或更新当前变量/字段。

# 长名 -> 短名（自治区/特别行政区），其余按后缀裁剪。
_SPECIAL = {  # 赋值或更新当前变量/字段。
    "内蒙古自治区": "内蒙古",  # 设置当前数据项或参数。
    "广西壮族自治区": "广西",  # 设置当前数据项或参数。
    "宁夏回族自治区": "宁夏",  # 设置当前数据项或参数。
    "新疆维吾尔自治区": "新疆",  # 设置当前数据项或参数。
    "西藏自治区": "西藏",  # 设置当前数据项或参数。
    "香港特别行政区": "香港",  # 设置当前数据项或参数。
    "澳门特别行政区": "澳门",  # 设置当前数据项或参数。
}  # 结束当前数据结构或调用块。


def normalize_name(name: str) -> str:  # 声明函数或方法入口。
    """北京市->北京、山东省->山东、崂山区->崂山、内蒙古自治区->内蒙古。幂等。"""
    if not name:  # 根据条件判断是否进入该分支。
        return ""  # 返回当前逻辑的处理结果。
    name = name.strip()  # 赋值或更新当前变量/字段。
    if name in _SPECIAL:  # 根据条件判断是否进入该分支。
        return _SPECIAL[name]  # 返回当前逻辑的处理结果。
    for suffix in ("特别行政区", "自治区", "省", "市", "区", "县"):  # 遍历集合中的每一项并执行处理。
        if name.endswith(suffix) and len(name) - len(suffix) >= 2:  # 根据条件判断是否进入该分支。
            return name[: -len(suffix)]  # 返回当前逻辑的处理结果。
    return name  # 返回当前逻辑的处理结果。


def _num(value: str) -> int:  # 声明函数或方法入口。
    """将输入值安全转换为浮点数，失败时返回零。"""
    value = (value or "").strip().replace(",", "")  # 赋值或更新当前变量/字段。
    return int(value) if value.isdigit() else 0  # 返回当前逻辑的处理结果。


@lru_cache(maxsize=1)  # 应用装饰器配置路由、权限或命令。
def _rows() -> list[dict]:  # 声明函数或方法入口。
    """从全国静态 CSV 数据中读取并缓存原始行。"""
    rows = []  # 赋值或更新当前变量/字段。
    with open(DATA_FILE, encoding="utf-8-sig") as f:  # utf-8-sig 去除 BOM
        for r in csv.DictReader(f):  # 遍历集合中的每一项并执行处理。
            rows.append(  # 执行本行代码逻辑。
                {  # 执行本行代码逻辑。
                    "province": normalize_name(r.get("省份", "")),  # 设置当前数据项或参数。
                    "city": normalize_name(r.get("城市", "")),  # 设置当前数据项或参数。
                    "ershou": _num(r.get("二手房")),  # 设置当前数据项或参数。
                    "xinfang": _num(r.get("新房")),  # 设置当前数据项或参数。
                    "zufang": _num(r.get("租房")),  # 设置当前数据项或参数。
                }  # 结束当前数据结构或调用块。
            )  # 结束当前数据结构或调用块。
    return rows  # 返回当前逻辑的处理结果。


def summary() -> dict:  # 声明函数或方法入口。
    """返回全国或真实数据模式的总览统计信息。"""
    rows = _rows()  # 赋值或更新当前变量/字段。
    top_cities = sorted(  # 赋值或更新当前变量/字段。
        ({"name": r["city"], "value": r["ershou"]} for r in rows),  # 设置当前数据项或参数。
        key=lambda x: x["value"],  # 赋值或更新当前变量/字段。
        reverse=True,  # 赋值或更新当前变量/字段。
    )[:10]  # 设置当前数据项或参数。
    return {  # 返回当前逻辑的处理结果。
        "ershou_total": sum(r["ershou"] for r in rows),  # 设置当前数据项或参数。
        "xinfang_total": sum(r["xinfang"] for r in rows),  # 设置当前数据项或参数。
        "zufang_total": sum(r["zufang"] for r in rows),  # 设置当前数据项或参数。
        "province_count": len({r["province"] for r in rows}),  # 设置当前数据项或参数。
        "city_count": len(rows),  # 设置当前数据项或参数。
        "top_cities": top_cities,  # 设置当前数据项或参数。
    }  # 结束当前数据结构或调用块。


def provinces() -> list[dict]:  # 声明函数或方法入口。
    """各省聚合（二手房/新房/租房合计 + 城市数），按二手房降序。"""
    agg: dict[str, dict] = {}  # 赋值或更新当前变量/字段。
    for r in _rows():  # 遍历集合中的每一项并执行处理。
        a = agg.setdefault(  # 赋值或更新当前变量/字段。
            r["province"],  # 设置当前数据项或参数。
            {"name": r["province"], "ershou": 0, "xinfang": 0, "zufang": 0, "city_count": 0},  # 设置当前数据项或参数。
        )  # 结束当前数据结构或调用块。
        a["ershou"] += r["ershou"]  # 赋值或更新当前变量/字段。
        a["xinfang"] += r["xinfang"]  # 赋值或更新当前变量/字段。
        a["zufang"] += r["zufang"]  # 赋值或更新当前变量/字段。
        a["city_count"] += 1  # 赋值或更新当前变量/字段。
    rows = sorted(agg.values(), key=lambda x: x["ershou"], reverse=True)  # 赋值或更新当前变量/字段。
    for i, r in enumerate(rows, 1):  # 遍历集合中的每一项并执行处理。
        r["rank"] = i  # 赋值或更新当前变量/字段。
    return rows  # 返回当前逻辑的处理结果。


def cities(province: str) -> list[dict]:  # 声明函数或方法入口。
    """某省下属城市列表，按二手房降序。province 可传长名或短名。"""
    key = normalize_name(province)  # 赋值或更新当前变量/字段。
    rows = [  # 赋值或更新当前变量/字段。
        {"name": r["city"], "ershou": r["ershou"], "xinfang": r["xinfang"], "zufang": r["zufang"]}  # 设置当前数据项或参数。
        for r in _rows()  # 遍历集合中的每一项并执行处理。
        if r["province"] == key  # 根据条件判断是否进入该分支。
    ]  # 结束当前数据结构或调用块。
    return sorted(rows, key=lambda x: x["ershou"], reverse=True)  # 返回当前逻辑的处理结果。


# ===== 基于真实采集房源（Property 表）的聚合 —— 供大屏「真实数据」模式 =====
# 区域名沿用 normalize_name，与地图 GeoJSON（DataV）一致；City.province / City.name
# 入库时已是短名，可直接匹配。

def _rooms_bucket(rooms: int) -> str:  # 声明函数或方法入口。
    """根据户型室数生成户型区间标签。"""
    r = rooms or 0  # 赋值或更新当前变量/字段。
    if r <= 1:  # 根据条件判断是否进入该分支。
        return "1室"  # 返回当前逻辑的处理结果。
    if r == 2:  # 根据条件判断是否进入该分支。
        return "2室"  # 返回当前逻辑的处理结果。
    if r == 3:  # 根据条件判断是否进入该分支。
        return "3室"  # 返回当前逻辑的处理结果。
    return "4室+"  # 返回当前逻辑的处理结果。


def _clean_text(value: str) -> str:  # 声明函数或方法入口。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    value = (value or "").strip()  # 赋值或更新当前变量/字段。
    if value in {"None", "暂无数据", "未知"}:  # 根据条件判断是否进入该分支。
        return ""  # 返回当前逻辑的处理结果。
    return value  # 返回当前逻辑的处理结果。


_CHONGQING_AREA_ADMIN = {  # 赋值或更新当前变量/字段。
    "西永": "沙坪坝区",  # 设置当前数据项或参数。
    "大学城": "沙坪坝区",  # 设置当前数据项或参数。
    "陈家桥": "沙坪坝区",  # 设置当前数据项或参数。
    "天星桥": "沙坪坝区",  # 设置当前数据项或参数。
    "小龙坎": "沙坪坝区",  # 设置当前数据项或参数。
    "沙正街": "沙坪坝区",  # 设置当前数据项或参数。
    "龙洲湾": "巴南区",  # 设置当前数据项或参数。
    "李家沱": "巴南区",  # 设置当前数据项或参数。
    "鱼洞": "巴南区",  # 设置当前数据项或参数。
    "鹿角": "巴南区",  # 设置当前数据项或参数。
    "融汇半岛": "巴南区",  # 设置当前数据项或参数。
    "南坪": "南岸区",  # 设置当前数据项或参数。
    "融侨半岛": "南岸区",  # 设置当前数据项或参数。
    "茶园新区": "南岸区",  # 设置当前数据项或参数。
    "弹子石": "南岸区",  # 设置当前数据项或参数。
    "杨家坪": "九龙坡区",  # 设置当前数据项或参数。
    "石坪桥": "九龙坡区",  # 设置当前数据项或参数。
    "彩云湖": "九龙坡区",  # 设置当前数据项或参数。
    "马王乡": "九龙坡区",  # 设置当前数据项或参数。
    "黄桷坪": "九龙坡区",  # 设置当前数据项或参数。
    "九宫庙": "大渡口区",  # 设置当前数据项或参数。
    "双山": "大渡口区",  # 设置当前数据项或参数。
    "北滨路": "江北区",  # 设置当前数据项或参数。
    "海尔路": "江北区",  # 设置当前数据项或参数。
    "南桥寺": "江北区",  # 设置当前数据项或参数。
    "石子山": "江北区",  # 设置当前数据项或参数。
    "鱼嘴": "江北区",  # 设置当前数据项或参数。
    "两路口": "渝中区",  # 设置当前数据项或参数。
    "大溪沟": "渝中区",  # 设置当前数据项或参数。
    "中央公园": "渝北区",  # 设置当前数据项或参数。
    "中央公园东区": "渝北区",  # 设置当前数据项或参数。
    "悦来": "渝北区",  # 设置当前数据项或参数。
    "汽博中心": "渝北区",  # 设置当前数据项或参数。
    "礼嘉": "渝北区",  # 设置当前数据项或参数。
    "空港新城": "渝北区",  # 设置当前数据项或参数。
    "黄泥磅": "渝北区",  # 设置当前数据项或参数。
    "龙兴": "渝北区",  # 设置当前数据项或参数。
    "龙溪": "渝北区",  # 设置当前数据项或参数。
    "鸳鸯": "渝北区",  # 设置当前数据项或参数。
    "大竹林": "渝北区",  # 设置当前数据项或参数。
    "蔡家": "北碚区",  # 设置当前数据项或参数。
    "璧山": "璧山区",  # 设置当前数据项或参数。
    "双福新区": "江津区",  # 设置当前数据项或参数。
    "周家坝": "万州区",  # 设置当前数据项或参数。
    "桃花新城": "长寿区",  # 设置当前数据项或参数。
}  # 结束当前数据结构或调用块。


@lru_cache(maxsize=1)  # 应用装饰器配置路由、权限或命令。
def _business_area_admin_map() -> dict[tuple[str, str], str]:  # 声明函数或方法入口。
    """Map (city, business area) to administrative district from raw TSV.

    The imported ``districts.name`` for Shandong data is mostly the business
    area column (``quyu``). The city-level DataV map, however, uses official
    administrative districts (``region``). This lookup lets the big screen roll
    business areas up to the matching map regions without changing property
    detail records.
    """
    mapping: dict[tuple[str, str], dict[str, int]] = {}  # 赋值或更新当前变量/字段。

    if HOUSE_INFO_FILE.exists():  # 根据条件判断是否进入该分支。
        with open(HOUSE_INFO_FILE, encoding="utf-8-sig", newline="") as f:  # 进入上下文管理器并自动处理资源。
            for row in csv.DictReader(f, delimiter="\t"):  # 遍历集合中的每一项并执行处理。
                city = normalize_name(_clean_text(row.get("city", "")))  # 赋值或更新当前变量/字段。
                business_area = normalize_name(_clean_text(row.get("quyu", "")))  # 赋值或更新当前变量/字段。
                admin = _clean_text(row.get("region", ""))  # 赋值或更新当前变量/字段。
                if not city or not business_area or not admin:  # 根据条件判断是否进入该分支。
                    continue  # 跳过本轮循环剩余逻辑。
                bucket = mapping.setdefault((city, business_area), {})  # 赋值或更新当前变量/字段。
                bucket[admin] = bucket.get(admin, 0) + 1  # 赋值或更新当前变量/字段。

    result = {  # 赋值或更新当前变量/字段。
        key: max(counts.items(), key=lambda item: item[1])[0]  # 赋值或更新当前变量/字段。
        for key, counts in mapping.items()  # 遍历集合中的每一项并执行处理。
    }  # 结束当前数据结构或调用块。
    result.update(  # 执行本行代码逻辑。
        {  # 执行本行代码逻辑。
            ("重庆", normalize_name(area)): admin  # 设置当前数据项或参数。
            for area, admin in _CHONGQING_AREA_ADMIN.items()  # 遍历集合中的每一项并执行处理。
        }  # 结束当前数据结构或调用块。
    )  # 结束当前数据结构或调用块。
    return result  # 返回当前逻辑的处理结果。


def real_summary() -> dict:  # 声明函数或方法入口。
    """真实房源总量、覆盖省/市/商圈数、平均单价、城市 TOP10、户型分布。"""
    total = db.session.query(func.count(Property.id)).scalar() or 0  # 赋值或更新当前变量/字段。
    avg_price = db.session.query(func.avg(Property.unit_price)).scalar() or 0  # 赋值或更新当前变量/字段。
    province_count = (  # 赋值或更新当前变量/字段。
        db.session.query(func.count(func.distinct(City.province)))  # 执行本行代码逻辑。
        .filter(City.province.isnot(None))  # 执行本行代码逻辑。
        .scalar()  # 执行本行代码逻辑。
        or 0  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    city_count = db.session.query(func.count(func.distinct(District.city_id))).scalar() or 0  # 赋值或更新当前变量/字段。
    district_count = db.session.query(func.count(func.distinct(Property.district_id))).scalar() or 0  # 赋值或更新当前变量/字段。

    top = (  # 赋值或更新当前变量/字段。
        db.session.query(City.name, func.count(Property.id).label("c"))  # 执行本行代码逻辑。
        .select_from(Property)  # 执行本行代码逻辑。
        .join(District, Property.district_id == District.id)  # 执行本行代码逻辑。
        .join(City, District.city_id == City.id)  # 执行本行代码逻辑。
        .group_by(City.id)  # 执行本行代码逻辑。
        .order_by(func.count(Property.id).desc())  # 执行本行代码逻辑。
        .limit(10)  # 执行本行代码逻辑。
        .all()  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    top_cities = [{"name": normalize_name(n), "value": int(c)} for n, c in top]  # 赋值或更新当前变量/字段。

    order = ["1室", "2室", "3室", "4室+"]  # 赋值或更新当前变量/字段。
    buckets = {k: 0 for k in order}  # 赋值或更新当前变量/字段。
    for rooms, c in db.session.query(Property.rooms, func.count(Property.id)).group_by(Property.rooms).all():  # 遍历集合中的每一项并执行处理。
        buckets[_rooms_bucket(rooms)] += int(c)  # 赋值或更新当前变量/字段。
    room_dist = [{"name": k, "value": buckets[k]} for k in order if buckets[k]]  # 赋值或更新当前变量/字段。

    return {  # 返回当前逻辑的处理结果。
        "count": int(total),  # 设置当前数据项或参数。
        "avg_price": round(avg_price or 0),  # 设置当前数据项或参数。
        "province_count": int(province_count),  # 设置当前数据项或参数。
        "city_count": int(city_count),  # 设置当前数据项或参数。
        "district_count": int(district_count),  # 设置当前数据项或参数。
        "top_cities": top_cities,  # 设置当前数据项或参数。
        "room_dist": room_dist,  # 设置当前数据项或参数。
    }  # 结束当前数据结构或调用块。


def real_provinces() -> list[dict]:  # 声明函数或方法入口。
    """各省真实房源数 + 均价 + 城市数 + 商圈数，按房源数降序（全国地图着色 + 排行）。"""
    rows = (  # 赋值或更新当前变量/字段。
        db.session.query(  # 执行本行代码逻辑。
            City.province,  # 设置当前数据项或参数。
            func.count(Property.id),  # 设置当前数据项或参数。
            func.avg(Property.unit_price),  # 设置当前数据项或参数。
            func.count(func.distinct(City.id)),  # 设置当前数据项或参数。
            func.count(func.distinct(District.id)),  # 设置当前数据项或参数。
        )  # 结束当前数据结构或调用块。
        .select_from(Property)  # 执行本行代码逻辑。
        .join(District, Property.district_id == District.id)  # 执行本行代码逻辑。
        .join(City, District.city_id == City.id)  # 执行本行代码逻辑。
        .filter(City.province.isnot(None))  # 执行本行代码逻辑。
        .group_by(City.province)  # 执行本行代码逻辑。
        .order_by(func.count(Property.id).desc())  # 执行本行代码逻辑。
        .all()  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    return [  # 返回当前逻辑的处理结果。
        {  # 执行本行代码逻辑。
            "name": normalize_name(prov),  # 设置当前数据项或参数。
            "count": int(cnt),  # 设置当前数据项或参数。
            "avg_price": round(avg or 0),  # 设置当前数据项或参数。
            "city_count": int(cc),  # 设置当前数据项或参数。
            "district_count": int(dc),  # 设置当前数据项或参数。
            "rank": i,  # 设置当前数据项或参数。
        }  # 结束当前数据结构或调用块。
        for i, (prov, cnt, avg, cc, dc) in enumerate(rows, 1)  # 遍历集合中的每一项并执行处理。
    ]  # 结束当前数据结构或调用块。


def real_cities(province: str) -> list[dict]:  # 声明函数或方法入口。
    """某省下属城市真实房源数 + 均价 + 商圈数（省级地图着色 + 城市排行）。"""
    key = normalize_name(province)  # 赋值或更新当前变量/字段。
    if key == "重庆":  # 根据条件判断是否进入该分支。
        return real_districts("重庆")  # 返回当前逻辑的处理结果。
    rows = (  # 赋值或更新当前变量/字段。
        db.session.query(  # 执行本行代码逻辑。
            City.name,  # 设置当前数据项或参数。
            City.province,  # 设置当前数据项或参数。
            func.count(Property.id),  # 设置当前数据项或参数。
            func.avg(Property.unit_price),  # 设置当前数据项或参数。
            func.count(func.distinct(District.id)),  # 设置当前数据项或参数。
        )  # 结束当前数据结构或调用块。
        .select_from(Property)  # 执行本行代码逻辑。
        .join(District, Property.district_id == District.id)  # 执行本行代码逻辑。
        .join(City, District.city_id == City.id)  # 执行本行代码逻辑。
        .group_by(City.id)  # 执行本行代码逻辑。
        .all()  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    out = [  # 赋值或更新当前变量/字段。
        {  # 执行本行代码逻辑。
            "name": normalize_name(name),  # 设置当前数据项或参数。
            "count": int(cnt),  # 设置当前数据项或参数。
            "avg_price": round(avg or 0),  # 设置当前数据项或参数。
            "district_count": int(dc),  # 设置当前数据项或参数。
        }  # 结束当前数据结构或调用块。
        for name, prov, cnt, avg, dc in rows  # 遍历集合中的每一项并执行处理。
        if normalize_name(prov) == key  # 根据条件判断是否进入该分支。
    ]  # 结束当前数据结构或调用块。
    return sorted(out, key=lambda x: x["count"], reverse=True)  # 返回当前逻辑的处理结果。


def real_districts(city: str) -> list[dict]:  # 声明函数或方法入口。
    """某城市行政区真实房源数 + 均价（市级地图着色 + 行政区排行）。

    Shandong imported data stores business areas as ``District.name``. For city
    maps, aggregate those business areas back to administrative districts using
    the raw TSV's ``region`` column so labels match DataV boundaries.
    """
    key = normalize_name(city)  # 赋值或更新当前变量/字段。
    area_to_admin = _business_area_admin_map()  # 赋值或更新当前变量/字段。
    rows = (  # 赋值或更新当前变量/字段。
        db.session.query(  # 执行本行代码逻辑。
            District.name,  # 设置当前数据项或参数。
            City.name,  # 设置当前数据项或参数。
            func.count(Property.id),  # 设置当前数据项或参数。
            func.avg(Property.unit_price),  # 设置当前数据项或参数。
            func.sum(Property.unit_price),  # 设置当前数据项或参数。
            func.count(func.distinct(District.id)),  # 设置当前数据项或参数。
        )  # 结束当前数据结构或调用块。
        .select_from(Property)  # 执行本行代码逻辑。
        .join(District, Property.district_id == District.id)  # 执行本行代码逻辑。
        .join(City, District.city_id == City.id)  # 执行本行代码逻辑。
        .group_by(District.id)  # 执行本行代码逻辑。
        .all()  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    agg: dict[str, dict] = {}  # 赋值或更新当前变量/字段。
    for dname, cname, cnt, avg, price_sum, business_count in rows:  # 遍历集合中的每一项并执行处理。
        if normalize_name(cname) != key:  # 根据条件判断是否进入该分支。
            continue  # 跳过本轮循环剩余逻辑。
        admin = area_to_admin.get((key, normalize_name(dname)), dname)  # 赋值或更新当前变量/字段。
        item = agg.setdefault(  # 赋值或更新当前变量/字段。
            admin,  # 设置当前数据项或参数。
            {"name": admin, "count": 0, "price_sum": 0.0, "district_count": 0},  # 设置当前数据项或参数。
        )  # 结束当前数据结构或调用块。
        item["count"] += int(cnt)  # 赋值或更新当前变量/字段。
        item["price_sum"] += float(price_sum or 0)  # 赋值或更新当前变量/字段。
        item["district_count"] += int(business_count or 0)  # 赋值或更新当前变量/字段。

    out = []  # 赋值或更新当前变量/字段。
    for item in agg.values():  # 遍历集合中的每一项并执行处理。
        count = item["count"]  # 赋值或更新当前变量/字段。
        out.append({  # 执行本行代码逻辑。
            "name": item["name"],  # 设置当前数据项或参数。
            "count": count,  # 设置当前数据项或参数。
            "avg_price": round(item["price_sum"] / count) if count else 0,  # 设置当前数据项或参数。
            "district_count": item["district_count"],  # 设置当前数据项或参数。
        })  # 执行本行代码逻辑。
    return sorted(out, key=lambda x: x["count"], reverse=True)  # 返回当前逻辑的处理结果。


def real_area_properties(city: str, area: str, limit: int = 800) -> dict:  # 声明函数或方法入口。
    """Property points for a city-level administrative area on the big screen."""
    city_key = normalize_name(city)  # 赋值或更新当前变量/字段。
    area_key = normalize_name(area)  # 赋值或更新当前变量/字段。
    limit = min(max(int(limit or 800), 1), 2000)  # 赋值或更新当前变量/字段。
    area_to_admin = _business_area_admin_map()  # 赋值或更新当前变量/字段。

    district_rows = (  # 赋值或更新当前变量/字段。
        db.session.query(District.id, District.name, City.name)  # 执行本行代码逻辑。
        .join(City, District.city_id == City.id)  # 执行本行代码逻辑。
        .all()  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    district_ids = []  # 赋值或更新当前变量/字段。
    for district_id, district_name, city_name in district_rows:  # 遍历集合中的每一项并执行处理。
        if normalize_name(city_name) != city_key:  # 根据条件判断是否进入该分支。
            continue  # 跳过本轮循环剩余逻辑。
        admin = area_to_admin.get((city_key, normalize_name(district_name)), district_name)  # 赋值或更新当前变量/字段。
        if normalize_name(admin) == area_key:  # 根据条件判断是否进入该分支。
            district_ids.append(district_id)  # 执行本行代码逻辑。

    if not district_ids:  # 根据条件判断是否进入该分支。
        return _empty_area_payload(city, area)  # 返回当前逻辑的处理结果。

    total = (  # 赋值或更新当前变量/字段。
        db.session.query(func.count(Property.id))  # 执行本行代码逻辑。
        .filter(Property.district_id.in_(district_ids))  # 执行本行代码逻辑。
        .scalar()  # 执行本行代码逻辑。
        or 0  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    avg_price = (  # 赋值或更新当前变量/字段。
        db.session.query(func.avg(Property.unit_price))  # 执行本行代码逻辑。
        .filter(Property.district_id.in_(district_ids), Property.unit_price.isnot(None))  # 执行本行代码逻辑。
        .scalar()  # 执行本行代码逻辑。
        or 0  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    coordinate_count = (  # 赋值或更新当前变量/字段。
        db.session.query(func.count(Property.id))  # 执行本行代码逻辑。
        .filter(  # 执行本行代码逻辑。
            Property.district_id.in_(district_ids),  # 设置当前数据项或参数。
            Property.lng.isnot(None),  # 设置当前数据项或参数。
            Property.lat.isnot(None),  # 设置当前数据项或参数。
        )  # 结束当前数据结构或调用块。
        .scalar()  # 执行本行代码逻辑。
        or 0  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    center = (  # 赋值或更新当前变量/字段。
        db.session.query(func.avg(Property.lng), func.avg(Property.lat))  # 执行本行代码逻辑。
        .filter(  # 执行本行代码逻辑。
            Property.district_id.in_(district_ids),  # 设置当前数据项或参数。
            Property.lng.isnot(None),  # 设置当前数据项或参数。
            Property.lat.isnot(None),  # 设置当前数据项或参数。
        )  # 结束当前数据结构或调用块。
        .first()  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    rows = (  # 赋值或更新当前变量/字段。
        db.session.query(Property)  # 执行本行代码逻辑。
        .filter(  # 执行本行代码逻辑。
            Property.district_id.in_(district_ids),  # 设置当前数据项或参数。
            Property.lng.isnot(None),  # 设置当前数据项或参数。
            Property.lat.isnot(None),  # 设置当前数据项或参数。
        )  # 结束当前数据结构或调用块。
        .order_by(Property.unit_price.desc(), Property.id.asc())  # 执行本行代码逻辑。
        .limit(limit)  # 执行本行代码逻辑。
        .all()  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。

    return {  # 返回当前逻辑的处理结果。
        "city": normalize_name(city),  # 设置当前数据项或参数。
        "area": area,  # 设置当前数据项或参数。
        "property_count": int(total),  # 设置当前数据项或参数。
        "coordinate_count": int(coordinate_count),  # 设置当前数据项或参数。
        "returned_count": len(rows),  # 设置当前数据项或参数。
        "avg_price": round(avg_price or 0),  # 设置当前数据项或参数。
        "center": {  # 设置当前数据项或参数。
            "lng": round(center[0], 6) if center and center[0] is not None else None,  # 设置当前数据项或参数。
            "lat": round(center[1], 6) if center and center[1] is not None else None,  # 设置当前数据项或参数。
        },  # 结束当前数据结构或调用块。
        "items": [_property_point(p) for p in rows],  # 设置当前数据项或参数。
    }  # 结束当前数据结构或调用块。


def _empty_area_payload(city: str, area: str) -> dict:  # 声明函数或方法入口。
    """生成空区域查询结果，保持接口返回结构稳定。"""
    return {  # 返回当前逻辑的处理结果。
        "city": normalize_name(city),  # 设置当前数据项或参数。
        "area": area,  # 设置当前数据项或参数。
        "property_count": 0,  # 设置当前数据项或参数。
        "coordinate_count": 0,  # 设置当前数据项或参数。
        "returned_count": 0,  # 设置当前数据项或参数。
        "avg_price": 0,  # 设置当前数据项或参数。
        "center": {"lng": None, "lat": None},  # 设置当前数据项或参数。
        "items": [],  # 设置当前数据项或参数。
    }  # 结束当前数据结构或调用块。


def _property_point(prop: Property) -> dict:  # 声明函数或方法入口。
    """将房源模型转换为地图点位和列表展示数据。"""
    return {  # 返回当前逻辑的处理结果。
        "id": prop.id,  # 设置当前数据项或参数。
        "title": prop.title,  # 设置当前数据项或参数。
        "district_name": prop.district.name if prop.district else None,  # 设置当前数据项或参数。
        "total_price": prop.total_price,  # 设置当前数据项或参数。
        "unit_price": prop.unit_price,  # 设置当前数据项或参数。
        "area": prop.area,  # 设置当前数据项或参数。
        "layout": prop.layout(),  # 设置当前数据项或参数。
        "lng": prop.lng,  # 设置当前数据项或参数。
        "lat": prop.lat,  # 设置当前数据项或参数。
    }  # 结束当前数据结构或调用块。
