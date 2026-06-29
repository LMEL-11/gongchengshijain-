"""全国二手房数据服务（基于真实 province_data.csv）。

数据列：省份, 城市, 二手房, 新房, 租房（均为挂牌量）。
为与地图（DataV GeoJSON）的区域名匹配，名称统一做规范化处理。
"""
import csv
from functools import lru_cache
from pathlib import Path

from sqlalchemy import func

from extensions import db
from models import City, District, Property

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "province_data.csv"
HOUSE_INFO_FILE = Path(__file__).resolve().parent.parent / "data" / "raw" / "house_info.tsv"

# 长名 -> 短名（自治区/特别行政区），其余按后缀裁剪。
_SPECIAL = {
    "内蒙古自治区": "内蒙古",
    "广西壮族自治区": "广西",
    "宁夏回族自治区": "宁夏",
    "新疆维吾尔自治区": "新疆",
    "西藏自治区": "西藏",
    "香港特别行政区": "香港",
    "澳门特别行政区": "澳门",
}


def normalize_name(name: str) -> str:
    """北京市->北京、山东省->山东、崂山区->崂山、内蒙古自治区->内蒙古。幂等。"""
    if not name:
        return ""
    name = name.strip()
    if name in _SPECIAL:
        return _SPECIAL[name]
    for suffix in ("特别行政区", "自治区", "省", "市", "区", "县"):
        if name.endswith(suffix) and len(name) - len(suffix) >= 2:
            return name[: -len(suffix)]
    return name


def _num(value: str) -> int:
    """将输入值安全转换为浮点数，失败时返回零。"""
    value = (value or "").strip().replace(",", "")
    return int(value) if value.isdigit() else 0


@lru_cache(maxsize=1)
def _rows() -> list[dict]:
    """从全国静态 CSV 数据中读取并缓存原始行。"""
    rows = []
    with open(DATA_FILE, encoding="utf-8-sig") as f:  # utf-8-sig 去除 BOM
        for r in csv.DictReader(f):
            rows.append(
                {
                    "province": normalize_name(r.get("省份", "")),
                    "city": normalize_name(r.get("城市", "")),
                    "ershou": _num(r.get("二手房")),
                    "xinfang": _num(r.get("新房")),
                    "zufang": _num(r.get("租房")),
                }
            )
    return rows


def summary() -> dict:
    """返回全国或真实数据模式的总览统计信息。"""
    rows = _rows()
    top_cities = sorted(
        ({"name": r["city"], "value": r["ershou"]} for r in rows),
        key=lambda x: x["value"],
        reverse=True,
    )[:10]
    return {
        "ershou_total": sum(r["ershou"] for r in rows),
        "xinfang_total": sum(r["xinfang"] for r in rows),
        "zufang_total": sum(r["zufang"] for r in rows),
        "province_count": len({r["province"] for r in rows}),
        "city_count": len(rows),
        "top_cities": top_cities,
    }


def provinces() -> list[dict]:
    """各省聚合（二手房/新房/租房合计 + 城市数），按二手房降序。"""
    agg: dict[str, dict] = {}
    for r in _rows():
        a = agg.setdefault(
            r["province"],
            {"name": r["province"], "ershou": 0, "xinfang": 0, "zufang": 0, "city_count": 0},
        )
        a["ershou"] += r["ershou"]
        a["xinfang"] += r["xinfang"]
        a["zufang"] += r["zufang"]
        a["city_count"] += 1
    rows = sorted(agg.values(), key=lambda x: x["ershou"], reverse=True)
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows


def cities(province: str) -> list[dict]:
    """某省下属城市列表，按二手房降序。province 可传长名或短名。"""
    key = normalize_name(province)
    rows = [
        {"name": r["city"], "ershou": r["ershou"], "xinfang": r["xinfang"], "zufang": r["zufang"]}
        for r in _rows()
        if r["province"] == key
    ]
    return sorted(rows, key=lambda x: x["ershou"], reverse=True)


# ===== 基于真实采集房源（Property 表）的聚合 —— 供大屏「真实数据」模式 =====
# 区域名沿用 normalize_name，与地图 GeoJSON（DataV）一致；City.province / City.name
# 入库时已是短名，可直接匹配。

def _rooms_bucket(rooms: int) -> str:
    """根据户型室数生成户型区间标签。"""
    r = rooms or 0
    if r <= 1:
        return "1室"
    if r == 2:
        return "2室"
    if r == 3:
        return "3室"
    return "4室+"


def _clean_text(value: str) -> str:
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    value = (value or "").strip()
    if value in {"None", "暂无数据", "未知"}:
        return ""
    return value


_CHONGQING_AREA_ADMIN = {
    "西永": "沙坪坝区",
    "大学城": "沙坪坝区",
    "陈家桥": "沙坪坝区",
    "天星桥": "沙坪坝区",
    "小龙坎": "沙坪坝区",
    "沙正街": "沙坪坝区",
    "龙洲湾": "巴南区",
    "李家沱": "巴南区",
    "鱼洞": "巴南区",
    "鹿角": "巴南区",
    "融汇半岛": "巴南区",
    "南坪": "南岸区",
    "融侨半岛": "南岸区",
    "茶园新区": "南岸区",
    "弹子石": "南岸区",
    "杨家坪": "九龙坡区",
    "石坪桥": "九龙坡区",
    "彩云湖": "九龙坡区",
    "马王乡": "九龙坡区",
    "黄桷坪": "九龙坡区",
    "九宫庙": "大渡口区",
    "双山": "大渡口区",
    "北滨路": "江北区",
    "海尔路": "江北区",
    "南桥寺": "江北区",
    "石子山": "江北区",
    "鱼嘴": "江北区",
    "两路口": "渝中区",
    "大溪沟": "渝中区",
    "中央公园": "渝北区",
    "中央公园东区": "渝北区",
    "悦来": "渝北区",
    "汽博中心": "渝北区",
    "礼嘉": "渝北区",
    "空港新城": "渝北区",
    "黄泥磅": "渝北区",
    "龙兴": "渝北区",
    "龙溪": "渝北区",
    "鸳鸯": "渝北区",
    "大竹林": "渝北区",
    "蔡家": "北碚区",
    "璧山": "璧山区",
    "双福新区": "江津区",
    "周家坝": "万州区",
    "桃花新城": "长寿区",
}


@lru_cache(maxsize=1)
def _business_area_admin_map() -> dict[tuple[str, str], str]:
    """Map (city, business area) to administrative district from raw TSV.

    The imported ``districts.name`` for Shandong data is mostly the business
    area column (``quyu``). The city-level DataV map, however, uses official
    administrative districts (``region``). This lookup lets the big screen roll
    business areas up to the matching map regions without changing property
    detail records.
    """
    mapping: dict[tuple[str, str], dict[str, int]] = {}

    if HOUSE_INFO_FILE.exists():
        with open(HOUSE_INFO_FILE, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                city = normalize_name(_clean_text(row.get("city", "")))
                business_area = normalize_name(_clean_text(row.get("quyu", "")))
                admin = _clean_text(row.get("region", ""))
                if not city or not business_area or not admin:
                    continue
                bucket = mapping.setdefault((city, business_area), {})
                bucket[admin] = bucket.get(admin, 0) + 1

    result = {
        key: max(counts.items(), key=lambda item: item[1])[0]
        for key, counts in mapping.items()
    }
    result.update(
        {
            ("重庆", normalize_name(area)): admin
            for area, admin in _CHONGQING_AREA_ADMIN.items()
        }
    )
    return result


def real_summary() -> dict:
    """真实房源总量、覆盖省/市/商圈数、平均单价、城市 TOP10、户型分布。"""
    # 真实大屏的首页指标全部来自 Property 表，反映当前已采集入库的数据规模。
    total = db.session.query(func.count(Property.id)).scalar() or 0
    avg_price = db.session.query(func.avg(Property.unit_price)).scalar() or 0
    province_count = (
        db.session.query(func.count(func.distinct(City.province)))
        .filter(City.province.isnot(None))
        .scalar()
        or 0
    )
    city_count = db.session.query(func.count(func.distinct(District.city_id))).scalar() or 0
    district_count = db.session.query(func.count(func.distinct(Property.district_id))).scalar() or 0

    top = (
        db.session.query(City.name, func.count(Property.id).label("c"))
        .select_from(Property)
        .join(District, Property.district_id == District.id)
        .join(City, District.city_id == City.id)
        .group_by(City.id)
        .order_by(func.count(Property.id).desc())
        .limit(10)
        .all()
    )
    top_cities = [{"name": normalize_name(n), "value": int(c)} for n, c in top]

    order = ["1室", "2室", "3室", "4室+"]
    buckets = {k: 0 for k in order}
    for rooms, c in db.session.query(Property.rooms, func.count(Property.id)).group_by(Property.rooms).all():
        buckets[_rooms_bucket(rooms)] += int(c)
    room_dist = [{"name": k, "value": buckets[k]} for k in order if buckets[k]]

    return {
        "count": int(total),
        "avg_price": round(avg_price or 0),
        "province_count": int(province_count),
        "city_count": int(city_count),
        "district_count": int(district_count),
        "top_cities": top_cities,
        "room_dist": room_dist,
    }


def real_provinces() -> list[dict]:
    """各省真实房源数 + 均价 + 城市数 + 商圈数，按房源数降序（全国地图着色 + 排行）。"""
    # 全国地图用省份名作为 key，因此这里按 City.province 聚合房源量和均价。
    rows = (
        db.session.query(
            City.province,
            func.count(Property.id),
            func.avg(Property.unit_price),
            func.count(func.distinct(City.id)),
            func.count(func.distinct(District.id)),
        )
        .select_from(Property)
        .join(District, Property.district_id == District.id)
        .join(City, District.city_id == City.id)
        .filter(City.province.isnot(None))
        .group_by(City.province)
        .order_by(func.count(Property.id).desc())
        .all()
    )
    return [
        {
            "name": normalize_name(prov),
            "count": int(cnt),
            "avg_price": round(avg or 0),
            "city_count": int(cc),
            "district_count": int(dc),
            "rank": i,
        }
        for i, (prov, cnt, avg, cc, dc) in enumerate(rows, 1)
    ]


def real_cities(province: str) -> list[dict]:
    """某省下属城市真实房源数 + 均价 + 商圈数（省级地图着色 + 城市排行）。"""
    key = normalize_name(province)
    # 直辖市没有“省 -> 市”的中间层，点击后直接展示行政区聚合。
    if key == "重庆":
        return real_districts("重庆")
    rows = (
        db.session.query(
            City.name,
            City.province,
            func.count(Property.id),
            func.avg(Property.unit_price),
            func.count(func.distinct(District.id)),
        )
        .select_from(Property)
        .join(District, Property.district_id == District.id)
        .join(City, District.city_id == City.id)
        .group_by(City.id)
        .all()
    )
    out = [
        {
            "name": normalize_name(name),
            "count": int(cnt),
            "avg_price": round(avg or 0),
            "district_count": int(dc),
        }
        for name, prov, cnt, avg, dc in rows
        if normalize_name(prov) == key
    ]
    return sorted(out, key=lambda x: x["count"], reverse=True)


def real_districts(city: str) -> list[dict]:
    """某城市行政区真实房源数 + 均价（市级地图着色 + 行政区排行）。

    Shandong imported data stores business areas as ``District.name``. For city
    maps, aggregate those business areas back to administrative districts using
    the raw TSV's ``region`` column so labels match DataV boundaries.
    """
    key = normalize_name(city)
    area_to_admin = _business_area_admin_map()
    # 先按导入时的 District.name 聚合，再用原始 TSV 映射把商圈归并到行政区，
    # 这样返回名称能和城市级 GeoJSON 边界对上。
    rows = (
        db.session.query(
            District.name,
            City.name,
            func.count(Property.id),
            func.avg(Property.unit_price),
            func.sum(Property.unit_price),
            func.count(func.distinct(District.id)),
        )
        .select_from(Property)
        .join(District, Property.district_id == District.id)
        .join(City, District.city_id == City.id)
        .group_by(District.id)
        .all()
    )
    agg: dict[str, dict] = {}
    for dname, cname, cnt, avg, price_sum, business_count in rows:
        if normalize_name(cname) != key:
            continue
        admin = area_to_admin.get((key, normalize_name(dname)), dname)
        item = agg.setdefault(
            admin,
            {"name": admin, "count": 0, "price_sum": 0.0, "district_count": 0},
        )
        item["count"] += int(cnt)
        item["price_sum"] += float(price_sum or 0)
        item["district_count"] += int(business_count or 0)

    out = []
    for item in agg.values():
        count = item["count"]
        out.append({
            "name": item["name"],
            "count": count,
            "avg_price": round(item["price_sum"] / count) if count else 0,
            "district_count": item["district_count"],
        })
    return sorted(out, key=lambda x: x["count"], reverse=True)


def real_area_properties(city: str, area: str, limit: int = 800) -> dict:
    """Property points for a city-level administrative area on the big screen."""
    city_key = normalize_name(city)
    area_key = normalize_name(area)
    limit = min(max(int(limit or 800), 1), 2000)
    area_to_admin = _business_area_admin_map()

    # 前端点击的是行政区名称，数据库里可能存的是商圈名；先找出属于该行政区的所有 District.id。
    district_rows = (
        db.session.query(District.id, District.name, City.name)
        .join(City, District.city_id == City.id)
        .all()
    )
    district_ids = []
    for district_id, district_name, city_name in district_rows:
        if normalize_name(city_name) != city_key:
            continue
        admin = area_to_admin.get((city_key, normalize_name(district_name)), district_name)
        if normalize_name(admin) == area_key:
            district_ids.append(district_id)

    if not district_ids:
        return _empty_area_payload(city, area)

    total = (
        db.session.query(func.count(Property.id))
        .filter(Property.district_id.in_(district_ids))
        .scalar()
        or 0
    )
    avg_price = (
        db.session.query(func.avg(Property.unit_price))
        .filter(Property.district_id.in_(district_ids), Property.unit_price.isnot(None))
        .scalar()
        or 0
    )
    coordinate_count = (
        db.session.query(func.count(Property.id))
        .filter(
            Property.district_id.in_(district_ids),
            Property.lng.isnot(None),
            Property.lat.isnot(None),
        )
        .scalar()
        or 0
    )
    center = (
        db.session.query(func.avg(Property.lng), func.avg(Property.lat))
        .filter(
            Property.district_id.in_(district_ids),
            Property.lng.isnot(None),
            Property.lat.isnot(None),
        )
        .first()
    )
    # 百度地图只绘制有经纬度的房源点，列表按单价倒序取前 limit 条，避免一次返回过大。
    rows = (
        db.session.query(Property)
        .filter(
            Property.district_id.in_(district_ids),
            Property.lng.isnot(None),
            Property.lat.isnot(None),
        )
        .order_by(Property.unit_price.desc(), Property.id.asc())
        .limit(limit)
        .all()
    )

    return {
        "city": normalize_name(city),
        "area": area,
        "property_count": int(total),
        "coordinate_count": int(coordinate_count),
        "returned_count": len(rows),
        "avg_price": round(avg_price or 0),
        "center": {
            "lng": round(center[0], 6) if center and center[0] is not None else None,
            "lat": round(center[1], 6) if center and center[1] is not None else None,
        },
        "items": [_property_point(p) for p in rows],
    }


def _empty_area_payload(city: str, area: str) -> dict:
    """生成空区域查询结果，保持接口返回结构稳定。"""
    return {
        "city": normalize_name(city),
        "area": area,
        "property_count": 0,
        "coordinate_count": 0,
        "returned_count": 0,
        "avg_price": 0,
        "center": {"lng": None, "lat": None},
        "items": [],
    }


def _property_point(prop: Property) -> dict:
    """将房源模型转换为地图点位和列表展示数据。"""
    return {
        "id": prop.id,
        "title": prop.title,
        "district_name": prop.district.name if prop.district else None,
        "total_price": prop.total_price,
        "unit_price": prop.unit_price,
        "area": prop.area,
        "layout": prop.layout(),
        "lng": prop.lng,
        "lat": prop.lat,
    }
