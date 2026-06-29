"""Seed the database with realistic **synthetic** housing data.

Run with:  flask --app app seed     (or)     python seed.py

All data here is generated, not scraped — see ``spider/__init__.py`` for the
data-collection scaffold and its compliance notes.
"""
import random  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from datetime import date  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import City, District, Facility, PriceHistory, Property  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

random.seed(42)  # reproducible output

# 城市 -> 中心经纬度、省份、各行政区基准单价（元/㎡）
CITY_DATA = {  # 初始化CITY_DATA中间数据字典，用于承载接口返回或中间聚合结果。
    "北京": {  # 把北京字段写入响应数据，供前端页面、图表或后续接口读取。
        "province": "北京市", "lng": 116.40, "lat": 39.90,  # 把province字段写入响应数据，供前端页面、图表或后续接口读取。
        "districts": {  # 把districts字段写入响应数据，供前端页面、图表或后续接口读取。
            "西城区": 130000, "东城区": 115000, "海淀区": 98000, "朝阳区": 85000,  # 把西城区字段写入响应数据，供前端页面、图表或后续接口读取。
            "丰台区": 62000, "石景山区": 55000, "通州区": 48000, "昌平区": 42000,  # 把丰台区字段写入响应数据，供前端页面、图表或后续接口读取。
        },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    "上海": {  # 把上海字段写入响应数据，供前端页面、图表或后续接口读取。
        "province": "上海市", "lng": 121.47, "lat": 31.23,  # 把province字段写入响应数据，供前端页面、图表或后续接口读取。
        "districts": {  # 把districts字段写入响应数据，供前端页面、图表或后续接口读取。
            "黄浦区": 120000, "静安区": 110000, "徐汇区": 105000, "长宁区": 95000,  # 把黄浦区字段写入响应数据，供前端页面、图表或后续接口读取。
            "浦东新区": 78000, "杨浦区": 72000, "闵行区": 58000, "宝山区": 48000,  # 把浦东新区字段写入响应数据，供前端页面、图表或后续接口读取。
        },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    "广州": {  # 把广州字段写入响应数据，供前端页面、图表或后续接口读取。
        "province": "广东省", "lng": 113.26, "lat": 23.13,  # 把province字段写入响应数据，供前端页面、图表或后续接口读取。
        "districts": {  # 把districts字段写入响应数据，供前端页面、图表或后续接口读取。
            "天河区": 68000, "越秀区": 62000, "海珠区": 55000, "荔湾区": 48000,  # 把天河区字段写入响应数据，供前端页面、图表或后续接口读取。
            "黄埔区": 40000, "白云区": 38000, "番禺区": 35000,  # 把黄埔区字段写入响应数据，供前端页面、图表或后续接口读取。
        },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    "深圳": {  # 把深圳字段写入响应数据，供前端页面、图表或后续接口读取。
        "province": "广东省", "lng": 114.06, "lat": 22.54,  # 把province字段写入响应数据，供前端页面、图表或后续接口读取。
        "districts": {  # 把districts字段写入响应数据，供前端页面、图表或后续接口读取。
            "南山区": 115000, "福田区": 105000, "罗湖区": 72000, "宝安区": 65000,  # 把南山区字段写入响应数据，供前端页面、图表或后续接口读取。
            "龙华区": 60000, "龙岗区": 52000,  # 把龙华区字段写入响应数据，供前端页面、图表或后续接口读取。
        },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    "杭州": {  # 把杭州字段写入响应数据，供前端页面、图表或后续接口读取。
        "province": "浙江省", "lng": 120.15, "lat": 30.27,  # 把province字段写入响应数据，供前端页面、图表或后续接口读取。
        "districts": {  # 把districts字段写入响应数据，供前端页面、图表或后续接口读取。
            "上城区": 58000, "西湖区": 55000, "滨江区": 52000, "拱墅区": 42000,  # 把上城区字段写入响应数据，供前端页面、图表或后续接口读取。
            "余杭区": 35000, "萧山区": 30000,  # 把余杭区字段写入响应数据，供前端页面、图表或后续接口读取。
        },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    "成都": {  # 把成都字段写入响应数据，供前端页面、图表或后续接口读取。
        "province": "四川省", "lng": 104.07, "lat": 30.57,  # 把province字段写入响应数据，供前端页面、图表或后续接口读取。
        "districts": {  # 把districts字段写入响应数据，供前端页面、图表或后续接口读取。
            "高新区": 30000, "锦江区": 28000, "青羊区": 27000, "武侯区": 26000,  # 把高新区字段写入响应数据，供前端页面、图表或后续接口读取。
            "成华区": 22000, "天府新区": 24000, "金牛区": 20000,  # 把成华区字段写入响应数据，供前端页面、图表或后续接口读取。
        },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
}  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

ORIENTATIONS = ["南", "南北", "东南", "东", "西南", "北"]  # 初始化ORIENTATIONS中间数据列表，用于收集清洗后的多条业务数据。
DECORATIONS = ["毛坯", "简装", "精装", "豪装"]  # 初始化DECORATIONS中间数据列表，用于收集清洗后的多条业务数据。
FEATURES = ["满五唯一", "近地铁", "南北通透", "优质学区", "精装修", "低总价", "采光极佳", "业主诚售"]  # 初始化FEATURES中间数据列表，用于收集清洗后的多条业务数据。
ROOM_AREA = {1: (38, 60), 2: (65, 95), 3: (95, 140), 4: (140, 200)}  # 初始化ROOM_AREA中间数据字典，用于承载接口返回或中间聚合结果。
ROOM_WEIGHTS = [(1, 0.18), (2, 0.42), (3, 0.30), (4, 0.10)]  # 初始化ROOM_WEIGHTS中间数据列表，用于收集清洗后的多条业务数据。


def _weighted_rooms() -> int:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """按权重随机生成更接近真实分布的户型室数。"""
    r = random.random()  # 计算或更新r中间数据，作为后续业务判断、统计或响应组装的输入。
    cum = 0.0  # 计算或更新cum中间数据，作为后续业务判断、统计或响应组装的输入。
    for rooms, w in ROOM_WEIGHTS:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        cum += w  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        if r <= cum:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            return rooms  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return 2  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _last_n_months(n: int) -> list[str]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """生成从当前月份向前追溯的月份序列。"""
    today = date.today()  # 计算或更新today中间数据，作为后续业务判断、统计或响应组装的输入。
    y, m, out = today.year, today.month, []  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    for _ in range(n):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        out.append(f"{y:04d}-{m:02d}")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        m -= 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        if m == 0:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            m, y = 12, y - 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return list(reversed(out))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _make_properties(district: District, base_price: int, n: int) -> list[Property]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """为指定区域批量生成模拟房源数据。"""
    props = []  # 初始化props中间数据列表，用于收集清洗后的多条业务数据。
    for _ in range(n):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        rooms = _weighted_rooms()  # 计算或更新rooms中间数据，作为后续业务判断、统计或响应组装的输入。
        lo, hi = ROOM_AREA[rooms]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        area = round(random.uniform(lo, hi), 1)  # 计算或更新area中间数据，作为后续业务判断、统计或响应组装的输入。
        unit_price = max(8000, round(random.gauss(base_price, base_price * 0.12)))  # 计算或更新unit_price中间数据，作为后续业务判断、统计或响应组装的输入。
        total_price = round(unit_price * area / 10000, 1)  # 万元
        total_floors = random.choice([6, 11, 18, 26, 33])  # 计算或更新total_floors中间数据，作为后续业务判断、统计或响应组装的输入。
        has_elevator = total_floors > 6 or random.random() > 0.5  # 计算或更新has_elevator中间数据，作为后续业务判断、统计或响应组装的输入。
        decoration = random.choice(DECORATIONS)  # 计算或更新decoration中间数据，作为后续业务判断、统计或响应组装的输入。
        props.append(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            Property(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                district_id=district.id,  # 计算或更新行政区编号，作为后续业务判断、统计或响应组装的输入。
                title=f"{district.name}{decoration}{rooms}居 {random.choice(FEATURES)}",  # 计算或更新title中间数据，作为后续业务判断、统计或响应组装的输入。
                total_price=total_price,  # 计算或更新total_price中间数据，作为后续业务判断、统计或响应组装的输入。
                unit_price=unit_price,  # 计算或更新unit_price中间数据，作为后续业务判断、统计或响应组装的输入。
                area=area,  # 计算或更新area中间数据，作为后续业务判断、统计或响应组装的输入。
                rooms=rooms,  # 计算或更新rooms中间数据，作为后续业务判断、统计或响应组装的输入。
                halls=1 if rooms <= 1 else 2,  # 计算或更新halls中间数据，作为后续业务判断、统计或响应组装的输入。
                floor=random.randint(1, total_floors),  # 计算或更新floor中间数据，作为后续业务判断、统计或响应组装的输入。
                total_floors=total_floors,  # 计算或更新total_floors中间数据，作为后续业务判断、统计或响应组装的输入。
                build_year=random.randint(1998, 2023),  # 计算或更新build_year中间数据，作为后续业务判断、统计或响应组装的输入。
                orientation=random.choice(ORIENTATIONS),  # 计算或更新orientation中间数据，作为后续业务判断、统计或响应组装的输入。
                decoration=decoration,  # 计算或更新decoration中间数据，作为后续业务判断、统计或响应组装的输入。
                has_elevator=has_elevator,  # 计算或更新has_elevator中间数据，作为后续业务判断、统计或响应组装的输入。
                listing_type="二手房",  # 计算或更新listing_type中间数据，作为后续业务判断、统计或响应组装的输入。
                lng=round((district.lng or 0) + random.uniform(-0.03, 0.03), 5),  # 计算或更新lng中间数据，作为后续业务判断、统计或响应组装的输入。
                lat=round((district.lat or 0) + random.uniform(-0.03, 0.03), 5),  # 计算或更新lat中间数据，作为后续业务判断、统计或响应组装的输入。
                source="seed",  # 计算或更新source中间数据，作为后续业务判断、统计或响应组装的输入。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return props  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _make_facilities(district: District) -> list[Facility]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """为指定区域生成周边配套设施模拟数据。"""
    base_lng, base_lat = district.lng or 0, district.lat or 0  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    specs = [  # 初始化specs中间数据列表，用于收集清洗后的多条业务数据。
        (f"{district.name}实验小学", "school"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        (f"{district.name}第二中学", "school"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        (f"{district.name}人民医院", "hospital"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        (f"地铁{random.randint(1, 16)}号线 · {district.name}站", "subway"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        (f"{district.name}万象汇", "mall"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        (f"{district.name}中央公园", "park"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return [  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        Facility(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            district_id=district.id, name=name, category=cat,  # 计算或更新行政区编号，作为后续业务判断、统计或响应组装的输入。
            lng=round(base_lng + random.uniform(-0.02, 0.02), 5),  # 计算或更新lng中间数据，作为后续业务判断、统计或响应组装的输入。
            lat=round(base_lat + random.uniform(-0.02, 0.02), 5),  # 计算或更新lat中间数据，作为后续业务判断、统计或响应组装的输入。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        for name, cat in specs  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def _make_price_history(district: District, base_price: int) -> list[PriceHistory]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """为指定区域生成近期房价历史模拟数据。"""
    months = _last_n_months(24)  # 计算或更新months中间数据，作为后续业务判断、统计或响应组装的输入。
    # Start a bit below today's level and drift upward with mild noise.
    price = base_price * random.uniform(0.85, 0.93)  # 计算或更新price中间数据，作为后续业务判断、统计或响应组装的输入。
    target_step = (base_price - price) / len(months)  # 计算或更新target_step中间数据，作为后续业务判断、统计或响应组装的输入。
    rows = []  # 初始化查询结果集合列表，用于收集清洗后的多条业务数据。
    for month in months:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        price += target_step * random.uniform(0.4, 1.6)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        rows.append(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            PriceHistory(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                district_id=district.id, month=month, avg_unit_price=round(price)  # 计算或更新行政区编号，作为后续业务判断、统计或响应组装的输入。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return rows  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def run_seed(app) -> None:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """清空并重建样例城市、区域、房源、设施和价格历史数据。"""
    with app.app_context():  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
        print("→ 重建数据表 ...")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        db.drop_all()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        db.create_all()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        n_cities = n_districts = n_props = n_facils = n_hist = 0  # 计算或更新n_cities中间数据，作为后续业务判断、统计或响应组装的输入。
        for city_name, info in CITY_DATA.items():  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            city = City(  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
                name=city_name, name_en="", province=info["province"],  # 计算或更新name中间数据，作为后续业务判断、统计或响应组装的输入。
                lng=info["lng"], lat=info["lat"],  # 计算或更新lng中间数据，作为后续业务判断、统计或响应组装的输入。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            db.session.add(city)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            db.session.flush()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            n_cities += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

            districts = list(info["districts"].items())  # 计算或更新行政区集合，作为后续业务判断、统计或响应组装的输入。
            cols = int(len(districts) ** 0.5) + 1  # 计算或更新cols中间数据，作为后续业务判断、统计或响应组装的输入。
            for idx, (dname, base_price) in enumerate(districts):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
                district = District(  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
                    city_id=city.id, name=dname,  # 计算或更新城市编号，作为后续业务判断、统计或响应组装的输入。
                    lng=round(info["lng"] + random.uniform(-0.08, 0.08), 5),  # 计算或更新lng中间数据，作为后续业务判断、统计或响应组装的输入。
                    lat=round(info["lat"] + random.uniform(-0.08, 0.08), 5),  # 计算或更新lat中间数据，作为后续业务判断、统计或响应组装的输入。
                    grid_x=idx % cols, grid_y=idx // cols,  # 计算或更新grid_x中间数据，作为后续业务判断、统计或响应组装的输入。
                )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
                db.session.add(district)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
                db.session.flush()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
                n_districts += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

                props = _make_properties(district, base_price, random.randint(22, 36))  # 计算或更新props中间数据，作为后续业务判断、统计或响应组装的输入。
                facils = _make_facilities(district)  # 计算或更新facils中间数据，作为后续业务判断、统计或响应组装的输入。
                hist = _make_price_history(district, base_price)  # 计算或更新hist中间数据，作为后续业务判断、统计或响应组装的输入。
                db.session.add_all(props + facils + hist)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
                n_props += len(props)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                n_facils += len(facils)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                n_hist += len(hist)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
        print(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            f"✓ 完成：{n_cities} 城市 / {n_districts} 行政区 / "  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            f"{n_props} 房源 / {n_facils} 设施 / {n_hist} 条价格走势。"  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


if __name__ == "__main__":  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    from app import app  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

    run_seed(app)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
