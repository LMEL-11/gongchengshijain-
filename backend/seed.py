"""Seed the database with realistic **synthetic** housing data.

Run with:  flask --app app seed     (or)     python seed.py

All data here is generated, not scraped — see ``spider/__init__.py`` for the
data-collection scaffold and its compliance notes.
"""
import random  # 导入 random 模块，为当前文件提供所需功能。
from datetime import date  # 从 datetime 导入 date，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import City, District, Facility, PriceHistory, Property  # 从 models 导入 City, District, Facility, PriceHistory, Property，供本文件后续逻辑调用。

random.seed(42)  # 执行当前代码行对应的业务处理步骤。

# 城市 -> 中心经纬度、省份、各行政区基准单价（元/㎡）
CITY_DATA = {  # 设置 CITY_DATA 的值，供后续业务判断、查询或响应组装使用。
    "北京": {  # 保留字符串内容，作为说明文本或页面展示文案。
        "province": "北京市", "lng": 116.40, "lat": 39.90,  # 保留字符串内容，作为说明文本或页面展示文案。
        "districts": {  # 保留字符串内容，作为说明文本或页面展示文案。
            "西城区": 130000, "东城区": 115000, "海淀区": 98000, "朝阳区": 85000,  # 保留字符串内容，作为说明文本或页面展示文案。
            "丰台区": 62000, "石景山区": 55000, "通州区": 48000, "昌平区": 42000,  # 保留字符串内容，作为说明文本或页面展示文案。
        },  # 结束当前多行数据结构或函数调用。
    },  # 结束当前多行数据结构或函数调用。
    "上海": {  # 保留字符串内容，作为说明文本或页面展示文案。
        "province": "上海市", "lng": 121.47, "lat": 31.23,  # 保留字符串内容，作为说明文本或页面展示文案。
        "districts": {  # 保留字符串内容，作为说明文本或页面展示文案。
            "黄浦区": 120000, "静安区": 110000, "徐汇区": 105000, "长宁区": 95000,  # 保留字符串内容，作为说明文本或页面展示文案。
            "浦东新区": 78000, "杨浦区": 72000, "闵行区": 58000, "宝山区": 48000,  # 保留字符串内容，作为说明文本或页面展示文案。
        },  # 结束当前多行数据结构或函数调用。
    },  # 结束当前多行数据结构或函数调用。
    "广州": {  # 保留字符串内容，作为说明文本或页面展示文案。
        "province": "广东省", "lng": 113.26, "lat": 23.13,  # 保留字符串内容，作为说明文本或页面展示文案。
        "districts": {  # 保留字符串内容，作为说明文本或页面展示文案。
            "天河区": 68000, "越秀区": 62000, "海珠区": 55000, "荔湾区": 48000,  # 保留字符串内容，作为说明文本或页面展示文案。
            "黄埔区": 40000, "白云区": 38000, "番禺区": 35000,  # 保留字符串内容，作为说明文本或页面展示文案。
        },  # 结束当前多行数据结构或函数调用。
    },  # 结束当前多行数据结构或函数调用。
    "深圳": {  # 保留字符串内容，作为说明文本或页面展示文案。
        "province": "广东省", "lng": 114.06, "lat": 22.54,  # 保留字符串内容，作为说明文本或页面展示文案。
        "districts": {  # 保留字符串内容，作为说明文本或页面展示文案。
            "南山区": 115000, "福田区": 105000, "罗湖区": 72000, "宝安区": 65000,  # 保留字符串内容，作为说明文本或页面展示文案。
            "龙华区": 60000, "龙岗区": 52000,  # 保留字符串内容，作为说明文本或页面展示文案。
        },  # 结束当前多行数据结构或函数调用。
    },  # 结束当前多行数据结构或函数调用。
    "杭州": {  # 保留字符串内容，作为说明文本或页面展示文案。
        "province": "浙江省", "lng": 120.15, "lat": 30.27,  # 保留字符串内容，作为说明文本或页面展示文案。
        "districts": {  # 保留字符串内容，作为说明文本或页面展示文案。
            "上城区": 58000, "西湖区": 55000, "滨江区": 52000, "拱墅区": 42000,  # 保留字符串内容，作为说明文本或页面展示文案。
            "余杭区": 35000, "萧山区": 30000,  # 保留字符串内容，作为说明文本或页面展示文案。
        },  # 结束当前多行数据结构或函数调用。
    },  # 结束当前多行数据结构或函数调用。
    "成都": {  # 保留字符串内容，作为说明文本或页面展示文案。
        "province": "四川省", "lng": 104.07, "lat": 30.57,  # 保留字符串内容，作为说明文本或页面展示文案。
        "districts": {  # 保留字符串内容，作为说明文本或页面展示文案。
            "高新区": 30000, "锦江区": 28000, "青羊区": 27000, "武侯区": 26000,  # 保留字符串内容，作为说明文本或页面展示文案。
            "成华区": 22000, "天府新区": 24000, "金牛区": 20000,  # 保留字符串内容，作为说明文本或页面展示文案。
        },  # 结束当前多行数据结构或函数调用。
    },  # 结束当前多行数据结构或函数调用。
}  # 结束当前多行数据结构或函数调用。

ORIENTATIONS = ["南", "南北", "东南", "东", "西南", "北"]  # 设置 ORIENTATIONS 的值，供后续业务判断、查询或响应组装使用。
DECORATIONS = ["毛坯", "简装", "精装", "豪装"]  # 设置 DECORATIONS 的值，供后续业务判断、查询或响应组装使用。
FEATURES = ["满五唯一", "近地铁", "南北通透", "优质学区", "精装修", "低总价", "采光极佳", "业主诚售"]  # 设置 FEATURES 的值，供后续业务判断、查询或响应组装使用。
ROOM_AREA = {1: (38, 60), 2: (65, 95), 3: (95, 140), 4: (140, 200)}  # 设置 ROOM_AREA 的值，供后续业务判断、查询或响应组装使用。
ROOM_WEIGHTS = [(1, 0.18), (2, 0.42), (3, 0.30), (4, 0.10)]  # 设置 ROOM_WEIGHTS 的值，供后续业务判断、查询或响应组装使用。


def _weighted_rooms() -> int:  # 定义 _weighted_rooms 函数，集中处理这一段业务逻辑。
    """按权重随机生成更接近真实分布的户型室数。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    r = random.random()  # 设置 r 的值，供后续业务判断、查询或响应组装使用。
    cum = 0.0  # 设置 cum 的值，供后续业务判断、查询或响应组装使用。
    for rooms, w in ROOM_WEIGHTS:  # 遍历当前数据集合，逐项完成处理。
        cum += w  # 设置 cum + 的值，供后续业务判断、查询或响应组装使用。
        if r <= cum:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            return rooms  # 返回处理后的结果给调用方继续使用。
    return 2  # 返回处理后的结果给调用方继续使用。


def _last_n_months(n: int) -> list[str]:  # 定义 _last_n_months 函数，集中处理这一段业务逻辑。
    """生成从当前月份向前追溯的月份序列。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    today = date.today()  # 设置 today 的值，供后续业务判断、查询或响应组装使用。
    y, m, out = today.year, today.month, []  # 设置 y, m, out 的值，供后续业务判断、查询或响应组装使用。
    for _ in range(n):  # 遍历当前数据集合，逐项完成处理。
        out.append(f"{y:04d}-{m:02d}")  # 执行当前代码行对应的业务处理步骤。
        m -= 1  # 设置 m - 的值，供后续业务判断、查询或响应组装使用。
        if m == 0:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            m, y = 12, y - 1  # 设置 m, y 的值，供后续业务判断、查询或响应组装使用。
    return list(reversed(out))  # 返回处理后的结果给调用方继续使用。


def _make_properties(district: District, base_price: int, n: int) -> list[Property]:  # 定义 _make_properties 函数，集中处理这一段业务逻辑。
    """为指定区域批量生成模拟房源数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    props = []  # 设置 props 的值，供后续业务判断、查询或响应组装使用。
    for _ in range(n):  # 遍历当前数据集合，逐项完成处理。
        rooms = _weighted_rooms()  # 设置 rooms 的值，供后续业务判断、查询或响应组装使用。
        lo, hi = ROOM_AREA[rooms]  # 设置 lo, hi 的值，供后续业务判断、查询或响应组装使用。
        area = round(random.uniform(lo, hi), 1)  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
        unit_price = max(8000, round(random.gauss(base_price, base_price * 0.12)))  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
        total_price = round(unit_price * area / 10000, 1)  # 设置 total_price 的值，供后续业务判断、查询或响应组装使用。
        total_floors = random.choice([6, 11, 18, 26, 33])  # 设置 total_floors 的值，供后续业务判断、查询或响应组装使用。
        has_elevator = total_floors > 6 or random.random() > 0.5  # 设置 has_elevator 的值，供后续业务判断、查询或响应组装使用。
        decoration = random.choice(DECORATIONS)  # 设置 decoration 的值，供后续业务判断、查询或响应组装使用。
        props.append(  # 执行当前代码行对应的业务处理步骤。
            Property(  # 执行当前代码行对应的业务处理步骤。
                district_id=district.id,  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
                title=f"{district.name}{decoration}{rooms}居 {random.choice(FEATURES)}",  # 设置 title 的值，供后续业务判断、查询或响应组装使用。
                total_price=total_price,  # 设置 total_price 的值，供后续业务判断、查询或响应组装使用。
                unit_price=unit_price,  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
                area=area,  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
                rooms=rooms,  # 设置 rooms 的值，供后续业务判断、查询或响应组装使用。
                halls=1 if rooms <= 1 else 2,  # 设置 halls 的值，供后续业务判断、查询或响应组装使用。
                floor=random.randint(1, total_floors),  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
                total_floors=total_floors,  # 设置 total_floors 的值，供后续业务判断、查询或响应组装使用。
                build_year=random.randint(1998, 2023),  # 设置 build_year 的值，供后续业务判断、查询或响应组装使用。
                orientation=random.choice(ORIENTATIONS),  # 设置 orientation 的值，供后续业务判断、查询或响应组装使用。
                decoration=decoration,  # 设置 decoration 的值，供后续业务判断、查询或响应组装使用。
                has_elevator=has_elevator,  # 设置 has_elevator 的值，供后续业务判断、查询或响应组装使用。
                listing_type="二手房",  # 设置 listing_type 的值，供后续业务判断、查询或响应组装使用。
                lng=round((district.lng or 0) + random.uniform(-0.03, 0.03), 5),  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
                lat=round((district.lat or 0) + random.uniform(-0.03, 0.03), 5),  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。
                source="seed",  # 设置 source 的值，供后续业务判断、查询或响应组装使用。
            )  # 结束当前多行数据结构或函数调用。
        )  # 结束当前多行数据结构或函数调用。
    return props  # 返回处理后的结果给调用方继续使用。


def _make_facilities(district: District) -> list[Facility]:  # 定义 _make_facilities 函数，集中处理这一段业务逻辑。
    """为指定区域生成周边配套设施模拟数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    base_lng, base_lat = district.lng or 0, district.lat or 0  # 设置 base_lng, base_lat 的值，供后续业务判断、查询或响应组装使用。
    specs = [  # 设置 specs 的值，供后续业务判断、查询或响应组装使用。
        (f"{district.name}实验小学", "school"),  # 执行当前代码行对应的业务处理步骤。
        (f"{district.name}第二中学", "school"),  # 执行当前代码行对应的业务处理步骤。
        (f"{district.name}人民医院", "hospital"),  # 执行当前代码行对应的业务处理步骤。
        (f"地铁{random.randint(1, 16)}号线 · {district.name}站", "subway"),  # 执行当前代码行对应的业务处理步骤。
        (f"{district.name}万象汇", "mall"),  # 执行当前代码行对应的业务处理步骤。
        (f"{district.name}中央公园", "park"),  # 执行当前代码行对应的业务处理步骤。
    ]  # 结束当前多行数据结构或函数调用。
    return [  # 返回处理后的结果给调用方继续使用。
        Facility(  # 执行当前代码行对应的业务处理步骤。
            district_id=district.id, name=name, category=cat,  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
            lng=round(base_lng + random.uniform(-0.02, 0.02), 5),  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
            lat=round(base_lat + random.uniform(-0.02, 0.02), 5),  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。
        )  # 结束当前多行数据结构或函数调用。
        for name, cat in specs  # 遍历当前数据集合，逐项完成处理。
    ]  # 结束当前多行数据结构或函数调用。


def _make_price_history(district: District, base_price: int) -> list[PriceHistory]:  # 定义 _make_price_history 函数，集中处理这一段业务逻辑。
    """为指定区域生成近期房价历史模拟数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    months = _last_n_months(24)  # 设置 months 的值，供后续业务判断、查询或响应组装使用。
    # Start a bit below today's level and drift upward with mild noise.
    price = base_price * random.uniform(0.85, 0.93)  # 设置 price 的值，供后续业务判断、查询或响应组装使用。
    target_step = (base_price - price) / len(months)  # 设置 target_step 的值，供后续业务判断、查询或响应组装使用。
    rows = []  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
    for month in months:  # 遍历当前数据集合，逐项完成处理。
        price += target_step * random.uniform(0.4, 1.6)  # 设置 price + 的值，供后续业务判断、查询或响应组装使用。
        rows.append(  # 执行当前代码行对应的业务处理步骤。
            PriceHistory(  # 执行当前代码行对应的业务处理步骤。
                district_id=district.id, month=month, avg_unit_price=round(price)  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
            )  # 结束当前多行数据结构或函数调用。
        )  # 结束当前多行数据结构或函数调用。
    return rows  # 返回处理后的结果给调用方继续使用。


def run_seed(app) -> None:  # 定义 run_seed 函数，集中处理这一段业务逻辑。
    """清空并重建样例城市、区域、房源、设施和价格历史数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    with app.app_context():  # 进入上下文管理流程，自动处理资源打开和释放。
        print("→ 重建数据表 ...")  # 输出当前处理结果或运行状态，方便调试和观察流程。
        db.drop_all()  # 执行当前代码行对应的业务处理步骤。
        db.create_all()  # 执行当前代码行对应的业务处理步骤。

        n_cities = n_districts = n_props = n_facils = n_hist = 0  # 设置 n_cities 的值，供后续业务判断、查询或响应组装使用。
        for city_name, info in CITY_DATA.items():  # 遍历当前数据集合，逐项完成处理。
            city = City(  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
                name=city_name, name_en="", province=info["province"],  # 设置 name 的值，供后续业务判断、查询或响应组装使用。
                lng=info["lng"], lat=info["lat"],  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
            )  # 结束当前多行数据结构或函数调用。
            db.session.add(city)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            db.session.flush()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            n_cities += 1  # 设置 n_cities + 的值，供后续业务判断、查询或响应组装使用。

            districts = list(info["districts"].items())  # 设置 districts 的值，供后续业务判断、查询或响应组装使用。
            cols = int(len(districts) ** 0.5) + 1  # 设置 cols 的值，供后续业务判断、查询或响应组装使用。
            for idx, (dname, base_price) in enumerate(districts):  # 遍历当前数据集合，逐项完成处理。
                district = District(  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
                    city_id=city.id, name=dname,  # 设置 city_id 的值，供后续业务判断、查询或响应组装使用。
                    lng=round(info["lng"] + random.uniform(-0.08, 0.08), 5),  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
                    lat=round(info["lat"] + random.uniform(-0.08, 0.08), 5),  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。
                    grid_x=idx % cols, grid_y=idx // cols,  # 设置 grid_x 的值，供后续业务判断、查询或响应组装使用。
                )  # 结束当前多行数据结构或函数调用。
                db.session.add(district)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
                db.session.flush()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
                n_districts += 1  # 设置 n_districts + 的值，供后续业务判断、查询或响应组装使用。

                props = _make_properties(district, base_price, random.randint(22, 36))  # 设置 props 的值，供后续业务判断、查询或响应组装使用。
                facils = _make_facilities(district)  # 设置 facils 的值，供后续业务判断、查询或响应组装使用。
                hist = _make_price_history(district, base_price)  # 设置 hist 的值，供后续业务判断、查询或响应组装使用。
                db.session.add_all(props + facils + hist)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
                n_props += len(props)  # 设置 n_props + 的值，供后续业务判断、查询或响应组装使用。
                n_facils += len(facils)  # 设置 n_facils + 的值，供后续业务判断、查询或响应组装使用。
                n_hist += len(hist)  # 设置 n_hist + 的值，供后续业务判断、查询或响应组装使用。

        db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
        print(  # 输出当前处理结果或运行状态，方便调试和观察流程。
            f"✓ 完成：{n_cities} 城市 / {n_districts} 行政区 / "  # 执行当前代码行对应的业务处理步骤。
            f"{n_props} 房源 / {n_facils} 设施 / {n_hist} 条价格走势。"  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。


if __name__ == "__main__":  # 判断当前条件是否成立，决定是否进入对应处理分支。
    from app import app  # 从 app 导入 app，供本文件后续逻辑调用。

    run_seed(app)  # 执行当前代码行对应的业务处理步骤。
