"""把山东 house_info.tsv 原始房源数据清洗后写入项目业务表。

这个脚本主要负责三件事：
1. 从 TSV 中读取城市、区域、小区、价格、面积、户型、楼层、坐标等原始字段；
2. 清洗并转换成项目 ``Property`` 模型需要的标准字段；
3. 自动补齐 ``City``、``District``，最后批量写入 ``Property`` 表。
"""
import argparse  # 导入 argparse 模块，为当前文件提供所需功能。
import csv  # 导入 csv 模块，为当前文件提供所需功能。
import math  # 导入 math 模块，为当前文件提供所需功能。
import re  # 导入 re 模块，为当前文件提供所需功能。
from collections import defaultdict  # 从 collections 导入 defaultdict，供本文件后续逻辑调用。
from pathlib import Path  # 从 pathlib 导入 Path，供本文件后续逻辑调用。

from sqlalchemy import func  # 从 sqlalchemy 导入 func，供本文件后续逻辑调用。

from app import create_app  # 从 app 导入 create_app，供本文件后续逻辑调用。
from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import City, District, Property  # 从 models 导入 City, District, Property，供本文件后续逻辑调用。


BASE_DIR = Path(__file__).resolve().parent  # 设置 BASE_DIR 的值，供后续业务判断、查询或响应组装使用。
DEFAULT_TSV = BASE_DIR.parent.parent / "house_info.tsv"  # 设置 DEFAULT_TSV 的值，供后续业务判断、查询或响应组装使用。
SOURCE = "shandong_house_info"  # 设置 SOURCE 的值，供后续业务判断、查询或响应组装使用。
BATCH_SIZE = 3000  # 设置 BATCH_SIZE 的值，供后续业务判断、查询或响应组装使用。


def clean_text(value, default=None, limit=None):  # 定义 clean_text 函数，集中处理这一段业务逻辑。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if value is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return default  # 返回处理后的结果给调用方继续使用。
    text = str(value).replace("\u00a0", " ").strip()  # 设置 text 的值，供后续业务判断、查询或响应组装使用。
    if not text or text in {"None", "暂无数据", "未知", "未知结构"}:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return default  # 返回处理后的结果给调用方继续使用。
    return text[:limit] if limit else text  # 返回处理后的结果给调用方继续使用。


def parse_float(value):  # 定义 parse_float 函数，集中处理这一段业务逻辑。
    """从文本中提取可用数字并转换为浮点值。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    text = clean_text(value)  # 设置 text 的值，供后续业务判断、查询或响应组装使用。
    if not text:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return None  # 返回处理后的结果给调用方继续使用。
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))  # 设置 match 的值，供后续业务判断、查询或响应组装使用。
    if not match:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return None  # 返回处理后的结果给调用方继续使用。
    try:  # 开始执行可能抛出异常的代码块。
        number = float(match.group())  # 设置 number 的值，供后续业务判断、查询或响应组装使用。
    except ValueError:  # 捕获指定异常，并转入可控的错误处理流程。
        return None  # 返回处理后的结果给调用方继续使用。
    return number if math.isfinite(number) else None  # 返回处理后的结果给调用方继续使用。


def parse_layout(value):  # 定义 parse_layout 函数，集中处理这一段业务逻辑。
    """从户型文本中解析室和厅数量。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    text = clean_text(value, "") or ""  # 设置 text 的值，供后续业务判断、查询或响应组装使用。
    rooms = halls = 0  # 设置 rooms 的值，供后续业务判断、查询或响应组装使用。
    room_match = re.search(r"(\d+)\s*室", text)  # 设置 room_match 的值，供后续业务判断、查询或响应组装使用。
    hall_match = re.search(r"(\d+)\s*厅", text)  # 设置 hall_match 的值，供后续业务判断、查询或响应组装使用。
    if room_match:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        rooms = int(room_match.group(1))  # 设置 rooms 的值，供后续业务判断、查询或响应组装使用。
    if hall_match:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        halls = int(hall_match.group(1))  # 设置 halls 的值，供后续业务判断、查询或响应组装使用。
    return rooms, halls  # 返回处理后的结果给调用方继续使用。


def parse_floor(value):  # 定义 parse_floor 函数，集中处理这一段业务逻辑。
    """从楼层文本中推断所在楼层和总楼层。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    text = clean_text(value, "") or ""  # 设置 text 的值，供后续业务判断、查询或响应组装使用。
    total_match = re.search(r"共\s*(\d+)\s*层", text)  # 设置 total_match 的值，供后续业务判断、查询或响应组装使用。
    total_floors = int(total_match.group(1)) if total_match else None  # 设置 total_floors 的值，供后续业务判断、查询或响应组装使用。

    floor = None  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
    if "低楼层" in text and total_floors:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        floor = max(1, round(total_floors * 0.25))  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
    elif "中楼层" in text and total_floors:  # 在前一个条件不成立时，继续判断这个补充分支。
        floor = max(1, round(total_floors * 0.5))  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
    elif "高楼层" in text and total_floors:  # 在前一个条件不成立时，继续判断这个补充分支。
        floor = max(1, round(total_floors * 0.8))  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
    else:  # 处理前面条件都未命中的兜底分支。
        floor_match = re.search(r"(\d+)\s*层", text)  # 设置 floor_match 的值，供后续业务判断、查询或响应组装使用。
        if floor_match:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            floor = int(floor_match.group(1))  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
    return floor, total_floors  # 返回处理后的结果给调用方继续使用。


def has_elevator(total_floors, elevator_text):  # 定义 has_elevator 函数，集中处理这一段业务逻辑。
    """根据电梯字段和总楼层判断房源是否有电梯。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    text = clean_text(elevator_text, "") or ""  # 设置 text 的值，供后续业务判断、查询或响应组装使用。
    if "电梯" in text:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return True  # 返回处理后的结果给调用方继续使用。
    return bool(total_floors and total_floors >= 7)  # 返回处理后的结果给调用方继续使用。


def make_title(row):  # 定义 make_title 函数，集中处理这一段业务逻辑。
    """根据小区、户型和面积字段生成房源标题。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    community = clean_text(row.get("mingcheng"), "山东房源", 120)  # 设置 community 的值，供后续业务判断、查询或响应组装使用。
    layout = clean_text(row.get("huxing"), limit=40)  # 设置 layout 的值，供后续业务判断、查询或响应组装使用。
    area = clean_text(row.get("mianji"), limit=20)  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
    parts = [community]  # 设置 parts 的值，供后续业务判断、查询或响应组装使用。
    if layout:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        parts.append(layout)  # 执行当前代码行对应的业务处理步骤。
    if area:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        parts.append(area)  # 执行当前代码行对应的业务处理步骤。
    return " ".join(parts)[:200]  # 返回处理后的结果给调用方继续使用。


def normalized_row(row):  # 定义 normalized_row 函数，集中处理这一段业务逻辑。
    """清洗并标准化一行原始山东房源数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    # 原始 TSV 同时包含商圈、行政区、价格文本和坐标文本；这里先把它收敛成
    # Property 入库所需的强类型字段，异常或明显离群的数据直接丢弃。
    city = clean_text(row.get("city"), limit=50)  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
    if not city:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return None  # 返回处理后的结果给调用方继续使用。

    district = (  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
        clean_text(row.get("quyu"), limit=50)  # 设置 clean_text(row.get("quyu"), limit 的值，供后续业务判断、查询或响应组装使用。
        or clean_text(row.get("region"), limit=50)  # 设置 or clean_text(row.get("region"), limit 的值，供后续业务判断、查询或响应组装使用。
        or "未知区域"  # 执行当前代码行对应的业务处理步骤。
    )  # 结束当前多行数据结构或函数调用。
    area = parse_float(row.get("mianji"))  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
    unit_price = parse_float(row.get("price"))  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
    # 面积和单价是后续统计、地图和预测的核心指标，过滤掉缺失或明显不合理的样本。
    if (  # 判断当前条件是否成立，决定是否进入对应处理分支。
        not area  # 执行当前代码行对应的业务处理步骤。
        or area < 10  # 执行当前代码行对应的业务处理步骤。
        or area > 1000  # 执行当前代码行对应的业务处理步骤。
        or not unit_price  # 执行当前代码行对应的业务处理步骤。
        or unit_price < 500  # 执行当前代码行对应的业务处理步骤。
    ):  # 执行当前代码行对应的业务处理步骤。
        return None  # 返回处理后的结果给调用方继续使用。

    lng = parse_float(row.get("jingdu"))  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
    lat = parse_float(row.get("weidu"))  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。
    # 山东采集数据的经纬度应落在大致省域范围内，越界坐标视为无效但不丢弃房源。
    if lng is not None and not (110 <= lng <= 125):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        lng = None  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
    if lat is not None and not (30 <= lat <= 40):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        lat = None  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。

    rooms, halls = parse_layout(row.get("huxing"))  # 设置 rooms, halls 的值，供后续业务判断、查询或响应组装使用。
    floor, total_floors = parse_floor(row.get("louceng"))  # 设置 floor, total_floors 的值，供后续业务判断、查询或响应组装使用。
    return {  # 返回处理后的结果给调用方继续使用。
        "city": city,  # 保留字符串内容，作为说明文本或页面展示文案。
        "district": district,  # 保留字符串内容，作为说明文本或页面展示文案。
        "title": make_title(row),  # 保留字符串内容，作为说明文本或页面展示文案。
        "total_price": round(unit_price * area / 10000, 2),  # 保留字符串内容，作为说明文本或页面展示文案。
        "unit_price": round(unit_price),  # 保留字符串内容，作为说明文本或页面展示文案。
        "area": round(area, 2),  # 保留字符串内容，作为说明文本或页面展示文案。
        "rooms": rooms,  # 保留字符串内容，作为说明文本或页面展示文案。
        "halls": halls,  # 保留字符串内容，作为说明文本或页面展示文案。
        "floor": floor,  # 保留字符串内容，作为说明文本或页面展示文案。
        "total_floors": total_floors,  # 保留字符串内容，作为说明文本或页面展示文案。
        "build_year": None,  # 保留字符串内容，作为说明文本或页面展示文案。
        "orientation": clean_text(row.get("chaoxiang"), limit=20),  # 设置 "orientation": clean_text(row.get("chaoxiang"), limit 的值，供后续业务判断、查询或响应组装使用。
        "decoration": clean_text(row.get("zhuangxiu"), limit=20),  # 设置 "decoration": clean_text(row.get("zhuangxiu"), limit 的值，供后续业务判断、查询或响应组装使用。
        "has_elevator": has_elevator(total_floors, row.get("tihu")),  # 保留字符串内容，作为说明文本或页面展示文案。
        "listing_type": "二手房",  # 保留字符串内容，作为说明文本或页面展示文案。
        "lng": lng,  # 保留字符串内容，作为说明文本或页面展示文案。
        "lat": lat,  # 保留字符串内容，作为说明文本或页面展示文案。
        "source": SOURCE,  # 保留字符串内容，作为说明文本或页面展示文案。
        "source_url": clean_text(row.get("link"), limit=500),  # 设置 "source_url": clean_text(row.get("link"), limit 的值，供后续业务判断、查询或响应组装使用。
    }  # 结束当前多行数据结构或函数调用。


def load_rows(path):  # 定义 load_rows 函数，集中处理这一段业务逻辑。
    """读取 TSV 文件并返回标准化房源、坐标统计和跳过数量。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    rows = []  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
    city_points = defaultdict(list)  # 设置 city_points 的值，供后续业务判断、查询或响应组装使用。
    district_points = defaultdict(list)  # 设置 district_points 的值，供后续业务判断、查询或响应组装使用。
    skipped = 0  # 设置 skipped 的值，供后续业务判断、查询或响应组装使用。
    # 读取时同步收集城市/区域坐标样本，后续用于给新建 City/District 计算中心点。
    with path.open("r", encoding="utf-8-sig", newline="") as fh:  # 进入上下文管理流程，自动处理资源打开和释放。
        reader = csv.DictReader(fh, delimiter="\t")  # 设置 reader 的值，供后续业务判断、查询或响应组装使用。
        for raw in reader:  # 遍历当前数据集合，逐项完成处理。
            item = normalized_row(raw)  # 设置 item 的值，供后续业务判断、查询或响应组装使用。
            if item is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                skipped += 1  # 设置 skipped + 的值，供后续业务判断、查询或响应组装使用。
                continue  # 跳过当前循环项，继续处理下一项。
            rows.append(item)  # 执行当前代码行对应的业务处理步骤。
            if item["lng"] is not None and item["lat"] is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                city_points[item["city"]].append((item["lng"], item["lat"]))  # 执行当前代码行对应的业务处理步骤。
                district_points[(item["city"], item["district"])].append(  # 执行当前代码行对应的业务处理步骤。
                    (item["lng"], item["lat"])  # 执行当前代码行对应的业务处理步骤。
                )  # 结束当前多行数据结构或函数调用。
    return rows, city_points, district_points, skipped  # 返回处理后的结果给调用方继续使用。


def average_point(points):  # 定义 average_point 函数，集中处理这一段业务逻辑。
    """计算一组经纬度坐标的平均中心点。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if not points:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return None, None  # 返回处理后的结果给调用方继续使用。
    return (  # 返回处理后的结果给调用方继续使用。
        round(sum(p[0] for p in points) / len(points), 6),  # 执行当前代码行对应的业务处理步骤。
        round(sum(p[1] for p in points) / len(points), 6),  # 执行当前代码行对应的业务处理步骤。
    )  # 结束当前多行数据结构或函数调用。


def ensure_cities(rows, city_points):  # 定义 ensure_cities 函数，集中处理这一段业务逻辑。
    """确保导入数据涉及的城市存在，并补全城市坐标。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    city_ids = {}  # 设置 city_ids 的值，供后续业务判断、查询或响应组装使用。
    city_names = sorted({row["city"] for row in rows})  # 设置 city_names 的值，供后续业务判断、查询或响应组装使用。
    existing = {  # 设置 existing 的值，供后续业务判断、查询或响应组装使用。
        city.name: city  # 执行当前代码行对应的业务处理步骤。
        for city in City.query.filter(City.name.in_(city_names)).all()  # 遍历当前数据集合，逐项完成处理。
    }  # 结束当前多行数据结构或函数调用。
    # 城市按名称去重：已存在则补省份/坐标，新城市则创建并立即 flush 拿到 id。
    for name in city_names:  # 遍历当前数据集合，逐项完成处理。
        lng, lat = average_point(city_points.get(name))  # 设置 lng, lat 的值，供后续业务判断、查询或响应组装使用。
        city = existing.get(name)  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
        if city is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            city = City(name=name, province="山东", lng=lng, lat=lat)  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
            db.session.add(city)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            db.session.flush()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
        else:  # 处理前面条件都未命中的兜底分支。
            city.province = city.province or "山东"  # 设置 city.province 的值，供后续业务判断、查询或响应组装使用。
            if lng is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                city.lng = lng  # 设置 city.lng 的值，供后续业务判断、查询或响应组装使用。
            if lat is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                city.lat = lat  # 设置 city.lat 的值，供后续业务判断、查询或响应组装使用。
        city_ids[name] = city.id  # 设置 city_ids[name 的值，供后续业务判断、查询或响应组装使用。
    db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
    return city_ids  # 返回处理后的结果给调用方继续使用。


def ensure_districts(rows, city_ids, district_points):  # 定义 ensure_districts 函数，集中处理这一段业务逻辑。
    """确保导入数据涉及的区域存在，并补全区域坐标和网格位置。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    district_ids = {}  # 设置 district_ids 的值，供后续业务判断、查询或响应组装使用。
    names_by_city = defaultdict(set)  # 设置 names_by_city 的值，供后续业务判断、查询或响应组装使用。
    for row in rows:  # 遍历当前数据集合，逐项完成处理。
        names_by_city[city_ids[row["city"]]].add(row["district"])  # 执行当前代码行对应的业务处理步骤。

    # 区域以“城市 id + 区域名”为唯一业务键，网格坐标用于无真实边界时的 3D 排布。
    for city_id, names in names_by_city.items():  # 遍历当前数据集合，逐项完成处理。
        existing = {  # 设置 existing 的值，供后续业务判断、查询或响应组装使用。
            district.name: district  # 执行当前代码行对应的业务处理步骤。
            for district in District.query.filter(  # 遍历当前数据集合，逐项完成处理。
                District.city_id == city_id,  # 执行当前代码行对应的业务处理步骤。
                District.name.in_(sorted(names)),  # 执行当前代码行对应的业务处理步骤。
            ).all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
        }  # 结束当前多行数据结构或函数调用。
        city_name = next(k for k, v in city_ids.items() if v == city_id)  # 执行当前代码行对应的业务处理步骤。
        for index, name in enumerate(sorted(names)):  # 遍历当前数据集合，逐项完成处理。
            lng, lat = average_point(district_points.get((city_name, name)))  # 设置 lng, lat 的值，供后续业务判断、查询或响应组装使用。
            district = existing.get(name)  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
            if district is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                district = District(  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
                    city_id=city_id,  # 设置 city_id 的值，供后续业务判断、查询或响应组装使用。
                    name=name,  # 设置 name 的值，供后续业务判断、查询或响应组装使用。
                    lng=lng,  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
                    lat=lat,  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。
                    grid_x=index % 12,  # 设置 grid_x 的值，供后续业务判断、查询或响应组装使用。
                    grid_y=index // 12,  # 设置 grid_y 的值，供后续业务判断、查询或响应组装使用。
                )  # 结束当前多行数据结构或函数调用。
                db.session.add(district)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
                db.session.flush()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            else:  # 处理前面条件都未命中的兜底分支。
                if lng is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    district.lng = lng  # 设置 district.lng 的值，供后续业务判断、查询或响应组装使用。
                if lat is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    district.lat = lat  # 设置 district.lat 的值，供后续业务判断、查询或响应组装使用。
                district.grid_x = district.grid_x or index % 12  # 设置 district.grid_x 的值，供后续业务判断、查询或响应组装使用。
                district.grid_y = district.grid_y or index // 12  # 设置 district.grid_y 的值，供后续业务判断、查询或响应组装使用。
            district_ids[(city_name, name)] = district.id  # 设置 district_ids[(city_name, name 的值，供后续业务判断、查询或响应组装使用。
    db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
    return district_ids  # 返回处理后的结果给调用方继续使用。


def insert_properties(rows, district_ids):  # 定义 insert_properties 函数，集中处理这一段业务逻辑。
    """批量插入去重后的山东房源记录。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    source_urls = [row["source_url"] for row in rows if row["source_url"]]  # 设置 source_urls 的值，供后续业务判断、查询或响应组装使用。
    existing_urls = set()  # 设置 existing_urls 的值，供后续业务判断、查询或响应组装使用。
    # source_url 是采集房源的天然去重键，先分批查询已有链接，避免重复导入。
    for start in range(0, len(source_urls), 10000):  # 遍历当前数据集合，逐项完成处理。
        batch = source_urls[start : start + 10000]  # 设置 batch 的值，供后续业务判断、查询或响应组装使用。
        existing_urls.update(  # 执行当前代码行对应的业务处理步骤。
            url  # 执行当前代码行对应的业务处理步骤。
            for (url,) in db.session.query(Property.source_url)  # 遍历当前数据集合，逐项完成处理。
            .filter(Property.source_url.in_(batch))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
            .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
        )  # 结束当前多行数据结构或函数调用。

    inserted = skipped = 0  # 设置 inserted 的值，供后续业务判断、查询或响应组装使用。
    buffer = []  # 设置 buffer 的值，供后续业务判断、查询或响应组装使用。
    # 插入阶段只保留区域能匹配且链接未出现过的房源，分批提交降低事务和内存压力。
    for row in rows:  # 遍历当前数据集合，逐项完成处理。
        if row["source_url"] and row["source_url"] in existing_urls:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            skipped += 1  # 设置 skipped + 的值，供后续业务判断、查询或响应组装使用。
            continue  # 跳过当前循环项，继续处理下一项。
        data = dict(row)  # 设置 data 的值，供后续业务判断、查询或响应组装使用。
        city = data.pop("city")  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
        district = data.pop("district")  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
        data["district_id"] = district_ids[(city, district)]  # 设置 data["district_id" 的值，供后续业务判断、查询或响应组装使用。
        buffer.append(Property(**data))  # 执行当前代码行对应的业务处理步骤。
        if len(buffer) >= BATCH_SIZE:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            db.session.bulk_save_objects(buffer)  # 执行当前代码行对应的业务处理步骤。
            db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            inserted += len(buffer)  # 设置 inserted + 的值，供后续业务判断、查询或响应组装使用。
            print(f"inserted {inserted} properties ...")  # 输出当前处理结果或运行状态，方便调试和观察流程。
            buffer.clear()  # 执行当前代码行对应的业务处理步骤。

    if buffer:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        db.session.bulk_save_objects(buffer)  # 执行当前代码行对应的业务处理步骤。
        db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
        inserted += len(buffer)  # 设置 inserted + 的值，供后续业务判断、查询或响应组装使用。
    return inserted, skipped  # 返回处理后的结果给调用方继续使用。


def main():  # 定义 main 函数，集中处理这一段业务逻辑。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    parser = argparse.ArgumentParser()  # 设置 parser 的值，供后续业务判断、查询或响应组装使用。
    parser.add_argument("--file", default=str(DEFAULT_TSV), help="house_info.tsv path")  # 设置 parser.add_argument("--file", default 的值，供后续业务判断、查询或响应组装使用。
    parser.add_argument(  # 执行当前代码行对应的业务处理步骤。
        "--replace",  # 保留字符串内容，作为说明文本或页面展示文案。
        action="store_true",  # 设置 action 的值，供后续业务判断、查询或响应组装使用。
        help=f"delete existing properties with source={SOURCE!r} before import",  # 设置 help 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。
    args = parser.parse_args()  # 设置 args 的值，供后续业务判断、查询或响应组装使用。

    path = Path(args.file).expanduser().resolve()  # 设置 path 的值，供后续业务判断、查询或响应组装使用。
    if not path.exists():  # 判断当前条件是否成立，决定是否进入对应处理分支。
        raise SystemExit(f"TSV not found: {path}")  # 主动抛出异常，提示当前流程无法继续。

    app = create_app()  # 设置 app 的值，供后续业务判断、查询或响应组装使用。
    with app.app_context():  # 进入上下文管理流程，自动处理资源打开和释放。
        db.create_all()  # 执行当前代码行对应的业务处理步骤。
        before = db.session.query(func.count(Property.id)).scalar()  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        if args.replace:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            deleted = Property.query.filter_by(source=SOURCE).delete(  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
                synchronize_session=False  # 设置 synchronize_session 的值，供后续业务判断、查询或响应组装使用。
            )  # 结束当前多行数据结构或函数调用。
            db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            print(f"deleted existing {SOURCE} properties: {deleted}")  # 输出当前处理结果或运行状态，方便调试和观察流程。

        rows, city_points, district_points, invalid = load_rows(path)  # 设置 rows, city_points, district_points, invalid 的值，供后续业务判断、查询或响应组装使用。
        print(f"loaded valid rows: {len(rows)}, skipped invalid rows: {invalid}")  # 输出当前处理结果或运行状态，方便调试和观察流程。
        city_ids = ensure_cities(rows, city_points)  # 设置 city_ids 的值，供后续业务判断、查询或响应组装使用。
        district_ids = ensure_districts(rows, city_ids, district_points)  # 设置 district_ids 的值，供后续业务判断、查询或响应组装使用。
        inserted, duplicate = insert_properties(rows, district_ids)  # 设置 inserted, duplicate 的值，供后续业务判断、查询或响应组装使用。
        after = db.session.query(func.count(Property.id)).scalar()  # 构造数据库查询，用于读取、筛选或聚合业务数据。

    print(f"cities touched: {len(city_ids)}")  # 输出当前处理结果或运行状态，方便调试和观察流程。
    print(f"districts touched: {len(district_ids)}")  # 输出当前处理结果或运行状态，方便调试和观察流程。
    print(f"properties before: {before}")  # 输出当前处理结果或运行状态，方便调试和观察流程。
    print(f"properties inserted: {inserted}")  # 输出当前处理结果或运行状态，方便调试和观察流程。
    print(f"properties skipped duplicate: {duplicate}")  # 输出当前处理结果或运行状态，方便调试和观察流程。
    print(f"properties after: {after}")  # 输出当前处理结果或运行状态，方便调试和观察流程。


if __name__ == "__main__":  # 判断当前条件是否成立，决定是否进入对应处理分支。
    main()  # 执行当前代码行对应的业务处理步骤。
