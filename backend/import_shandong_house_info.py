"""Import Shandong house_info TSV data into the app schema.

Source file columns come from ``house_info.tsv``. The importer cleans the raw
fields and writes data into cities, districts, and properties so existing API
endpoints can serve the records directly.
"""
import argparse  # 逐行注释：导入本行所需的模块或对象。
import csv  # 逐行注释：导入本行所需的模块或对象。
import math  # 逐行注释：导入本行所需的模块或对象。
import re  # 逐行注释：导入本行所需的模块或对象。
from collections import defaultdict  # 逐行注释：导入本行所需的模块或对象。
from pathlib import Path  # 逐行注释：导入本行所需的模块或对象。

from sqlalchemy import func  # 逐行注释：导入本行所需的模块或对象。

from app import create_app  # 逐行注释：导入本行所需的模块或对象。
from extensions import db  # 逐行注释：导入本行所需的模块或对象。
from models import City, District, Property  # 逐行注释：导入本行所需的模块或对象。


BASE_DIR = Path(__file__).resolve().parent  # 逐行注释：赋值或更新当前变量/字段。
DEFAULT_TSV = BASE_DIR.parent.parent / "house_info.tsv"  # 逐行注释：赋值或更新当前变量/字段。
SOURCE = "shandong_house_info"  # 逐行注释：赋值或更新当前变量/字段。
BATCH_SIZE = 3000  # 逐行注释：赋值或更新当前变量/字段。


def clean_text(value, default=None, limit=None):  # 逐行注释：声明函数或方法入口。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    if value is None:  # 逐行注释：根据条件判断是否进入该分支。
        return default  # 逐行注释：返回当前逻辑的处理结果。
    text = str(value).replace("\u00a0", " ").strip()  # 逐行注释：赋值或更新当前变量/字段。
    if not text or text in {"None", "暂无数据", "未知", "未知结构"}:  # 逐行注释：根据条件判断是否进入该分支。
        return default  # 逐行注释：返回当前逻辑的处理结果。
    return text[:limit] if limit else text  # 逐行注释：返回当前逻辑的处理结果。


def parse_float(value):  # 逐行注释：声明函数或方法入口。
    """从文本中提取可用数字并转换为浮点值。"""
    text = clean_text(value)  # 逐行注释：赋值或更新当前变量/字段。
    if not text:  # 逐行注释：根据条件判断是否进入该分支。
        return None  # 逐行注释：返回当前逻辑的处理结果。
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))  # 逐行注释：赋值或更新当前变量/字段。
    if not match:  # 逐行注释：根据条件判断是否进入该分支。
        return None  # 逐行注释：返回当前逻辑的处理结果。
    try:  # 逐行注释：开始执行可能出现异常的逻辑。
        number = float(match.group())  # 逐行注释：赋值或更新当前变量/字段。
    except ValueError:  # 逐行注释：捕获异常并执行错误处理。
        return None  # 逐行注释：返回当前逻辑的处理结果。
    return number if math.isfinite(number) else None  # 逐行注释：返回当前逻辑的处理结果。


def parse_layout(value):  # 逐行注释：声明函数或方法入口。
    """从户型文本中解析室和厅数量。"""
    text = clean_text(value, "") or ""  # 逐行注释：赋值或更新当前变量/字段。
    rooms = halls = 0  # 逐行注释：赋值或更新当前变量/字段。
    room_match = re.search(r"(\d+)\s*室", text)  # 逐行注释：赋值或更新当前变量/字段。
    hall_match = re.search(r"(\d+)\s*厅", text)  # 逐行注释：赋值或更新当前变量/字段。
    if room_match:  # 逐行注释：根据条件判断是否进入该分支。
        rooms = int(room_match.group(1))  # 逐行注释：赋值或更新当前变量/字段。
    if hall_match:  # 逐行注释：根据条件判断是否进入该分支。
        halls = int(hall_match.group(1))  # 逐行注释：赋值或更新当前变量/字段。
    return rooms, halls  # 逐行注释：返回当前逻辑的处理结果。


def parse_floor(value):  # 逐行注释：声明函数或方法入口。
    """从楼层文本中推断所在楼层和总楼层。"""
    text = clean_text(value, "") or ""  # 逐行注释：赋值或更新当前变量/字段。
    total_match = re.search(r"共\s*(\d+)\s*层", text)  # 逐行注释：赋值或更新当前变量/字段。
    total_floors = int(total_match.group(1)) if total_match else None  # 逐行注释：赋值或更新当前变量/字段。

    floor = None  # 逐行注释：赋值或更新当前变量/字段。
    if "低楼层" in text and total_floors:  # 逐行注释：根据条件判断是否进入该分支。
        floor = max(1, round(total_floors * 0.25))  # 逐行注释：赋值或更新当前变量/字段。
    elif "中楼层" in text and total_floors:  # 逐行注释：根据条件判断是否进入该分支。
        floor = max(1, round(total_floors * 0.5))  # 逐行注释：赋值或更新当前变量/字段。
    elif "高楼层" in text and total_floors:  # 逐行注释：根据条件判断是否进入该分支。
        floor = max(1, round(total_floors * 0.8))  # 逐行注释：赋值或更新当前变量/字段。
    else:  # 逐行注释：处理条件不满足时的兜底分支。
        floor_match = re.search(r"(\d+)\s*层", text)  # 逐行注释：赋值或更新当前变量/字段。
        if floor_match:  # 逐行注释：根据条件判断是否进入该分支。
            floor = int(floor_match.group(1))  # 逐行注释：赋值或更新当前变量/字段。
    return floor, total_floors  # 逐行注释：返回当前逻辑的处理结果。


def has_elevator(total_floors, elevator_text):  # 逐行注释：声明函数或方法入口。
    """根据电梯字段和总楼层判断房源是否有电梯。"""
    text = clean_text(elevator_text, "") or ""  # 逐行注释：赋值或更新当前变量/字段。
    if "电梯" in text:  # 逐行注释：根据条件判断是否进入该分支。
        return True  # 逐行注释：返回当前逻辑的处理结果。
    return bool(total_floors and total_floors >= 7)  # 逐行注释：返回当前逻辑的处理结果。


def make_title(row):  # 逐行注释：声明函数或方法入口。
    """根据小区、户型和面积字段生成房源标题。"""
    community = clean_text(row.get("mingcheng"), "山东房源", 120)  # 逐行注释：赋值或更新当前变量/字段。
    layout = clean_text(row.get("huxing"), limit=40)  # 逐行注释：赋值或更新当前变量/字段。
    area = clean_text(row.get("mianji"), limit=20)  # 逐行注释：赋值或更新当前变量/字段。
    parts = [community]  # 逐行注释：赋值或更新当前变量/字段。
    if layout:  # 逐行注释：根据条件判断是否进入该分支。
        parts.append(layout)  # 逐行注释：执行本行代码逻辑。
    if area:  # 逐行注释：根据条件判断是否进入该分支。
        parts.append(area)  # 逐行注释：执行本行代码逻辑。
    return " ".join(parts)[:200]  # 逐行注释：返回当前逻辑的处理结果。


def normalized_row(row):  # 逐行注释：声明函数或方法入口。
    """清洗并标准化一行原始山东房源数据。"""
    city = clean_text(row.get("city"), limit=50)  # 逐行注释：赋值或更新当前变量/字段。
    if not city:  # 逐行注释：根据条件判断是否进入该分支。
        return None  # 逐行注释：返回当前逻辑的处理结果。

    district = (  # 逐行注释：赋值或更新当前变量/字段。
        clean_text(row.get("quyu"), limit=50)  # 逐行注释：赋值或更新当前变量/字段。
        or clean_text(row.get("region"), limit=50)  # 逐行注释：赋值或更新当前变量/字段。
        or "未知区域"  # 逐行注释：执行本行代码逻辑。
    )  # 逐行注释：结束当前数据结构或调用块。
    area = parse_float(row.get("mianji"))  # 逐行注释：赋值或更新当前变量/字段。
    unit_price = parse_float(row.get("price"))  # 逐行注释：赋值或更新当前变量/字段。
    if (  # 逐行注释：根据条件判断是否进入该分支。
        not area  # 逐行注释：执行本行代码逻辑。
        or area < 10  # 逐行注释：执行本行代码逻辑。
        or area > 1000  # 逐行注释：执行本行代码逻辑。
        or not unit_price  # 逐行注释：执行本行代码逻辑。
        or unit_price < 500  # 逐行注释：执行本行代码逻辑。
    ):  # 逐行注释：开始一个新的缩进代码块。
        return None  # 逐行注释：返回当前逻辑的处理结果。

    lng = parse_float(row.get("jingdu"))  # 逐行注释：赋值或更新当前变量/字段。
    lat = parse_float(row.get("weidu"))  # 逐行注释：赋值或更新当前变量/字段。
    if lng is not None and not (110 <= lng <= 125):  # 逐行注释：根据条件判断是否进入该分支。
        lng = None  # 逐行注释：赋值或更新当前变量/字段。
    if lat is not None and not (30 <= lat <= 40):  # 逐行注释：根据条件判断是否进入该分支。
        lat = None  # 逐行注释：赋值或更新当前变量/字段。

    rooms, halls = parse_layout(row.get("huxing"))  # 逐行注释：赋值或更新当前变量/字段。
    floor, total_floors = parse_floor(row.get("louceng"))  # 逐行注释：赋值或更新当前变量/字段。
    return {  # 逐行注释：返回当前逻辑的处理结果。
        "city": city,  # 逐行注释：设置当前数据项或参数。
        "district": district,  # 逐行注释：设置当前数据项或参数。
        "title": make_title(row),  # 逐行注释：设置当前数据项或参数。
        "total_price": round(unit_price * area / 10000, 2),  # 逐行注释：设置当前数据项或参数。
        "unit_price": round(unit_price),  # 逐行注释：设置当前数据项或参数。
        "area": round(area, 2),  # 逐行注释：设置当前数据项或参数。
        "rooms": rooms,  # 逐行注释：设置当前数据项或参数。
        "halls": halls,  # 逐行注释：设置当前数据项或参数。
        "floor": floor,  # 逐行注释：设置当前数据项或参数。
        "total_floors": total_floors,  # 逐行注释：设置当前数据项或参数。
        "build_year": None,  # 逐行注释：设置当前数据项或参数。
        "orientation": clean_text(row.get("chaoxiang"), limit=20),  # 逐行注释：赋值或更新当前变量/字段。
        "decoration": clean_text(row.get("zhuangxiu"), limit=20),  # 逐行注释：赋值或更新当前变量/字段。
        "has_elevator": has_elevator(total_floors, row.get("tihu")),  # 逐行注释：设置当前数据项或参数。
        "listing_type": "二手房",  # 逐行注释：设置当前数据项或参数。
        "lng": lng,  # 逐行注释：设置当前数据项或参数。
        "lat": lat,  # 逐行注释：设置当前数据项或参数。
        "source": SOURCE,  # 逐行注释：设置当前数据项或参数。
        "source_url": clean_text(row.get("link"), limit=500),  # 逐行注释：赋值或更新当前变量/字段。
    }  # 逐行注释：结束当前数据结构或调用块。


def load_rows(path):  # 逐行注释：声明函数或方法入口。
    """读取 TSV 文件并返回标准化房源、坐标统计和跳过数量。"""
    rows = []  # 逐行注释：赋值或更新当前变量/字段。
    city_points = defaultdict(list)  # 逐行注释：赋值或更新当前变量/字段。
    district_points = defaultdict(list)  # 逐行注释：赋值或更新当前变量/字段。
    skipped = 0  # 逐行注释：赋值或更新当前变量/字段。
    with path.open("r", encoding="utf-8-sig", newline="") as fh:  # 逐行注释：进入上下文管理器并自动处理资源。
        reader = csv.DictReader(fh, delimiter="\t")  # 逐行注释：赋值或更新当前变量/字段。
        for raw in reader:  # 逐行注释：遍历集合中的每一项并执行处理。
            item = normalized_row(raw)  # 逐行注释：赋值或更新当前变量/字段。
            if item is None:  # 逐行注释：根据条件判断是否进入该分支。
                skipped += 1  # 逐行注释：赋值或更新当前变量/字段。
                continue  # 逐行注释：跳过本轮循环剩余逻辑。
            rows.append(item)  # 逐行注释：执行本行代码逻辑。
            if item["lng"] is not None and item["lat"] is not None:  # 逐行注释：根据条件判断是否进入该分支。
                city_points[item["city"]].append((item["lng"], item["lat"]))  # 逐行注释：执行本行代码逻辑。
                district_points[(item["city"], item["district"])].append(  # 逐行注释：执行本行代码逻辑。
                    (item["lng"], item["lat"])  # 逐行注释：执行本行代码逻辑。
                )  # 逐行注释：结束当前数据结构或调用块。
    return rows, city_points, district_points, skipped  # 逐行注释：返回当前逻辑的处理结果。


def average_point(points):  # 逐行注释：声明函数或方法入口。
    """计算一组经纬度坐标的平均中心点。"""
    if not points:  # 逐行注释：根据条件判断是否进入该分支。
        return None, None  # 逐行注释：返回当前逻辑的处理结果。
    return (  # 逐行注释：返回当前逻辑的处理结果。
        round(sum(p[0] for p in points) / len(points), 6),  # 逐行注释：设置当前数据项或参数。
        round(sum(p[1] for p in points) / len(points), 6),  # 逐行注释：设置当前数据项或参数。
    )  # 逐行注释：结束当前数据结构或调用块。


def ensure_cities(rows, city_points):  # 逐行注释：声明函数或方法入口。
    """确保导入数据涉及的城市存在，并补全城市坐标。"""
    city_ids = {}  # 逐行注释：赋值或更新当前变量/字段。
    city_names = sorted({row["city"] for row in rows})  # 逐行注释：赋值或更新当前变量/字段。
    existing = {  # 逐行注释：赋值或更新当前变量/字段。
        city.name: city  # 逐行注释：设置当前数据项或参数。
        for city in City.query.filter(City.name.in_(city_names)).all()  # 逐行注释：遍历集合中的每一项并执行处理。
    }  # 逐行注释：结束当前数据结构或调用块。
    for name in city_names:  # 逐行注释：遍历集合中的每一项并执行处理。
        lng, lat = average_point(city_points.get(name))  # 逐行注释：赋值或更新当前变量/字段。
        city = existing.get(name)  # 逐行注释：赋值或更新当前变量/字段。
        if city is None:  # 逐行注释：根据条件判断是否进入该分支。
            city = City(name=name, province="山东", lng=lng, lat=lat)  # 逐行注释：赋值或更新当前变量/字段。
            db.session.add(city)  # 逐行注释：把对象加入数据库会话等待提交。
            db.session.flush()  # 逐行注释：执行本行代码逻辑。
        else:  # 逐行注释：处理条件不满足时的兜底分支。
            city.province = city.province or "山东"  # 逐行注释：赋值或更新当前变量/字段。
            if lng is not None:  # 逐行注释：根据条件判断是否进入该分支。
                city.lng = lng  # 逐行注释：赋值或更新当前变量/字段。
            if lat is not None:  # 逐行注释：根据条件判断是否进入该分支。
                city.lat = lat  # 逐行注释：赋值或更新当前变量/字段。
        city_ids[name] = city.id  # 逐行注释：赋值或更新当前变量/字段。
    db.session.commit()  # 逐行注释：提交当前数据库事务。
    return city_ids  # 逐行注释：返回当前逻辑的处理结果。


def ensure_districts(rows, city_ids, district_points):  # 逐行注释：声明函数或方法入口。
    """确保导入数据涉及的区域存在，并补全区域坐标和网格位置。"""
    district_ids = {}  # 逐行注释：赋值或更新当前变量/字段。
    names_by_city = defaultdict(set)  # 逐行注释：赋值或更新当前变量/字段。
    for row in rows:  # 逐行注释：遍历集合中的每一项并执行处理。
        names_by_city[city_ids[row["city"]]].add(row["district"])  # 逐行注释：执行本行代码逻辑。

    for city_id, names in names_by_city.items():  # 逐行注释：遍历集合中的每一项并执行处理。
        existing = {  # 逐行注释：赋值或更新当前变量/字段。
            district.name: district  # 逐行注释：设置当前数据项或参数。
            for district in District.query.filter(  # 逐行注释：遍历集合中的每一项并执行处理。
                District.city_id == city_id,  # 逐行注释：设置当前数据项或参数。
                District.name.in_(sorted(names)),  # 逐行注释：设置当前数据项或参数。
            ).all()  # 逐行注释：执行本行代码逻辑。
        }  # 逐行注释：结束当前数据结构或调用块。
        city_name = next(k for k, v in city_ids.items() if v == city_id)  # 逐行注释：执行本行代码逻辑。
        for index, name in enumerate(sorted(names)):  # 逐行注释：遍历集合中的每一项并执行处理。
            lng, lat = average_point(district_points.get((city_name, name)))  # 逐行注释：赋值或更新当前变量/字段。
            district = existing.get(name)  # 逐行注释：赋值或更新当前变量/字段。
            if district is None:  # 逐行注释：根据条件判断是否进入该分支。
                district = District(  # 逐行注释：赋值或更新当前变量/字段。
                    city_id=city_id,  # 逐行注释：赋值或更新当前变量/字段。
                    name=name,  # 逐行注释：赋值或更新当前变量/字段。
                    lng=lng,  # 逐行注释：赋值或更新当前变量/字段。
                    lat=lat,  # 逐行注释：赋值或更新当前变量/字段。
                    grid_x=index % 12,  # 逐行注释：赋值或更新当前变量/字段。
                    grid_y=index // 12,  # 逐行注释：赋值或更新当前变量/字段。
                )  # 逐行注释：结束当前数据结构或调用块。
                db.session.add(district)  # 逐行注释：把对象加入数据库会话等待提交。
                db.session.flush()  # 逐行注释：执行本行代码逻辑。
            else:  # 逐行注释：处理条件不满足时的兜底分支。
                if lng is not None:  # 逐行注释：根据条件判断是否进入该分支。
                    district.lng = lng  # 逐行注释：赋值或更新当前变量/字段。
                if lat is not None:  # 逐行注释：根据条件判断是否进入该分支。
                    district.lat = lat  # 逐行注释：赋值或更新当前变量/字段。
                district.grid_x = district.grid_x or index % 12  # 逐行注释：赋值或更新当前变量/字段。
                district.grid_y = district.grid_y or index // 12  # 逐行注释：赋值或更新当前变量/字段。
            district_ids[(city_name, name)] = district.id  # 逐行注释：赋值或更新当前变量/字段。
    db.session.commit()  # 逐行注释：提交当前数据库事务。
    return district_ids  # 逐行注释：返回当前逻辑的处理结果。


def insert_properties(rows, district_ids):  # 逐行注释：声明函数或方法入口。
    """批量插入去重后的山东房源记录。"""
    source_urls = [row["source_url"] for row in rows if row["source_url"]]  # 逐行注释：赋值或更新当前变量/字段。
    existing_urls = set()  # 逐行注释：赋值或更新当前变量/字段。
    for start in range(0, len(source_urls), 10000):  # 逐行注释：遍历集合中的每一项并执行处理。
        batch = source_urls[start : start + 10000]  # 逐行注释：赋值或更新当前变量/字段。
        existing_urls.update(  # 逐行注释：执行本行代码逻辑。
            url  # 逐行注释：执行本行代码逻辑。
            for (url,) in db.session.query(Property.source_url)  # 逐行注释：遍历集合中的每一项并执行处理。
            .filter(Property.source_url.in_(batch))  # 逐行注释：执行本行代码逻辑。
            .all()  # 逐行注释：执行本行代码逻辑。
        )  # 逐行注释：结束当前数据结构或调用块。

    inserted = skipped = 0  # 逐行注释：赋值或更新当前变量/字段。
    buffer = []  # 逐行注释：赋值或更新当前变量/字段。
    for row in rows:  # 逐行注释：遍历集合中的每一项并执行处理。
        if row["source_url"] and row["source_url"] in existing_urls:  # 逐行注释：根据条件判断是否进入该分支。
            skipped += 1  # 逐行注释：赋值或更新当前变量/字段。
            continue  # 逐行注释：跳过本轮循环剩余逻辑。
        data = dict(row)  # 逐行注释：赋值或更新当前变量/字段。
        city = data.pop("city")  # 逐行注释：赋值或更新当前变量/字段。
        district = data.pop("district")  # 逐行注释：赋值或更新当前变量/字段。
        data["district_id"] = district_ids[(city, district)]  # 逐行注释：赋值或更新当前变量/字段。
        buffer.append(Property(**data))  # 逐行注释：执行本行代码逻辑。
        if len(buffer) >= BATCH_SIZE:  # 逐行注释：根据条件判断是否进入该分支。
            db.session.bulk_save_objects(buffer)  # 逐行注释：执行本行代码逻辑。
            db.session.commit()  # 逐行注释：提交当前数据库事务。
            inserted += len(buffer)  # 逐行注释：赋值或更新当前变量/字段。
            print(f"inserted {inserted} properties ...")  # 逐行注释：执行本行代码逻辑。
            buffer.clear()  # 逐行注释：执行本行代码逻辑。

    if buffer:  # 逐行注释：根据条件判断是否进入该分支。
        db.session.bulk_save_objects(buffer)  # 逐行注释：执行本行代码逻辑。
        db.session.commit()  # 逐行注释：提交当前数据库事务。
        inserted += len(buffer)  # 逐行注释：赋值或更新当前变量/字段。
    return inserted, skipped  # 逐行注释：返回当前逻辑的处理结果。


def main():  # 逐行注释：声明函数或方法入口。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    parser = argparse.ArgumentParser()  # 逐行注释：赋值或更新当前变量/字段。
    parser.add_argument("--file", default=str(DEFAULT_TSV), help="house_info.tsv path")  # 逐行注释：赋值或更新当前变量/字段。
    parser.add_argument(  # 逐行注释：执行本行代码逻辑。
        "--replace",  # 逐行注释：设置当前数据项或参数。
        action="store_true",  # 逐行注释：赋值或更新当前变量/字段。
        help=f"delete existing properties with source={SOURCE!r} before import",  # 逐行注释：赋值或更新当前变量/字段。
    )  # 逐行注释：结束当前数据结构或调用块。
    args = parser.parse_args()  # 逐行注释：赋值或更新当前变量/字段。

    path = Path(args.file).expanduser().resolve()  # 逐行注释：赋值或更新当前变量/字段。
    if not path.exists():  # 逐行注释：根据条件判断是否进入该分支。
        raise SystemExit(f"TSV not found: {path}")  # 逐行注释：抛出异常并交由上层处理。

    app = create_app()  # 逐行注释：赋值或更新当前变量/字段。
    with app.app_context():  # 逐行注释：进入上下文管理器并自动处理资源。
        db.create_all()  # 逐行注释：执行本行代码逻辑。
        before = db.session.query(func.count(Property.id)).scalar()  # 逐行注释：赋值或更新当前变量/字段。
        if args.replace:  # 逐行注释：根据条件判断是否进入该分支。
            deleted = Property.query.filter_by(source=SOURCE).delete(  # 逐行注释：赋值或更新当前变量/字段。
                synchronize_session=False  # 逐行注释：赋值或更新当前变量/字段。
            )  # 逐行注释：结束当前数据结构或调用块。
            db.session.commit()  # 逐行注释：提交当前数据库事务。
            print(f"deleted existing {SOURCE} properties: {deleted}")  # 逐行注释：设置当前数据项或参数。

        rows, city_points, district_points, invalid = load_rows(path)  # 逐行注释：赋值或更新当前变量/字段。
        print(f"loaded valid rows: {len(rows)}, skipped invalid rows: {invalid}")  # 逐行注释：设置当前数据项或参数。
        city_ids = ensure_cities(rows, city_points)  # 逐行注释：赋值或更新当前变量/字段。
        district_ids = ensure_districts(rows, city_ids, district_points)  # 逐行注释：赋值或更新当前变量/字段。
        inserted, duplicate = insert_properties(rows, district_ids)  # 逐行注释：赋值或更新当前变量/字段。
        after = db.session.query(func.count(Property.id)).scalar()  # 逐行注释：赋值或更新当前变量/字段。

    print(f"cities touched: {len(city_ids)}")  # 逐行注释：设置当前数据项或参数。
    print(f"districts touched: {len(district_ids)}")  # 逐行注释：设置当前数据项或参数。
    print(f"properties before: {before}")  # 逐行注释：设置当前数据项或参数。
    print(f"properties inserted: {inserted}")  # 逐行注释：设置当前数据项或参数。
    print(f"properties skipped duplicate: {duplicate}")  # 逐行注释：设置当前数据项或参数。
    print(f"properties after: {after}")  # 逐行注释：设置当前数据项或参数。


if __name__ == "__main__":  # 逐行注释：根据条件判断是否进入该分支。
    main()  # 逐行注释：执行本行代码逻辑。
