"""Import Shandong house_info TSV data into the app schema.

Source file columns come from ``house_info.tsv``. The importer cleans the raw
fields and writes data into cities, districts, and properties so existing API
endpoints can serve the records directly.
"""
import argparse
import csv
import math
import re
from collections import defaultdict
from pathlib import Path

from sqlalchemy import func

from app import create_app
from extensions import db
from models import City, District, Property


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TSV = BASE_DIR.parent.parent / "house_info.tsv"
SOURCE = "shandong_house_info"
BATCH_SIZE = 3000


def clean_text(value, default=None, limit=None):
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    if value is None:
        return default
    text = str(value).replace("\u00a0", " ").strip()
    if not text or text in {"None", "暂无数据", "未知", "未知结构"}:
        return default
    return text[:limit] if limit else text


def parse_float(value):
    """从文本中提取可用数字并转换为浮点值。"""
    text = clean_text(value)
    if not text:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    if not match:
        return None
    try:
        number = float(match.group())
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def parse_layout(value):
    """从户型文本中解析室和厅数量。"""
    text = clean_text(value, "") or ""
    rooms = halls = 0
    room_match = re.search(r"(\d+)\s*室", text)
    hall_match = re.search(r"(\d+)\s*厅", text)
    if room_match:
        rooms = int(room_match.group(1))
    if hall_match:
        halls = int(hall_match.group(1))
    return rooms, halls


def parse_floor(value):
    """从楼层文本中推断所在楼层和总楼层。"""
    text = clean_text(value, "") or ""
    total_match = re.search(r"共\s*(\d+)\s*层", text)
    total_floors = int(total_match.group(1)) if total_match else None

    floor = None
    if "低楼层" in text and total_floors:
        floor = max(1, round(total_floors * 0.25))
    elif "中楼层" in text and total_floors:
        floor = max(1, round(total_floors * 0.5))
    elif "高楼层" in text and total_floors:
        floor = max(1, round(total_floors * 0.8))
    else:
        floor_match = re.search(r"(\d+)\s*层", text)
        if floor_match:
            floor = int(floor_match.group(1))
    return floor, total_floors


def has_elevator(total_floors, elevator_text):
    """根据电梯字段和总楼层判断房源是否有电梯。"""
    text = clean_text(elevator_text, "") or ""
    if "电梯" in text:
        return True
    return bool(total_floors and total_floors >= 7)


def make_title(row):
    """根据小区、户型和面积字段生成房源标题。"""
    community = clean_text(row.get("mingcheng"), "山东房源", 120)
    layout = clean_text(row.get("huxing"), limit=40)
    area = clean_text(row.get("mianji"), limit=20)
    parts = [community]
    if layout:
        parts.append(layout)
    if area:
        parts.append(area)
    return " ".join(parts)[:200]


def normalized_row(row):
    """清洗并标准化一行原始山东房源数据。"""
    # 原始 TSV 同时包含商圈、行政区、价格文本和坐标文本；这里先把它收敛成
    # Property 入库所需的强类型字段，异常或明显离群的数据直接丢弃。
    city = clean_text(row.get("city"), limit=50)
    if not city:
        return None

    district = (
        clean_text(row.get("quyu"), limit=50)
        or clean_text(row.get("region"), limit=50)
        or "未知区域"
    )
    area = parse_float(row.get("mianji"))
    unit_price = parse_float(row.get("price"))
    # 面积和单价是后续统计、地图和预测的核心指标，过滤掉缺失或明显不合理的样本。
    if (
        not area
        or area < 10
        or area > 1000
        or not unit_price
        or unit_price < 500
    ):
        return None

    lng = parse_float(row.get("jingdu"))
    lat = parse_float(row.get("weidu"))
    # 山东采集数据的经纬度应落在大致省域范围内，越界坐标视为无效但不丢弃房源。
    if lng is not None and not (110 <= lng <= 125):
        lng = None
    if lat is not None and not (30 <= lat <= 40):
        lat = None

    rooms, halls = parse_layout(row.get("huxing"))
    floor, total_floors = parse_floor(row.get("louceng"))
    return {
        "city": city,
        "district": district,
        "title": make_title(row),
        "total_price": round(unit_price * area / 10000, 2),
        "unit_price": round(unit_price),
        "area": round(area, 2),
        "rooms": rooms,
        "halls": halls,
        "floor": floor,
        "total_floors": total_floors,
        "build_year": None,
        "orientation": clean_text(row.get("chaoxiang"), limit=20),
        "decoration": clean_text(row.get("zhuangxiu"), limit=20),
        "has_elevator": has_elevator(total_floors, row.get("tihu")),
        "listing_type": "二手房",
        "lng": lng,
        "lat": lat,
        "source": SOURCE,
        "source_url": clean_text(row.get("link"), limit=500),
    }


def load_rows(path):
    """读取 TSV 文件并返回标准化房源、坐标统计和跳过数量。"""
    rows = []
    city_points = defaultdict(list)
    district_points = defaultdict(list)
    skipped = 0
    # 读取时同步收集城市/区域坐标样本，后续用于给新建 City/District 计算中心点。
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for raw in reader:
            item = normalized_row(raw)
            if item is None:
                skipped += 1
                continue
            rows.append(item)
            if item["lng"] is not None and item["lat"] is not None:
                city_points[item["city"]].append((item["lng"], item["lat"]))
                district_points[(item["city"], item["district"])].append(
                    (item["lng"], item["lat"])
                )
    return rows, city_points, district_points, skipped


def average_point(points):
    """计算一组经纬度坐标的平均中心点。"""
    if not points:
        return None, None
    return (
        round(sum(p[0] for p in points) / len(points), 6),
        round(sum(p[1] for p in points) / len(points), 6),
    )


def ensure_cities(rows, city_points):
    """确保导入数据涉及的城市存在，并补全城市坐标。"""
    city_ids = {}
    city_names = sorted({row["city"] for row in rows})
    existing = {
        city.name: city
        for city in City.query.filter(City.name.in_(city_names)).all()
    }
    # 城市按名称去重：已存在则补省份/坐标，新城市则创建并立即 flush 拿到 id。
    for name in city_names:
        lng, lat = average_point(city_points.get(name))
        city = existing.get(name)
        if city is None:
            city = City(name=name, province="山东", lng=lng, lat=lat)
            db.session.add(city)
            db.session.flush()
        else:
            city.province = city.province or "山东"
            if lng is not None:
                city.lng = lng
            if lat is not None:
                city.lat = lat
        city_ids[name] = city.id
    db.session.commit()
    return city_ids


def ensure_districts(rows, city_ids, district_points):
    """确保导入数据涉及的区域存在，并补全区域坐标和网格位置。"""
    district_ids = {}
    names_by_city = defaultdict(set)
    for row in rows:
        names_by_city[city_ids[row["city"]]].add(row["district"])

    # 区域以“城市 id + 区域名”为唯一业务键，网格坐标用于无真实边界时的 3D 排布。
    for city_id, names in names_by_city.items():
        existing = {
            district.name: district
            for district in District.query.filter(
                District.city_id == city_id,
                District.name.in_(sorted(names)),
            ).all()
        }
        city_name = next(k for k, v in city_ids.items() if v == city_id)
        for index, name in enumerate(sorted(names)):
            lng, lat = average_point(district_points.get((city_name, name)))
            district = existing.get(name)
            if district is None:
                district = District(
                    city_id=city_id,
                    name=name,
                    lng=lng,
                    lat=lat,
                    grid_x=index % 12,
                    grid_y=index // 12,
                )
                db.session.add(district)
                db.session.flush()
            else:
                if lng is not None:
                    district.lng = lng
                if lat is not None:
                    district.lat = lat
                district.grid_x = district.grid_x or index % 12
                district.grid_y = district.grid_y or index // 12
            district_ids[(city_name, name)] = district.id
    db.session.commit()
    return district_ids


def insert_properties(rows, district_ids):
    """批量插入去重后的山东房源记录。"""
    source_urls = [row["source_url"] for row in rows if row["source_url"]]
    existing_urls = set()
    # source_url 是采集房源的天然去重键，先分批查询已有链接，避免重复导入。
    for start in range(0, len(source_urls), 10000):
        batch = source_urls[start : start + 10000]
        existing_urls.update(
            url
            for (url,) in db.session.query(Property.source_url)
            .filter(Property.source_url.in_(batch))
            .all()
        )

    inserted = skipped = 0
    buffer = []
    # 插入阶段只保留区域能匹配且链接未出现过的房源，分批提交降低事务和内存压力。
    for row in rows:
        if row["source_url"] and row["source_url"] in existing_urls:
            skipped += 1
            continue
        data = dict(row)
        city = data.pop("city")
        district = data.pop("district")
        data["district_id"] = district_ids[(city, district)]
        buffer.append(Property(**data))
        if len(buffer) >= BATCH_SIZE:
            db.session.bulk_save_objects(buffer)
            db.session.commit()
            inserted += len(buffer)
            print(f"inserted {inserted} properties ...")
            buffer.clear()

    if buffer:
        db.session.bulk_save_objects(buffer)
        db.session.commit()
        inserted += len(buffer)
    return inserted, skipped


def main():
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=str(DEFAULT_TSV), help="house_info.tsv path")
    parser.add_argument(
        "--replace",
        action="store_true",
        help=f"delete existing properties with source={SOURCE!r} before import",
    )
    args = parser.parse_args()

    path = Path(args.file).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"TSV not found: {path}")

    app = create_app()
    with app.app_context():
        db.create_all()
        before = db.session.query(func.count(Property.id)).scalar()
        if args.replace:
            deleted = Property.query.filter_by(source=SOURCE).delete(
                synchronize_session=False
            )
            db.session.commit()
            print(f"deleted existing {SOURCE} properties: {deleted}")

        rows, city_points, district_points, invalid = load_rows(path)
        print(f"loaded valid rows: {len(rows)}, skipped invalid rows: {invalid}")
        city_ids = ensure_cities(rows, city_points)
        district_ids = ensure_districts(rows, city_ids, district_points)
        inserted, duplicate = insert_properties(rows, district_ids)
        after = db.session.query(func.count(Property.id)).scalar()

    print(f"cities touched: {len(city_ids)}")
    print(f"districts touched: {len(district_ids)}")
    print(f"properties before: {before}")
    print(f"properties inserted: {inserted}")
    print(f"properties skipped duplicate: {duplicate}")
    print(f"properties after: {after}")


if __name__ == "__main__":
    main()
