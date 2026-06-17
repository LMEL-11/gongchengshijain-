"""Build district-level facility tags from Shandong house_info text fields."""
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

from app import create_app
from extensions import db
from models import City, District, Facility


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TSV = BASE_DIR / "data" / "raw" / "house_info.tsv"
TEXT_FIELDS = ("maidian", "jieshao", "huxingjieshao", "jiaotong")
MAX_FACILITIES_PER_DISTRICT = 8

RULES = (
    ("school", "学校/幼儿园", ("学校", "幼儿园", "小学", "中学", "一中", "二中", "大学", "学区", "上学", "陪读", "烟大")),
    ("hospital", "医院/医疗", ("医院", "诊所", "医疗", "卫生院")),
    ("hospital", "药店", ("药店", "药房")),
    ("subway", "地铁", ("地铁",)),
    ("transport", "公交站点", ("公交", "公交车", "路车", "站点", "站牌")),
    ("transport", "火车/高铁/汽车站", ("火车站", "高铁站", "汽车站", "客运站")),
    ("transport", "交通便利", ("交通便利", "出行方便", "出行便利")),
    ("mall", "商场/购物中心", ("商场", "购物", "商城", "万达", "银座", "百货", "佳世客", "大润发", "振华", "家家悦", "超市")),
    ("mall", "菜市场/早市", ("菜市场", "早市", "农贸市场")),
    ("mall", "餐饮生活", ("饭店", "餐饮", "酒店", "吃喝玩乐", "生活便利")),
    ("park", "公园/绿地", ("公园", "绿化", "体育公园", "休闲")),
    ("park", "景观休闲", ("海边", "湖", "河", "景观", "空气清新")),
)


def clean_text(value):
    if value is None:
        return ""
    text = str(value).replace("\u00a0", " ").strip()
    return "" if text in {"None", "暂无数据", "未知"} else text


def matched_facilities(text):
    for category, name, keywords in RULES:
        if any(keyword in text for keyword in keywords):
            yield category, name


def load_matches(path):
    matches = defaultdict(Counter)
    skipped = 0
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            city = clean_text(row.get("city"))
            district = clean_text(row.get("quyu")) or clean_text(row.get("region"))
            if not city or not district:
                skipped += 1
                continue

            text = " ".join(clean_text(row.get(field)) for field in TEXT_FIELDS)
            if not text:
                continue
            for facility in matched_facilities(text):
                matches[(city, district)][facility] += 1
    return matches, skipped


def existing_districts():
    rows = (
        db.session.query(District, City)
        .join(City, District.city_id == City.id)
        .all()
    )
    return {(city.name, district.name): district for district, city in rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=str(DEFAULT_TSV), help="house_info.tsv path")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="delete existing facilities for districts touched by this TSV first",
    )
    args = parser.parse_args()

    path = Path(args.file).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"TSV not found: {path}")

    app = create_app()
    with app.app_context():
        db.create_all()
        matches, skipped = load_matches(path)
        district_by_key = existing_districts()
        touched_ids = [
            district.id
            for key, district in district_by_key.items()
            if key in matches
        ]

        if args.replace and touched_ids:
            deleted = (
                Facility.query.filter(Facility.district_id.in_(touched_ids))
                .delete(synchronize_session=False)
            )
            db.session.commit()
            print(f"deleted existing facilities: {deleted}")

        existing = {
            (facility.district_id, facility.category, facility.name)
            for facility in Facility.query.filter(Facility.district_id.in_(touched_ids)).all()
        }

        inserted = unmatched = 0
        buffer = []
        for key, counter in matches.items():
            district = district_by_key.get(key)
            if district is None:
                unmatched += 1
                continue

            for (category, name), _count in counter.most_common(MAX_FACILITIES_PER_DISTRICT):
                marker = (district.id, category, name)
                if marker in existing:
                    continue
                buffer.append(
                    Facility(
                        district_id=district.id,
                        category=category,
                        name=name,
                        lng=district.lng,
                        lat=district.lat,
                    )
                )
                existing.add(marker)

        if buffer:
            db.session.bulk_save_objects(buffer)
            db.session.commit()
            inserted = len(buffer)

    print(f"districts with text matches: {len(matches)}")
    print(f"districts matched in DB: {len(touched_ids)}")
    print(f"districts unmatched in DB: {unmatched}")
    print(f"rows skipped without city/district: {skipped}")
    print(f"facilities inserted: {inserted}")


if __name__ == "__main__":
    main()
