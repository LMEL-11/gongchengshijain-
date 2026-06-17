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
    if value is None:
        return default
    text = str(value).replace("\u00a0", " ").strip()
    if not text or text in {"None", "暂无数据", "未知", "未知结构"}:
        return default
    return text[:limit] if limit else text


def parse_float(value):
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
    text = clean_text(elevator_text, "") or ""
    if "电梯" in text:
        return True
    return bool(total_floors and total_floors >= 7)


def make_title(row):
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
    rows = []
    city_points = defaultdict(list)
    district_points = defaultdict(list)
    skipped = 0
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
    if not points:
        return None, None
    return (
        round(sum(p[0] for p in points) / len(points), 6),
        round(sum(p[1] for p in points) / len(points), 6),
    )


def ensure_cities(rows, city_points):
    city_ids = {}
    city_names = sorted({row["city"] for row in rows})
    existing = {
        city.name: city
        for city in City.query.filter(City.name.in_(city_names)).all()
    }
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
    district_ids = {}
    names_by_city = defaultdict(set)
    for row in rows:
        names_by_city[city_ids[row["city"]]].add(row["district"])

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
    source_urls = [row["source_url"] for row in rows if row["source_url"]]
    existing_urls = set()
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
