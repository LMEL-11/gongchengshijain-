"""Import Shandong house_info TSV data into the app schema.

Source file columns come from ``house_info.tsv``. The importer cleans the raw
fields and writes data into cities, districts, and properties so existing API
endpoints can serve the records directly.
"""
import argparse  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
import csv  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
import math  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
import re  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from collections import defaultdict  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from pathlib import Path  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from sqlalchemy import func  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from app import create_app  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import City, District, Property  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


BASE_DIR = Path(__file__).resolve().parent  # 计算或更新BASE_DIR中间数据，作为后续业务判断、统计或响应组装的输入。
DEFAULT_TSV = BASE_DIR.parent.parent / "house_info.tsv"  # 计算或更新DEFAULT_TSV中间数据，作为后续业务判断、统计或响应组装的输入。
SOURCE = "shandong_house_info"  # 计算或更新SOURCE中间数据，作为后续业务判断、统计或响应组装的输入。
BATCH_SIZE = 3000  # 计算或更新BATCH_SIZE中间数据，作为后续业务判断、统计或响应组装的输入。


def clean_text(value, default=None, limit=None):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    if value is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return default  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    text = str(value).replace("\u00a0", " ").strip()  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
    if not text or text in {"None", "暂无数据", "未知", "未知结构"}:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return default  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return text[:limit] if limit else text  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def parse_float(value):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从文本中提取可用数字并转换为浮点值。"""
    text = clean_text(value)  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
    if not text:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))  # 计算或更新match中间数据，作为后续业务判断、统计或响应组装的输入。
    if not match:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    try:  # 开始执行可能失败的外部访问、数据转换或数据库操作。
        number = float(match.group())  # 计算或更新number中间数据，作为后续业务判断、统计或响应组装的输入。
    except ValueError:  # 捕获异常并转换为可控的错误处理或提示信息。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return number if math.isfinite(number) else None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def parse_layout(value):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从户型文本中解析室和厅数量。"""
    text = clean_text(value, "") or ""  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
    rooms = halls = 0  # 计算或更新rooms中间数据，作为后续业务判断、统计或响应组装的输入。
    room_match = re.search(r"(\d+)\s*室", text)  # 计算或更新room_match中间数据，作为后续业务判断、统计或响应组装的输入。
    hall_match = re.search(r"(\d+)\s*厅", text)  # 计算或更新hall_match中间数据，作为后续业务判断、统计或响应组装的输入。
    if room_match:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        rooms = int(room_match.group(1))  # 计算或更新rooms中间数据，作为后续业务判断、统计或响应组装的输入。
    if hall_match:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        halls = int(hall_match.group(1))  # 计算或更新halls中间数据，作为后续业务判断、统计或响应组装的输入。
    return rooms, halls  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def parse_floor(value):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从楼层文本中推断所在楼层和总楼层。"""
    text = clean_text(value, "") or ""  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
    total_match = re.search(r"共\s*(\d+)\s*层", text)  # 计算或更新total_match中间数据，作为后续业务判断、统计或响应组装的输入。
    total_floors = int(total_match.group(1)) if total_match else None  # 计算或更新total_floors中间数据，作为后续业务判断、统计或响应组装的输入。

    floor = None  # 计算或更新floor中间数据，作为后续业务判断、统计或响应组装的输入。
    if "低楼层" in text and total_floors:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        floor = max(1, round(total_floors * 0.25))  # 计算或更新floor中间数据，作为后续业务判断、统计或响应组装的输入。
    elif "中楼层" in text and total_floors:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        floor = max(1, round(total_floors * 0.5))  # 计算或更新floor中间数据，作为后续业务判断、统计或响应组装的输入。
    elif "高楼层" in text and total_floors:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        floor = max(1, round(total_floors * 0.8))  # 计算或更新floor中间数据，作为后续业务判断、统计或响应组装的输入。
    else:  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
        floor_match = re.search(r"(\d+)\s*层", text)  # 计算或更新floor_match中间数据，作为后续业务判断、统计或响应组装的输入。
        if floor_match:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            floor = int(floor_match.group(1))  # 计算或更新floor中间数据，作为后续业务判断、统计或响应组装的输入。
    return floor, total_floors  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def has_elevator(total_floors, elevator_text):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """根据电梯字段和总楼层判断房源是否有电梯。"""
    text = clean_text(elevator_text, "") or ""  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
    if "电梯" in text:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return True  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return bool(total_floors and total_floors >= 7)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def make_title(row):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """根据小区、户型和面积字段生成房源标题。"""
    community = clean_text(row.get("mingcheng"), "山东房源", 120)  # 计算或更新community中间数据，作为后续业务判断、统计或响应组装的输入。
    layout = clean_text(row.get("huxing"), limit=40)  # 计算或更新layout中间数据，作为后续业务判断、统计或响应组装的输入。
    area = clean_text(row.get("mianji"), limit=20)  # 计算或更新area中间数据，作为后续业务判断、统计或响应组装的输入。
    parts = [community]  # 初始化parts中间数据列表，用于收集清洗后的多条业务数据。
    if layout:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        parts.append(layout)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    if area:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        parts.append(area)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return " ".join(parts)[:200]  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def normalized_row(row):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """清洗并标准化一行原始山东房源数据。"""
    # 原始 TSV 同时包含商圈、行政区、价格文本和坐标文本；这里先把它收敛成
    # Property 入库所需的强类型字段，异常或明显离群的数据直接丢弃。
    city = clean_text(row.get("city"), limit=50)  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
    if not city:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    district = (  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
        clean_text(row.get("quyu"), limit=50)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        or clean_text(row.get("region"), limit=50)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        or "未知区域"  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    area = parse_float(row.get("mianji"))  # 计算或更新area中间数据，作为后续业务判断、统计或响应组装的输入。
    unit_price = parse_float(row.get("price"))  # 计算或更新unit_price中间数据，作为后续业务判断、统计或响应组装的输入。
    # 面积和单价是后续统计、地图和预测的核心指标，过滤掉缺失或明显不合理的样本。
    if (  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        not area  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        or area < 10  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        or area > 1000  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        or not unit_price  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        or unit_price < 500  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ):  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    lng = parse_float(row.get("jingdu"))  # 计算或更新lng中间数据，作为后续业务判断、统计或响应组装的输入。
    lat = parse_float(row.get("weidu"))  # 计算或更新lat中间数据，作为后续业务判断、统计或响应组装的输入。
    # 山东采集数据的经纬度应落在大致省域范围内，越界坐标视为无效但不丢弃房源。
    if lng is not None and not (110 <= lng <= 125):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        lng = None  # 计算或更新lng中间数据，作为后续业务判断、统计或响应组装的输入。
    if lat is not None and not (30 <= lat <= 40):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        lat = None  # 计算或更新lat中间数据，作为后续业务判断、统计或响应组装的输入。

    rooms, halls = parse_layout(row.get("huxing"))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    floor, total_floors = parse_floor(row.get("louceng"))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        "city": city,  # 把city字段写入响应数据，供前端页面、图表或后续接口读取。
        "district": district,  # 把district字段写入响应数据，供前端页面、图表或后续接口读取。
        "title": make_title(row),  # 把title字段写入响应数据，供前端页面、图表或后续接口读取。
        "total_price": round(unit_price * area / 10000, 2),  # 把total_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "unit_price": round(unit_price),  # 把unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "area": round(area, 2),  # 把area字段写入响应数据，供前端页面、图表或后续接口读取。
        "rooms": rooms,  # 把rooms字段写入响应数据，供前端页面、图表或后续接口读取。
        "halls": halls,  # 把halls字段写入响应数据，供前端页面、图表或后续接口读取。
        "floor": floor,  # 把floor字段写入响应数据，供前端页面、图表或后续接口读取。
        "total_floors": total_floors,  # 把total_floors字段写入响应数据，供前端页面、图表或后续接口读取。
        "build_year": None,  # 把build_year字段写入响应数据，供前端页面、图表或后续接口读取。
        "orientation": clean_text(row.get("chaoxiang"), limit=20),  # 把orientation字段写入响应数据，供前端页面、图表或后续接口读取。
        "decoration": clean_text(row.get("zhuangxiu"), limit=20),  # 把decoration字段写入响应数据，供前端页面、图表或后续接口读取。
        "has_elevator": has_elevator(total_floors, row.get("tihu")),  # 把has_elevator字段写入响应数据，供前端页面、图表或后续接口读取。
        "listing_type": "二手房",  # 把listing_type字段写入响应数据，供前端页面、图表或后续接口读取。
        "lng": lng,  # 把lng字段写入响应数据，供前端页面、图表或后续接口读取。
        "lat": lat,  # 把lat字段写入响应数据，供前端页面、图表或后续接口读取。
        "source": SOURCE,  # 把source字段写入响应数据，供前端页面、图表或后续接口读取。
        "source_url": clean_text(row.get("link"), limit=500),  # 把source_url字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def load_rows(path):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """读取 TSV 文件并返回标准化房源、坐标统计和跳过数量。"""
    rows = []  # 初始化查询结果集合列表，用于收集清洗后的多条业务数据。
    city_points = defaultdict(list)  # 计算或更新city_points中间数据，作为后续业务判断、统计或响应组装的输入。
    district_points = defaultdict(list)  # 计算或更新district_points中间数据，作为后续业务判断、统计或响应组装的输入。
    skipped = 0  # 计算或更新skipped中间数据，作为后续业务判断、统计或响应组装的输入。
    # 读取时同步收集城市/区域坐标样本，后续用于给新建 City/District 计算中心点。
    with path.open("r", encoding="utf-8-sig", newline="") as fh:  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
        reader = csv.DictReader(fh, delimiter="\t")  # 计算或更新reader中间数据，作为后续业务判断、统计或响应组装的输入。
        for raw in reader:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            item = normalized_row(raw)  # 计算或更新单条数据，作为后续业务判断、统计或响应组装的输入。
            if item is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                skipped += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            rows.append(item)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            if item["lng"] is not None and item["lat"] is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                city_points[item["city"]].append((item["lng"], item["lat"]))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                district_points[(item["city"], item["district"])].append(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                    (item["lng"], item["lat"])  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return rows, city_points, district_points, skipped  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def average_point(points):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """计算一组经纬度坐标的平均中心点。"""
    if not points:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return None, None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return (  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        round(sum(p[0] for p in points) / len(points), 6),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        round(sum(p[1] for p in points) / len(points), 6),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def ensure_cities(rows, city_points):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """确保导入数据涉及的城市存在，并补全城市坐标。"""
    city_ids = {}  # 初始化city_ids中间数据字典，用于承载接口返回或中间聚合结果。
    city_names = sorted({row["city"] for row in rows})  # 计算或更新city_names中间数据，作为后续业务判断、统计或响应组装的输入。
    existing = {  # 初始化existing中间数据字典，用于承载接口返回或中间聚合结果。
        city.name: city  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        for city in City.query.filter(City.name.in_(city_names)).all()  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    # 城市按名称去重：已存在则补省份/坐标，新城市则创建并立即 flush 拿到 id。
    for name in city_names:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        lng, lat = average_point(city_points.get(name))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        city = existing.get(name)  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
        if city is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            city = City(name=name, province="山东", lng=lng, lat=lat)  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
            db.session.add(city)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            db.session.flush()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
        else:  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
            city.province = city.province or "山东"  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            if lng is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                city.lng = lng  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            if lat is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                city.lat = lat  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        city_ids[name] = city.id  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
    return city_ids  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def ensure_districts(rows, city_ids, district_points):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """确保导入数据涉及的区域存在，并补全区域坐标和网格位置。"""
    district_ids = {}  # 初始化district_ids中间数据字典，用于承载接口返回或中间聚合结果。
    names_by_city = defaultdict(set)  # 计算或更新names_by_city中间数据，作为后续业务判断、统计或响应组装的输入。
    for row in rows:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        names_by_city[city_ids[row["city"]]].add(row["district"])  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    # 区域以“城市 id + 区域名”为唯一业务键，网格坐标用于无真实边界时的 3D 排布。
    for city_id, names in names_by_city.items():  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        existing = {  # 初始化existing中间数据字典，用于承载接口返回或中间聚合结果。
            district.name: district  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            for district in District.query.filter(  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
                District.city_id == city_id,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                District.name.in_(sorted(names)),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            ).all()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        city_name = next(k for k, v in city_ids.items() if v == city_id)  # 计算或更新城市名称，作为后续业务判断、统计或响应组装的输入。
        for index, name in enumerate(sorted(names)):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            lng, lat = average_point(district_points.get((city_name, name)))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            district = existing.get(name)  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
            if district is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                district = District(  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
                    city_id=city_id,  # 计算或更新城市编号，作为后续业务判断、统计或响应组装的输入。
                    name=name,  # 计算或更新name中间数据，作为后续业务判断、统计或响应组装的输入。
                    lng=lng,  # 计算或更新lng中间数据，作为后续业务判断、统计或响应组装的输入。
                    lat=lat,  # 计算或更新lat中间数据，作为后续业务判断、统计或响应组装的输入。
                    grid_x=index % 12,  # 计算或更新grid_x中间数据，作为后续业务判断、统计或响应组装的输入。
                    grid_y=index // 12,  # 计算或更新grid_y中间数据，作为后续业务判断、统计或响应组装的输入。
                )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
                db.session.add(district)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
                db.session.flush()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            else:  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
                if lng is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                    district.lng = lng  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                if lat is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                    district.lat = lat  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                district.grid_x = district.grid_x or index % 12  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                district.grid_y = district.grid_y or index // 12  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            district_ids[(city_name, name)] = district.id  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
    return district_ids  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def insert_properties(rows, district_ids):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """批量插入去重后的山东房源记录。"""
    source_urls = [row["source_url"] for row in rows if row["source_url"]]  # 初始化source_urls中间数据列表，用于收集清洗后的多条业务数据。
    existing_urls = set()  # 计算或更新existing_urls中间数据，作为后续业务判断、统计或响应组装的输入。
    # source_url 是采集房源的天然去重键，先分批查询已有链接，避免重复导入。
    for start in range(0, len(source_urls), 10000):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        batch = source_urls[start : start + 10000]  # 计算或更新batch中间数据，作为后续业务判断、统计或响应组装的输入。
        existing_urls.update(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            url  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            for (url,) in db.session.query(Property.source_url)  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            .filter(Property.source_url.in_(batch))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
            .all()  # 执行查询并取回结果，作为后续数据转换的输入。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    inserted = skipped = 0  # 计算或更新inserted中间数据，作为后续业务判断、统计或响应组装的输入。
    buffer = []  # 初始化buffer中间数据列表，用于收集清洗后的多条业务数据。
    # 插入阶段只保留区域能匹配且链接未出现过的房源，分批提交降低事务和内存压力。
    for row in rows:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        if row["source_url"] and row["source_url"] in existing_urls:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            skipped += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        data = dict(row)  # 初始化响应数据结构字典，用于承载接口返回或中间聚合结果。
        city = data.pop("city")  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
        district = data.pop("district")  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
        data["district_id"] = district_ids[(city, district)]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        buffer.append(Property(**data))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        if len(buffer) >= BATCH_SIZE:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            db.session.bulk_save_objects(buffer)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            inserted += len(buffer)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            print(f"inserted {inserted} properties ...")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            buffer.clear()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    if buffer:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        db.session.bulk_save_objects(buffer)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
        inserted += len(buffer)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return inserted, skipped  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def main():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    parser = argparse.ArgumentParser()  # 计算或更新parser中间数据，作为后续业务判断、统计或响应组装的输入。
    parser.add_argument("--file", default=str(DEFAULT_TSV), help="house_info.tsv path")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    parser.add_argument(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
        "--replace",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        action="store_true",  # 计算或更新action中间数据，作为后续业务判断、统计或响应组装的输入。
        help=f"delete existing properties with source={SOURCE!r} before import",  # 计算或更新help中间数据，作为后续业务判断、统计或响应组装的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    args = parser.parse_args()  # 计算或更新args中间数据，作为后续业务判断、统计或响应组装的输入。

    path = Path(args.file).expanduser().resolve()  # 计算或更新地图钻取路径，作为后续业务判断、统计或响应组装的输入。
    if not path.exists():  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        raise SystemExit(f"TSV not found: {path}")  # 把无法继续处理的异常上抛，交给调用方统一响应。

    app = create_app()  # 计算或更新app中间数据，作为后续业务判断、统计或响应组装的输入。
    with app.app_context():  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
        db.create_all()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        before = db.session.query(func.count(Property.id)).scalar()  # 创建before中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
        if args.replace:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            deleted = Property.query.filter_by(source=SOURCE).delete(  # 计算或更新deleted中间数据，作为后续业务判断、统计或响应组装的输入。
                synchronize_session=False  # 计算或更新synchronize_session中间数据，作为后续业务判断、统计或响应组装的输入。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            print(f"deleted existing {SOURCE} properties: {deleted}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        rows, city_points, district_points, invalid = load_rows(path)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        print(f"loaded valid rows: {len(rows)}, skipped invalid rows: {invalid}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        city_ids = ensure_cities(rows, city_points)  # 计算或更新city_ids中间数据，作为后续业务判断、统计或响应组装的输入。
        district_ids = ensure_districts(rows, city_ids, district_points)  # 计算或更新district_ids中间数据，作为后续业务判断、统计或响应组装的输入。
        inserted, duplicate = insert_properties(rows, district_ids)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        after = db.session.query(func.count(Property.id)).scalar()  # 创建after中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。

    print(f"cities touched: {len(city_ids)}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    print(f"districts touched: {len(district_ids)}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    print(f"properties before: {before}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    print(f"properties inserted: {inserted}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    print(f"properties skipped duplicate: {duplicate}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    print(f"properties after: {after}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。


if __name__ == "__main__":  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    main()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
