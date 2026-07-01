"""从山东 house_info.tsv 的文本描述中提取区域级周边配套标签。

这个脚本不写入具体房源，而是读取房源介绍、卖点、户型介绍、交通描述等文本，
按关键词规则统计每个“城市 + 区域”命中了哪些配套类型，最后写入 ``Facility`` 表。
"""
import argparse  # 导入 argparse 模块，为当前文件提供所需功能。
import csv  # 导入 csv 模块，为当前文件提供所需功能。
from collections import Counter, defaultdict  # 从 collections 导入 Counter, defaultdict，供本文件后续逻辑调用。
from pathlib import Path  # 从 pathlib 导入 Path，供本文件后续逻辑调用。

from app import create_app  # 从 app 导入 create_app，供本文件后续逻辑调用。
from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import City, District, Facility  # 从 models 导入 City, District, Facility，供本文件后续逻辑调用。


BASE_DIR = Path(__file__).resolve().parent  # 设置 BASE_DIR 的值，供后续业务判断、查询或响应组装使用。
DEFAULT_TSV = BASE_DIR / "data" / "raw" / "house_info.tsv"  # 设置 DEFAULT_TSV 的值，供后续业务判断、查询或响应组装使用。
TEXT_FIELDS = ("maidian", "jieshao", "huxingjieshao", "jiaotong")  # 设置 TEXT_FIELDS 的值，供后续业务判断、查询或响应组装使用。
MAX_FACILITIES_PER_DISTRICT = 8  # 设置 MAX_FACILITIES_PER_DISTRICT 的值，供后续业务判断、查询或响应组装使用。

RULES = (  # 设置 RULES 的值，供后续业务判断、查询或响应组装使用。
    ("school", "学校/幼儿园", ("学校", "幼儿园", "小学", "中学", "一中", "二中", "大学", "学区", "上学", "陪读", "烟大")),  # 执行当前代码行对应的业务处理步骤。
    ("hospital", "医院/医疗", ("医院", "诊所", "医疗", "卫生院")),  # 执行当前代码行对应的业务处理步骤。
    ("hospital", "药店", ("药店", "药房")),  # 执行当前代码行对应的业务处理步骤。
    ("subway", "地铁", ("地铁",)),  # 执行当前代码行对应的业务处理步骤。
    ("transport", "公交站点", ("公交", "公交车", "路车", "站点", "站牌")),  # 执行当前代码行对应的业务处理步骤。
    ("transport", "火车/高铁/汽车站", ("火车站", "高铁站", "汽车站", "客运站")),  # 执行当前代码行对应的业务处理步骤。
    ("transport", "交通便利", ("交通便利", "出行方便", "出行便利")),  # 执行当前代码行对应的业务处理步骤。
    ("mall", "商场/购物中心", ("商场", "购物", "商城", "万达", "银座", "百货", "佳世客", "大润发", "振华", "家家悦", "超市")),  # 执行当前代码行对应的业务处理步骤。
    ("mall", "菜市场/早市", ("菜市场", "早市", "农贸市场")),  # 执行当前代码行对应的业务处理步骤。
    ("mall", "餐饮生活", ("饭店", "餐饮", "酒店", "吃喝玩乐", "生活便利")),  # 执行当前代码行对应的业务处理步骤。
    ("park", "公园/绿地", ("公园", "绿化", "体育公园", "休闲")),  # 执行当前代码行对应的业务处理步骤。
    ("park", "景观休闲", ("海边", "湖", "河", "景观", "空气清新")),  # 执行当前代码行对应的业务处理步骤。
)  # 结束当前多行数据结构或函数调用。


def clean_text(value):  # 定义 clean_text 函数，集中处理这一段业务逻辑。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if value is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return ""  # 返回处理后的结果给调用方继续使用。
    text = str(value).replace("\u00a0", " ").strip()  # 设置 text 的值，供后续业务判断、查询或响应组装使用。
    return "" if text in {"None", "暂无数据", "未知"} else text  # 返回处理后的结果给调用方继续使用。


def matched_facilities(text):  # 定义 matched_facilities 函数，集中处理这一段业务逻辑。
    """从原始房源字段中提取匹配到的周边配套设施名称。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    for category, name, keywords in RULES:  # 遍历当前数据集合，逐项完成处理。
        if any(keyword in text for keyword in keywords):  # 判断当前条件是否成立，决定是否进入对应处理分支。
            yield category, name  # 产出当前请求或数据项，交给框架后续流程处理。


def load_matches(path):  # 定义 load_matches 函数，集中处理这一段业务逻辑。
    """读取原始 TSV 数据并按城市、区域汇总设施匹配结果。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    matches = defaultdict(Counter)  # 设置 matches 的值，供后续业务判断、查询或响应组装使用。
    skipped = 0  # 设置 skipped 的值，供后续业务判断、查询或响应组装使用。
    with path.open("r", encoding="utf-8-sig", newline="") as fh:  # 进入上下文管理流程，自动处理资源打开和释放。
        reader = csv.DictReader(fh, delimiter="\t")  # 设置 reader 的值，供后续业务判断、查询或响应组装使用。
        for row in reader:  # 遍历当前数据集合，逐项完成处理。
            city = clean_text(row.get("city"))  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
            district = clean_text(row.get("quyu")) or clean_text(row.get("region"))  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
            if not city or not district:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                skipped += 1  # 设置 skipped + 的值，供后续业务判断、查询或响应组装使用。
                continue  # 跳过当前循环项，继续处理下一项。

            text = " ".join(clean_text(row.get(field)) for field in TEXT_FIELDS)  # 把关联表纳入查询，获取跨表维度的数据。
            if not text:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                continue  # 跳过当前循环项，继续处理下一项。
            for facility in matched_facilities(text):  # 遍历当前数据集合，逐项完成处理。
                matches[(city, district)][facility] += 1  # 设置 matches[(city, district)][facility] + 的值，供后续业务判断、查询或响应组装使用。
    return matches, skipped  # 返回处理后的结果给调用方继续使用。


def existing_districts():  # 定义 existing_districts 函数，集中处理这一段业务逻辑。
    """加载数据库中已存在的山东城市区域映射。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    rows = (  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(District, City)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    return {(city.name, district.name): district for district, city in rows}  # 返回处理后的结果给调用方继续使用。


def main():  # 定义 main 函数，集中处理这一段业务逻辑。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    parser = argparse.ArgumentParser()  # 设置 parser 的值，供后续业务判断、查询或响应组装使用。
    parser.add_argument("--file", default=str(DEFAULT_TSV), help="house_info.tsv path")  # 设置 parser.add_argument("--file", default 的值，供后续业务判断、查询或响应组装使用。
    parser.add_argument(  # 执行当前代码行对应的业务处理步骤。
        "--replace",  # 保留字符串内容，作为说明文本或页面展示文案。
        action="store_true",  # 设置 action 的值，供后续业务判断、查询或响应组装使用。
        help="delete existing facilities for districts touched by this TSV first",  # 设置 help 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。
    args = parser.parse_args()  # 设置 args 的值，供后续业务判断、查询或响应组装使用。

    path = Path(args.file).expanduser().resolve()  # 设置 path 的值，供后续业务判断、查询或响应组装使用。
    if not path.exists():  # 判断当前条件是否成立，决定是否进入对应处理分支。
        raise SystemExit(f"TSV not found: {path}")  # 主动抛出异常，提示当前流程无法继续。

    app = create_app()  # 设置 app 的值，供后续业务判断、查询或响应组装使用。
    with app.app_context():  # 进入上下文管理流程，自动处理资源打开和释放。
        db.create_all()  # 执行当前代码行对应的业务处理步骤。
        matches, skipped = load_matches(path)  # 设置 matches, skipped 的值，供后续业务判断、查询或响应组装使用。
        district_by_key = existing_districts()  # 设置 district_by_key 的值，供后续业务判断、查询或响应组装使用。
        touched_ids = [  # 设置 touched_ids 的值，供后续业务判断、查询或响应组装使用。
            district.id  # 执行当前代码行对应的业务处理步骤。
            for key, district in district_by_key.items()  # 遍历当前数据集合，逐项完成处理。
            if key in matches  # 判断当前条件是否成立，决定是否进入对应处理分支。
        ]  # 结束当前多行数据结构或函数调用。

        if args.replace and touched_ids:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            deleted = (  # 设置 deleted 的值，供后续业务判断、查询或响应组装使用。
                Facility.query.filter(Facility.district_id.in_(touched_ids))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
                .delete(synchronize_session=False)  # 设置 .delete(synchronize_session 的值，供后续业务判断、查询或响应组装使用。
            )  # 结束当前多行数据结构或函数调用。
            db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            print(f"deleted existing facilities: {deleted}")  # 输出当前处理结果或运行状态，方便调试和观察流程。

        existing = {  # 设置 existing 的值，供后续业务判断、查询或响应组装使用。
            (facility.district_id, facility.category, facility.name)  # 执行当前代码行对应的业务处理步骤。
            for facility in Facility.query.filter(Facility.district_id.in_(touched_ids)).all()  # 遍历当前数据集合，逐项完成处理。
        }  # 结束当前多行数据结构或函数调用。

        inserted = unmatched = 0  # 设置 inserted 的值，供后续业务判断、查询或响应组装使用。
        buffer = []  # 设置 buffer 的值，供后续业务判断、查询或响应组装使用。
        for key, counter in matches.items():  # 遍历当前数据集合，逐项完成处理。
            district = district_by_key.get(key)  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
            if district is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                unmatched += 1  # 设置 unmatched + 的值，供后续业务判断、查询或响应组装使用。
                continue  # 跳过当前循环项，继续处理下一项。

            for (category, name), _count in counter.most_common(MAX_FACILITIES_PER_DISTRICT):  # 遍历当前数据集合，逐项完成处理。
                marker = (district.id, category, name)  # 设置 marker 的值，供后续业务判断、查询或响应组装使用。
                if marker in existing:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    continue  # 跳过当前循环项，继续处理下一项。
                buffer.append(  # 执行当前代码行对应的业务处理步骤。
                    Facility(  # 执行当前代码行对应的业务处理步骤。
                        district_id=district.id,  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
                        category=category,  # 设置 category 的值，供后续业务判断、查询或响应组装使用。
                        name=name,  # 设置 name 的值，供后续业务判断、查询或响应组装使用。
                        lng=district.lng,  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
                        lat=district.lat,  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。
                    )  # 结束当前多行数据结构或函数调用。
                )  # 结束当前多行数据结构或函数调用。
                existing.add(marker)  # 执行当前代码行对应的业务处理步骤。

        if buffer:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            db.session.bulk_save_objects(buffer)  # 执行当前代码行对应的业务处理步骤。
            db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            inserted = len(buffer)  # 设置 inserted 的值，供后续业务判断、查询或响应组装使用。

    print(f"districts with text matches: {len(matches)}")  # 输出当前处理结果或运行状态，方便调试和观察流程。
    print(f"districts matched in DB: {len(touched_ids)}")  # 输出当前处理结果或运行状态，方便调试和观察流程。
    print(f"districts unmatched in DB: {unmatched}")  # 输出当前处理结果或运行状态，方便调试和观察流程。
    print(f"rows skipped without city/district: {skipped}")  # 输出当前处理结果或运行状态，方便调试和观察流程。
    print(f"facilities inserted: {inserted}")  # 输出当前处理结果或运行状态，方便调试和观察流程。


if __name__ == "__main__":  # 判断当前条件是否成立，决定是否进入对应处理分支。
    main()  # 执行当前代码行对应的业务处理步骤。
