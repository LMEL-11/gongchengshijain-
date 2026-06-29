"""Build district-level facility tags from Shandong house_info text fields."""
import argparse  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
import csv  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from collections import Counter, defaultdict  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from pathlib import Path  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from app import create_app  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import City, District, Facility  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


BASE_DIR = Path(__file__).resolve().parent  # 计算或更新BASE_DIR中间数据，作为后续业务判断、统计或响应组装的输入。
DEFAULT_TSV = BASE_DIR / "data" / "raw" / "house_info.tsv"  # 计算或更新DEFAULT_TSV中间数据，作为后续业务判断、统计或响应组装的输入。
TEXT_FIELDS = ("maidian", "jieshao", "huxingjieshao", "jiaotong")  # 计算或更新TEXT_FIELDS中间数据，作为后续业务判断、统计或响应组装的输入。
MAX_FACILITIES_PER_DISTRICT = 8  # 计算或更新MAX_FACILITIES_PER_DISTRICT中间数据，作为后续业务判断、统计或响应组装的输入。

RULES = (  # 计算或更新RULES中间数据，作为后续业务判断、统计或响应组装的输入。
    ("school", "学校/幼儿园", ("学校", "幼儿园", "小学", "中学", "一中", "二中", "大学", "学区", "上学", "陪读", "烟大")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("hospital", "医院/医疗", ("医院", "诊所", "医疗", "卫生院")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("hospital", "药店", ("药店", "药房")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("subway", "地铁", ("地铁",)),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("transport", "公交站点", ("公交", "公交车", "路车", "站点", "站牌")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("transport", "火车/高铁/汽车站", ("火车站", "高铁站", "汽车站", "客运站")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("transport", "交通便利", ("交通便利", "出行方便", "出行便利")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("mall", "商场/购物中心", ("商场", "购物", "商城", "万达", "银座", "百货", "佳世客", "大润发", "振华", "家家悦", "超市")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("mall", "菜市场/早市", ("菜市场", "早市", "农贸市场")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("mall", "餐饮生活", ("饭店", "餐饮", "酒店", "吃喝玩乐", "生活便利")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("park", "公园/绿地", ("公园", "绿化", "体育公园", "休闲")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ("park", "景观休闲", ("海边", "湖", "河", "景观", "空气清新")),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
)  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def clean_text(value):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    if value is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return ""  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    text = str(value).replace("\u00a0", " ").strip()  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
    return "" if text in {"None", "暂无数据", "未知"} else text  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def matched_facilities(text):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从原始房源字段中提取匹配到的周边配套设施名称。"""
    for category, name, keywords in RULES:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        if any(keyword in text for keyword in keywords):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            yield category, name  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。


def load_matches(path):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """读取原始 TSV 数据并按城市、区域汇总设施匹配结果。"""
    matches = defaultdict(Counter)  # 计算或更新matches中间数据，作为后续业务判断、统计或响应组装的输入。
    skipped = 0  # 计算或更新skipped中间数据，作为后续业务判断、统计或响应组装的输入。
    with path.open("r", encoding="utf-8-sig", newline="") as fh:  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
        reader = csv.DictReader(fh, delimiter="\t")  # 计算或更新reader中间数据，作为后续业务判断、统计或响应组装的输入。
        for row in reader:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            city = clean_text(row.get("city"))  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
            district = clean_text(row.get("quyu")) or clean_text(row.get("region"))  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
            if not city or not district:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                skipped += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

            text = " ".join(clean_text(row.get(field)) for field in TEXT_FIELDS)  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
            if not text:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            for facility in matched_facilities(text):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
                matches[(city, district)][facility] += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return matches, skipped  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def existing_districts():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """加载数据库中已存在的山东城市区域映射。"""
    rows = (  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
        db.session.query(District, City)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return {(city.name, district.name): district for district, city in rows}  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def main():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    parser = argparse.ArgumentParser()  # 计算或更新parser中间数据，作为后续业务判断、统计或响应组装的输入。
    parser.add_argument("--file", default=str(DEFAULT_TSV), help="house_info.tsv path")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    parser.add_argument(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
        "--replace",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        action="store_true",  # 计算或更新action中间数据，作为后续业务判断、统计或响应组装的输入。
        help="delete existing facilities for districts touched by this TSV first",  # 计算或更新help中间数据，作为后续业务判断、统计或响应组装的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    args = parser.parse_args()  # 计算或更新args中间数据，作为后续业务判断、统计或响应组装的输入。

    path = Path(args.file).expanduser().resolve()  # 计算或更新地图钻取路径，作为后续业务判断、统计或响应组装的输入。
    if not path.exists():  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        raise SystemExit(f"TSV not found: {path}")  # 把无法继续处理的异常上抛，交给调用方统一响应。

    app = create_app()  # 计算或更新app中间数据，作为后续业务判断、统计或响应组装的输入。
    with app.app_context():  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
        db.create_all()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        matches, skipped = load_matches(path)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        district_by_key = existing_districts()  # 计算或更新district_by_key中间数据，作为后续业务判断、统计或响应组装的输入。
        touched_ids = [  # 初始化touched_ids中间数据列表，用于收集清洗后的多条业务数据。
            district.id  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            for key, district in district_by_key.items()  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            if key in matches  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

        if args.replace and touched_ids:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            deleted = (  # 计算或更新deleted中间数据，作为后续业务判断、统计或响应组装的输入。
                Facility.query.filter(Facility.district_id.in_(touched_ids))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                .delete(synchronize_session=False)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            print(f"deleted existing facilities: {deleted}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        existing = {  # 初始化existing中间数据字典，用于承载接口返回或中间聚合结果。
            (facility.district_id, facility.category, facility.name)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            for facility in Facility.query.filter(Facility.district_id.in_(touched_ids)).all()  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

        inserted = unmatched = 0  # 计算或更新inserted中间数据，作为后续业务判断、统计或响应组装的输入。
        buffer = []  # 初始化buffer中间数据列表，用于收集清洗后的多条业务数据。
        for key, counter in matches.items():  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            district = district_by_key.get(key)  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
            if district is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                unmatched += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

            for (category, name), _count in counter.most_common(MAX_FACILITIES_PER_DISTRICT):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
                marker = (district.id, category, name)  # 计算或更新marker中间数据，作为后续业务判断、统计或响应组装的输入。
                if marker in existing:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                    continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                buffer.append(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                    Facility(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                        district_id=district.id,  # 计算或更新行政区编号，作为后续业务判断、统计或响应组装的输入。
                        category=category,  # 计算或更新category中间数据，作为后续业务判断、统计或响应组装的输入。
                        name=name,  # 计算或更新name中间数据，作为后续业务判断、统计或响应组装的输入。
                        lng=district.lng,  # 计算或更新lng中间数据，作为后续业务判断、统计或响应组装的输入。
                        lat=district.lat,  # 计算或更新lat中间数据，作为后续业务判断、统计或响应组装的输入。
                    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
                )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
                existing.add(marker)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        if buffer:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            db.session.bulk_save_objects(buffer)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            inserted = len(buffer)  # 计算或更新inserted中间数据，作为后续业务判断、统计或响应组装的输入。

    print(f"districts with text matches: {len(matches)}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    print(f"districts matched in DB: {len(touched_ids)}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    print(f"districts unmatched in DB: {unmatched}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    print(f"rows skipped without city/district: {skipped}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    print(f"facilities inserted: {inserted}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。


if __name__ == "__main__":  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    main()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
