"""Seed the database with realistic **synthetic** housing data.

Run with:  flask --app app seed     (or)     python seed.py

All data here is generated, not scraped — see ``spider/__init__.py`` for the
data-collection scaffold and its compliance notes.
"""
import random  # 导入本行所需的模块或对象。
from datetime import date  # 导入本行所需的模块或对象。

from extensions import db  # 导入本行所需的模块或对象。
from models import City, District, Facility, PriceHistory, Property  # 导入本行所需的模块或对象。

random.seed(42)  # reproducible output

# 城市 -> 中心经纬度、省份、各行政区基准单价（元/㎡）
CITY_DATA = {  # 赋值或更新当前变量/字段。
    "北京": {  # 设置当前数据项或参数。
        "province": "北京市", "lng": 116.40, "lat": 39.90,  # 设置当前数据项或参数。
        "districts": {  # 设置当前数据项或参数。
            "西城区": 130000, "东城区": 115000, "海淀区": 98000, "朝阳区": 85000,  # 设置当前数据项或参数。
            "丰台区": 62000, "石景山区": 55000, "通州区": 48000, "昌平区": 42000,  # 设置当前数据项或参数。
        },  # 结束当前数据结构或调用块。
    },  # 结束当前数据结构或调用块。
    "上海": {  # 设置当前数据项或参数。
        "province": "上海市", "lng": 121.47, "lat": 31.23,  # 设置当前数据项或参数。
        "districts": {  # 设置当前数据项或参数。
            "黄浦区": 120000, "静安区": 110000, "徐汇区": 105000, "长宁区": 95000,  # 设置当前数据项或参数。
            "浦东新区": 78000, "杨浦区": 72000, "闵行区": 58000, "宝山区": 48000,  # 设置当前数据项或参数。
        },  # 结束当前数据结构或调用块。
    },  # 结束当前数据结构或调用块。
    "广州": {  # 设置当前数据项或参数。
        "province": "广东省", "lng": 113.26, "lat": 23.13,  # 设置当前数据项或参数。
        "districts": {  # 设置当前数据项或参数。
            "天河区": 68000, "越秀区": 62000, "海珠区": 55000, "荔湾区": 48000,  # 设置当前数据项或参数。
            "黄埔区": 40000, "白云区": 38000, "番禺区": 35000,  # 设置当前数据项或参数。
        },  # 结束当前数据结构或调用块。
    },  # 结束当前数据结构或调用块。
    "深圳": {  # 设置当前数据项或参数。
        "province": "广东省", "lng": 114.06, "lat": 22.54,  # 设置当前数据项或参数。
        "districts": {  # 设置当前数据项或参数。
            "南山区": 115000, "福田区": 105000, "罗湖区": 72000, "宝安区": 65000,  # 设置当前数据项或参数。
            "龙华区": 60000, "龙岗区": 52000,  # 设置当前数据项或参数。
        },  # 结束当前数据结构或调用块。
    },  # 结束当前数据结构或调用块。
    "杭州": {  # 设置当前数据项或参数。
        "province": "浙江省", "lng": 120.15, "lat": 30.27,  # 设置当前数据项或参数。
        "districts": {  # 设置当前数据项或参数。
            "上城区": 58000, "西湖区": 55000, "滨江区": 52000, "拱墅区": 42000,  # 设置当前数据项或参数。
            "余杭区": 35000, "萧山区": 30000,  # 设置当前数据项或参数。
        },  # 结束当前数据结构或调用块。
    },  # 结束当前数据结构或调用块。
    "成都": {  # 设置当前数据项或参数。
        "province": "四川省", "lng": 104.07, "lat": 30.57,  # 设置当前数据项或参数。
        "districts": {  # 设置当前数据项或参数。
            "高新区": 30000, "锦江区": 28000, "青羊区": 27000, "武侯区": 26000,  # 设置当前数据项或参数。
            "成华区": 22000, "天府新区": 24000, "金牛区": 20000,  # 设置当前数据项或参数。
        },  # 结束当前数据结构或调用块。
    },  # 结束当前数据结构或调用块。
}  # 结束当前数据结构或调用块。

ORIENTATIONS = ["南", "南北", "东南", "东", "西南", "北"]  # 赋值或更新当前变量/字段。
DECORATIONS = ["毛坯", "简装", "精装", "豪装"]  # 赋值或更新当前变量/字段。
FEATURES = ["满五唯一", "近地铁", "南北通透", "优质学区", "精装修", "低总价", "采光极佳", "业主诚售"]  # 赋值或更新当前变量/字段。
ROOM_AREA = {1: (38, 60), 2: (65, 95), 3: (95, 140), 4: (140, 200)}  # 赋值或更新当前变量/字段。
ROOM_WEIGHTS = [(1, 0.18), (2, 0.42), (3, 0.30), (4, 0.10)]  # 赋值或更新当前变量/字段。


def _weighted_rooms() -> int:  # 声明函数或方法入口。
    """按权重随机生成更接近真实分布的户型室数。"""
    r = random.random()  # 赋值或更新当前变量/字段。
    cum = 0.0  # 赋值或更新当前变量/字段。
    for rooms, w in ROOM_WEIGHTS:  # 遍历集合中的每一项并执行处理。
        cum += w  # 赋值或更新当前变量/字段。
        if r <= cum:  # 根据条件判断是否进入该分支。
            return rooms  # 返回当前逻辑的处理结果。
    return 2  # 返回当前逻辑的处理结果。


def _last_n_months(n: int) -> list[str]:  # 声明函数或方法入口。
    """生成从当前月份向前追溯的月份序列。"""
    today = date.today()  # 赋值或更新当前变量/字段。
    y, m, out = today.year, today.month, []  # 赋值或更新当前变量/字段。
    for _ in range(n):  # 遍历集合中的每一项并执行处理。
        out.append(f"{y:04d}-{m:02d}")  # 设置当前数据项或参数。
        m -= 1  # 赋值或更新当前变量/字段。
        if m == 0:  # 根据条件判断是否进入该分支。
            m, y = 12, y - 1  # 赋值或更新当前变量/字段。
    return list(reversed(out))  # 返回当前逻辑的处理结果。


def _make_properties(district: District, base_price: int, n: int) -> list[Property]:  # 声明函数或方法入口。
    """为指定区域批量生成模拟房源数据。"""
    props = []  # 赋值或更新当前变量/字段。
    for _ in range(n):  # 遍历集合中的每一项并执行处理。
        rooms = _weighted_rooms()  # 赋值或更新当前变量/字段。
        lo, hi = ROOM_AREA[rooms]  # 赋值或更新当前变量/字段。
        area = round(random.uniform(lo, hi), 1)  # 赋值或更新当前变量/字段。
        unit_price = max(8000, round(random.gauss(base_price, base_price * 0.12)))  # 赋值或更新当前变量/字段。
        total_price = round(unit_price * area / 10000, 1)  # 万元
        total_floors = random.choice([6, 11, 18, 26, 33])  # 赋值或更新当前变量/字段。
        has_elevator = total_floors > 6 or random.random() > 0.5  # 赋值或更新当前变量/字段。
        decoration = random.choice(DECORATIONS)  # 赋值或更新当前变量/字段。
        props.append(  # 执行本行代码逻辑。
            Property(  # 执行本行代码逻辑。
                district_id=district.id,  # 赋值或更新当前变量/字段。
                title=f"{district.name}{decoration}{rooms}居 {random.choice(FEATURES)}",  # 赋值或更新当前变量/字段。
                total_price=total_price,  # 赋值或更新当前变量/字段。
                unit_price=unit_price,  # 赋值或更新当前变量/字段。
                area=area,  # 赋值或更新当前变量/字段。
                rooms=rooms,  # 赋值或更新当前变量/字段。
                halls=1 if rooms <= 1 else 2,  # 设置当前数据项或参数。
                floor=random.randint(1, total_floors),  # 赋值或更新当前变量/字段。
                total_floors=total_floors,  # 赋值或更新当前变量/字段。
                build_year=random.randint(1998, 2023),  # 赋值或更新当前变量/字段。
                orientation=random.choice(ORIENTATIONS),  # 赋值或更新当前变量/字段。
                decoration=decoration,  # 赋值或更新当前变量/字段。
                has_elevator=has_elevator,  # 赋值或更新当前变量/字段。
                listing_type="二手房",  # 赋值或更新当前变量/字段。
                lng=round((district.lng or 0) + random.uniform(-0.03, 0.03), 5),  # 赋值或更新当前变量/字段。
                lat=round((district.lat or 0) + random.uniform(-0.03, 0.03), 5),  # 赋值或更新当前变量/字段。
                source="seed",  # 赋值或更新当前变量/字段。
            )  # 结束当前数据结构或调用块。
        )  # 结束当前数据结构或调用块。
    return props  # 返回当前逻辑的处理结果。


def _make_facilities(district: District) -> list[Facility]:  # 声明函数或方法入口。
    """为指定区域生成周边配套设施模拟数据。"""
    base_lng, base_lat = district.lng or 0, district.lat or 0  # 赋值或更新当前变量/字段。
    specs = [  # 赋值或更新当前变量/字段。
        (f"{district.name}实验小学", "school"),  # 设置当前数据项或参数。
        (f"{district.name}第二中学", "school"),  # 设置当前数据项或参数。
        (f"{district.name}人民医院", "hospital"),  # 设置当前数据项或参数。
        (f"地铁{random.randint(1, 16)}号线 · {district.name}站", "subway"),  # 设置当前数据项或参数。
        (f"{district.name}万象汇", "mall"),  # 设置当前数据项或参数。
        (f"{district.name}中央公园", "park"),  # 设置当前数据项或参数。
    ]  # 结束当前数据结构或调用块。
    return [  # 返回当前逻辑的处理结果。
        Facility(  # 执行本行代码逻辑。
            district_id=district.id, name=name, category=cat,  # 赋值或更新当前变量/字段。
            lng=round(base_lng + random.uniform(-0.02, 0.02), 5),  # 赋值或更新当前变量/字段。
            lat=round(base_lat + random.uniform(-0.02, 0.02), 5),  # 赋值或更新当前变量/字段。
        )  # 结束当前数据结构或调用块。
        for name, cat in specs  # 遍历集合中的每一项并执行处理。
    ]  # 结束当前数据结构或调用块。


def _make_price_history(district: District, base_price: int) -> list[PriceHistory]:  # 声明函数或方法入口。
    """为指定区域生成近期房价历史模拟数据。"""
    months = _last_n_months(24)  # 赋值或更新当前变量/字段。
    # Start a bit below today's level and drift upward with mild noise.
    price = base_price * random.uniform(0.85, 0.93)  # 赋值或更新当前变量/字段。
    target_step = (base_price - price) / len(months)  # 赋值或更新当前变量/字段。
    rows = []  # 赋值或更新当前变量/字段。
    for month in months:  # 遍历集合中的每一项并执行处理。
        price += target_step * random.uniform(0.4, 1.6)  # 赋值或更新当前变量/字段。
        rows.append(  # 执行本行代码逻辑。
            PriceHistory(  # 执行本行代码逻辑。
                district_id=district.id, month=month, avg_unit_price=round(price)  # 赋值或更新当前变量/字段。
            )  # 结束当前数据结构或调用块。
        )  # 结束当前数据结构或调用块。
    return rows  # 返回当前逻辑的处理结果。


def run_seed(app) -> None:  # 声明函数或方法入口。
    """清空并重建样例城市、区域、房源、设施和价格历史数据。"""
    with app.app_context():  # 进入上下文管理器并自动处理资源。
        print("→ 重建数据表 ...")  # 执行本行代码逻辑。
        db.drop_all()  # 执行本行代码逻辑。
        db.create_all()  # 执行本行代码逻辑。

        n_cities = n_districts = n_props = n_facils = n_hist = 0  # 赋值或更新当前变量/字段。
        for city_name, info in CITY_DATA.items():  # 遍历集合中的每一项并执行处理。
            city = City(  # 赋值或更新当前变量/字段。
                name=city_name, name_en="", province=info["province"],  # 赋值或更新当前变量/字段。
                lng=info["lng"], lat=info["lat"],  # 赋值或更新当前变量/字段。
            )  # 结束当前数据结构或调用块。
            db.session.add(city)  # 把对象加入数据库会话等待提交。
            db.session.flush()  # 执行本行代码逻辑。
            n_cities += 1  # 赋值或更新当前变量/字段。

            districts = list(info["districts"].items())  # 赋值或更新当前变量/字段。
            cols = int(len(districts) ** 0.5) + 1  # 赋值或更新当前变量/字段。
            for idx, (dname, base_price) in enumerate(districts):  # 遍历集合中的每一项并执行处理。
                district = District(  # 赋值或更新当前变量/字段。
                    city_id=city.id, name=dname,  # 赋值或更新当前变量/字段。
                    lng=round(info["lng"] + random.uniform(-0.08, 0.08), 5),  # 赋值或更新当前变量/字段。
                    lat=round(info["lat"] + random.uniform(-0.08, 0.08), 5),  # 赋值或更新当前变量/字段。
                    grid_x=idx % cols, grid_y=idx // cols,  # 赋值或更新当前变量/字段。
                )  # 结束当前数据结构或调用块。
                db.session.add(district)  # 把对象加入数据库会话等待提交。
                db.session.flush()  # 执行本行代码逻辑。
                n_districts += 1  # 赋值或更新当前变量/字段。

                props = _make_properties(district, base_price, random.randint(22, 36))  # 赋值或更新当前变量/字段。
                facils = _make_facilities(district)  # 赋值或更新当前变量/字段。
                hist = _make_price_history(district, base_price)  # 赋值或更新当前变量/字段。
                db.session.add_all(props + facils + hist)  # 把对象加入数据库会话等待提交。
                n_props += len(props)  # 赋值或更新当前变量/字段。
                n_facils += len(facils)  # 赋值或更新当前变量/字段。
                n_hist += len(hist)  # 赋值或更新当前变量/字段。

        db.session.commit()  # 提交当前数据库事务。
        print(  # 执行本行代码逻辑。
            f"✓ 完成：{n_cities} 城市 / {n_districts} 行政区 / "  # 执行本行代码逻辑。
            f"{n_props} 房源 / {n_facils} 设施 / {n_hist} 条价格走势。"  # 执行本行代码逻辑。
        )  # 结束当前数据结构或调用块。


if __name__ == "__main__":  # 根据条件判断是否进入该分支。
    from app import app  # 导入本行所需的模块或对象。

    run_seed(app)  # 执行本行代码逻辑。
