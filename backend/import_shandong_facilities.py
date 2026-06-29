"""Build district-level facility tags from Shandong house_info text fields."""
import argparse  # 逐行注释：导入本行所需的模块或对象。
import csv  # 逐行注释：导入本行所需的模块或对象。
from collections import Counter, defaultdict  # 逐行注释：导入本行所需的模块或对象。
from pathlib import Path  # 逐行注释：导入本行所需的模块或对象。

from app import create_app  # 逐行注释：导入本行所需的模块或对象。
from extensions import db  # 逐行注释：导入本行所需的模块或对象。
from models import City, District, Facility  # 逐行注释：导入本行所需的模块或对象。


BASE_DIR = Path(__file__).resolve().parent  # 逐行注释：赋值或更新当前变量/字段。
DEFAULT_TSV = BASE_DIR / "data" / "raw" / "house_info.tsv"  # 逐行注释：赋值或更新当前变量/字段。
TEXT_FIELDS = ("maidian", "jieshao", "huxingjieshao", "jiaotong")  # 逐行注释：赋值或更新当前变量/字段。
MAX_FACILITIES_PER_DISTRICT = 8  # 逐行注释：赋值或更新当前变量/字段。

RULES = (  # 逐行注释：赋值或更新当前变量/字段。
    ("school", "学校/幼儿园", ("学校", "幼儿园", "小学", "中学", "一中", "二中", "大学", "学区", "上学", "陪读", "烟大")),  # 逐行注释：设置当前数据项或参数。
    ("hospital", "医院/医疗", ("医院", "诊所", "医疗", "卫生院")),  # 逐行注释：设置当前数据项或参数。
    ("hospital", "药店", ("药店", "药房")),  # 逐行注释：设置当前数据项或参数。
    ("subway", "地铁", ("地铁",)),  # 逐行注释：设置当前数据项或参数。
    ("transport", "公交站点", ("公交", "公交车", "路车", "站点", "站牌")),  # 逐行注释：设置当前数据项或参数。
    ("transport", "火车/高铁/汽车站", ("火车站", "高铁站", "汽车站", "客运站")),  # 逐行注释：设置当前数据项或参数。
    ("transport", "交通便利", ("交通便利", "出行方便", "出行便利")),  # 逐行注释：设置当前数据项或参数。
    ("mall", "商场/购物中心", ("商场", "购物", "商城", "万达", "银座", "百货", "佳世客", "大润发", "振华", "家家悦", "超市")),  # 逐行注释：设置当前数据项或参数。
    ("mall", "菜市场/早市", ("菜市场", "早市", "农贸市场")),  # 逐行注释：设置当前数据项或参数。
    ("mall", "餐饮生活", ("饭店", "餐饮", "酒店", "吃喝玩乐", "生活便利")),  # 逐行注释：设置当前数据项或参数。
    ("park", "公园/绿地", ("公园", "绿化", "体育公园", "休闲")),  # 逐行注释：设置当前数据项或参数。
    ("park", "景观休闲", ("海边", "湖", "河", "景观", "空气清新")),  # 逐行注释：设置当前数据项或参数。
)  # 逐行注释：结束当前数据结构或调用块。


def clean_text(value):  # 逐行注释：声明函数或方法入口。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    if value is None:  # 逐行注释：根据条件判断是否进入该分支。
        return ""  # 逐行注释：返回当前逻辑的处理结果。
    text = str(value).replace("\u00a0", " ").strip()  # 逐行注释：赋值或更新当前变量/字段。
    return "" if text in {"None", "暂无数据", "未知"} else text  # 逐行注释：返回当前逻辑的处理结果。


def matched_facilities(text):  # 逐行注释：声明函数或方法入口。
    """从原始房源字段中提取匹配到的周边配套设施名称。"""
    for category, name, keywords in RULES:  # 逐行注释：遍历集合中的每一项并执行处理。
        if any(keyword in text for keyword in keywords):  # 逐行注释：根据条件判断是否进入该分支。
            yield category, name  # 逐行注释：执行本行代码逻辑。


def load_matches(path):  # 逐行注释：声明函数或方法入口。
    """读取原始 TSV 数据并按城市、区域汇总设施匹配结果。"""
    matches = defaultdict(Counter)  # 逐行注释：赋值或更新当前变量/字段。
    skipped = 0  # 逐行注释：赋值或更新当前变量/字段。
    with path.open("r", encoding="utf-8-sig", newline="") as fh:  # 逐行注释：进入上下文管理器并自动处理资源。
        reader = csv.DictReader(fh, delimiter="\t")  # 逐行注释：赋值或更新当前变量/字段。
        for row in reader:  # 逐行注释：遍历集合中的每一项并执行处理。
            city = clean_text(row.get("city"))  # 逐行注释：赋值或更新当前变量/字段。
            district = clean_text(row.get("quyu")) or clean_text(row.get("region"))  # 逐行注释：赋值或更新当前变量/字段。
            if not city or not district:  # 逐行注释：根据条件判断是否进入该分支。
                skipped += 1  # 逐行注释：赋值或更新当前变量/字段。
                continue  # 逐行注释：跳过本轮循环剩余逻辑。

            text = " ".join(clean_text(row.get(field)) for field in TEXT_FIELDS)  # 逐行注释：赋值或更新当前变量/字段。
            if not text:  # 逐行注释：根据条件判断是否进入该分支。
                continue  # 逐行注释：跳过本轮循环剩余逻辑。
            for facility in matched_facilities(text):  # 逐行注释：遍历集合中的每一项并执行处理。
                matches[(city, district)][facility] += 1  # 逐行注释：赋值或更新当前变量/字段。
    return matches, skipped  # 逐行注释：返回当前逻辑的处理结果。


def existing_districts():  # 逐行注释：声明函数或方法入口。
    """加载数据库中已存在的山东城市区域映射。"""
    rows = (  # 逐行注释：赋值或更新当前变量/字段。
        db.session.query(District, City)  # 逐行注释：执行本行代码逻辑。
        .join(City, District.city_id == City.id)  # 逐行注释：执行本行代码逻辑。
        .all()  # 逐行注释：执行本行代码逻辑。
    )  # 逐行注释：结束当前数据结构或调用块。
    return {(city.name, district.name): district for district, city in rows}  # 逐行注释：返回当前逻辑的处理结果。


def main():  # 逐行注释：声明函数或方法入口。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    parser = argparse.ArgumentParser()  # 逐行注释：赋值或更新当前变量/字段。
    parser.add_argument("--file", default=str(DEFAULT_TSV), help="house_info.tsv path")  # 逐行注释：赋值或更新当前变量/字段。
    parser.add_argument(  # 逐行注释：执行本行代码逻辑。
        "--replace",  # 逐行注释：设置当前数据项或参数。
        action="store_true",  # 逐行注释：赋值或更新当前变量/字段。
        help="delete existing facilities for districts touched by this TSV first",  # 逐行注释：赋值或更新当前变量/字段。
    )  # 逐行注释：结束当前数据结构或调用块。
    args = parser.parse_args()  # 逐行注释：赋值或更新当前变量/字段。

    path = Path(args.file).expanduser().resolve()  # 逐行注释：赋值或更新当前变量/字段。
    if not path.exists():  # 逐行注释：根据条件判断是否进入该分支。
        raise SystemExit(f"TSV not found: {path}")  # 逐行注释：抛出异常并交由上层处理。

    app = create_app()  # 逐行注释：赋值或更新当前变量/字段。
    with app.app_context():  # 逐行注释：进入上下文管理器并自动处理资源。
        db.create_all()  # 逐行注释：执行本行代码逻辑。
        matches, skipped = load_matches(path)  # 逐行注释：赋值或更新当前变量/字段。
        district_by_key = existing_districts()  # 逐行注释：赋值或更新当前变量/字段。
        touched_ids = [  # 逐行注释：赋值或更新当前变量/字段。
            district.id  # 逐行注释：执行本行代码逻辑。
            for key, district in district_by_key.items()  # 逐行注释：遍历集合中的每一项并执行处理。
            if key in matches  # 逐行注释：根据条件判断是否进入该分支。
        ]  # 逐行注释：结束当前数据结构或调用块。

        if args.replace and touched_ids:  # 逐行注释：根据条件判断是否进入该分支。
            deleted = (  # 逐行注释：赋值或更新当前变量/字段。
                Facility.query.filter(Facility.district_id.in_(touched_ids))  # 逐行注释：执行本行代码逻辑。
                .delete(synchronize_session=False)  # 逐行注释：赋值或更新当前变量/字段。
            )  # 逐行注释：结束当前数据结构或调用块。
            db.session.commit()  # 逐行注释：提交当前数据库事务。
            print(f"deleted existing facilities: {deleted}")  # 逐行注释：设置当前数据项或参数。

        existing = {  # 逐行注释：赋值或更新当前变量/字段。
            (facility.district_id, facility.category, facility.name)  # 逐行注释：执行本行代码逻辑。
            for facility in Facility.query.filter(Facility.district_id.in_(touched_ids)).all()  # 逐行注释：遍历集合中的每一项并执行处理。
        }  # 逐行注释：结束当前数据结构或调用块。

        inserted = unmatched = 0  # 逐行注释：赋值或更新当前变量/字段。
        buffer = []  # 逐行注释：赋值或更新当前变量/字段。
        for key, counter in matches.items():  # 逐行注释：遍历集合中的每一项并执行处理。
            district = district_by_key.get(key)  # 逐行注释：赋值或更新当前变量/字段。
            if district is None:  # 逐行注释：根据条件判断是否进入该分支。
                unmatched += 1  # 逐行注释：赋值或更新当前变量/字段。
                continue  # 逐行注释：跳过本轮循环剩余逻辑。

            for (category, name), _count in counter.most_common(MAX_FACILITIES_PER_DISTRICT):  # 逐行注释：遍历集合中的每一项并执行处理。
                marker = (district.id, category, name)  # 逐行注释：赋值或更新当前变量/字段。
                if marker in existing:  # 逐行注释：根据条件判断是否进入该分支。
                    continue  # 逐行注释：跳过本轮循环剩余逻辑。
                buffer.append(  # 逐行注释：执行本行代码逻辑。
                    Facility(  # 逐行注释：执行本行代码逻辑。
                        district_id=district.id,  # 逐行注释：赋值或更新当前变量/字段。
                        category=category,  # 逐行注释：赋值或更新当前变量/字段。
                        name=name,  # 逐行注释：赋值或更新当前变量/字段。
                        lng=district.lng,  # 逐行注释：赋值或更新当前变量/字段。
                        lat=district.lat,  # 逐行注释：赋值或更新当前变量/字段。
                    )  # 逐行注释：结束当前数据结构或调用块。
                )  # 逐行注释：结束当前数据结构或调用块。
                existing.add(marker)  # 逐行注释：执行本行代码逻辑。

        if buffer:  # 逐行注释：根据条件判断是否进入该分支。
            db.session.bulk_save_objects(buffer)  # 逐行注释：执行本行代码逻辑。
            db.session.commit()  # 逐行注释：提交当前数据库事务。
            inserted = len(buffer)  # 逐行注释：赋值或更新当前变量/字段。

    print(f"districts with text matches: {len(matches)}")  # 逐行注释：设置当前数据项或参数。
    print(f"districts matched in DB: {len(touched_ids)}")  # 逐行注释：设置当前数据项或参数。
    print(f"districts unmatched in DB: {unmatched}")  # 逐行注释：设置当前数据项或参数。
    print(f"rows skipped without city/district: {skipped}")  # 逐行注释：设置当前数据项或参数。
    print(f"facilities inserted: {inserted}")  # 逐行注释：设置当前数据项或参数。


if __name__ == "__main__":  # 逐行注释：根据条件判断是否进入该分支。
    main()  # 逐行注释：执行本行代码逻辑。
