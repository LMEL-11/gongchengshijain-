"""Seed the database with realistic **synthetic** housing data.

Run with:  flask --app app seed     (or)     python seed.py

All data here is generated, not scraped — see ``spider/__init__.py`` for the
data-collection scaffold and its compliance notes.
"""
import random
from datetime import date

from extensions import db
from models import City, District, Facility, PriceHistory, Property

random.seed(42)  # reproducible output

# 城市 -> 中心经纬度、省份、各行政区基准单价（元/㎡）
CITY_DATA = {
    "北京": {
        "province": "北京市", "lng": 116.40, "lat": 39.90,
        "districts": {
            "西城区": 130000, "东城区": 115000, "海淀区": 98000, "朝阳区": 85000,
            "丰台区": 62000, "石景山区": 55000, "通州区": 48000, "昌平区": 42000,
        },
    },
    "上海": {
        "province": "上海市", "lng": 121.47, "lat": 31.23,
        "districts": {
            "黄浦区": 120000, "静安区": 110000, "徐汇区": 105000, "长宁区": 95000,
            "浦东新区": 78000, "杨浦区": 72000, "闵行区": 58000, "宝山区": 48000,
        },
    },
    "广州": {
        "province": "广东省", "lng": 113.26, "lat": 23.13,
        "districts": {
            "天河区": 68000, "越秀区": 62000, "海珠区": 55000, "荔湾区": 48000,
            "黄埔区": 40000, "白云区": 38000, "番禺区": 35000,
        },
    },
    "深圳": {
        "province": "广东省", "lng": 114.06, "lat": 22.54,
        "districts": {
            "南山区": 115000, "福田区": 105000, "罗湖区": 72000, "宝安区": 65000,
            "龙华区": 60000, "龙岗区": 52000,
        },
    },
    "杭州": {
        "province": "浙江省", "lng": 120.15, "lat": 30.27,
        "districts": {
            "上城区": 58000, "西湖区": 55000, "滨江区": 52000, "拱墅区": 42000,
            "余杭区": 35000, "萧山区": 30000,
        },
    },
    "成都": {
        "province": "四川省", "lng": 104.07, "lat": 30.57,
        "districts": {
            "高新区": 30000, "锦江区": 28000, "青羊区": 27000, "武侯区": 26000,
            "成华区": 22000, "天府新区": 24000, "金牛区": 20000,
        },
    },
}

ORIENTATIONS = ["南", "南北", "东南", "东", "西南", "北"]
DECORATIONS = ["毛坯", "简装", "精装", "豪装"]
FEATURES = ["满五唯一", "近地铁", "南北通透", "优质学区", "精装修", "低总价", "采光极佳", "业主诚售"]
ROOM_AREA = {1: (38, 60), 2: (65, 95), 3: (95, 140), 4: (140, 200)}
ROOM_WEIGHTS = [(1, 0.18), (2, 0.42), (3, 0.30), (4, 0.10)]


def _weighted_rooms() -> int:
    """按权重随机生成更接近真实分布的户型室数。"""
    r = random.random()
    cum = 0.0
    for rooms, w in ROOM_WEIGHTS:
        cum += w
        if r <= cum:
            return rooms
    return 2


def _last_n_months(n: int) -> list[str]:
    """生成从当前月份向前追溯的月份序列。"""
    today = date.today()
    y, m, out = today.year, today.month, []
    for _ in range(n):
        out.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    return list(reversed(out))


def _make_properties(district: District, base_price: int, n: int) -> list[Property]:
    """为指定区域批量生成模拟房源数据。"""
    props = []
    for _ in range(n):
        rooms = _weighted_rooms()
        lo, hi = ROOM_AREA[rooms]
        area = round(random.uniform(lo, hi), 1)
        unit_price = max(8000, round(random.gauss(base_price, base_price * 0.12)))
        total_price = round(unit_price * area / 10000, 1)  # 万元
        total_floors = random.choice([6, 11, 18, 26, 33])
        has_elevator = total_floors > 6 or random.random() > 0.5
        decoration = random.choice(DECORATIONS)
        props.append(
            Property(
                district_id=district.id,
                title=f"{district.name}{decoration}{rooms}居 {random.choice(FEATURES)}",
                total_price=total_price,
                unit_price=unit_price,
                area=area,
                rooms=rooms,
                halls=1 if rooms <= 1 else 2,
                floor=random.randint(1, total_floors),
                total_floors=total_floors,
                build_year=random.randint(1998, 2023),
                orientation=random.choice(ORIENTATIONS),
                decoration=decoration,
                has_elevator=has_elevator,
                listing_type="二手房",
                lng=round((district.lng or 0) + random.uniform(-0.03, 0.03), 5),
                lat=round((district.lat or 0) + random.uniform(-0.03, 0.03), 5),
                source="seed",
            )
        )
    return props


def _make_facilities(district: District) -> list[Facility]:
    """为指定区域生成周边配套设施模拟数据。"""
    base_lng, base_lat = district.lng or 0, district.lat or 0
    specs = [
        (f"{district.name}实验小学", "school"),
        (f"{district.name}第二中学", "school"),
        (f"{district.name}人民医院", "hospital"),
        (f"地铁{random.randint(1, 16)}号线 · {district.name}站", "subway"),
        (f"{district.name}万象汇", "mall"),
        (f"{district.name}中央公园", "park"),
    ]
    return [
        Facility(
            district_id=district.id, name=name, category=cat,
            lng=round(base_lng + random.uniform(-0.02, 0.02), 5),
            lat=round(base_lat + random.uniform(-0.02, 0.02), 5),
        )
        for name, cat in specs
    ]


def _make_price_history(district: District, base_price: int) -> list[PriceHistory]:
    """为指定区域生成近期房价历史模拟数据。"""
    months = _last_n_months(24)
    # Start a bit below today's level and drift upward with mild noise.
    price = base_price * random.uniform(0.85, 0.93)
    target_step = (base_price - price) / len(months)
    rows = []
    for month in months:
        price += target_step * random.uniform(0.4, 1.6)
        rows.append(
            PriceHistory(
                district_id=district.id, month=month, avg_unit_price=round(price)
            )
        )
    return rows


def run_seed(app) -> None:
    """清空并重建样例城市、区域、房源、设施和价格历史数据。"""
    with app.app_context():
        print("→ 重建数据表 ...")
        db.drop_all()
        db.create_all()

        n_cities = n_districts = n_props = n_facils = n_hist = 0
        for city_name, info in CITY_DATA.items():
            city = City(
                name=city_name, name_en="", province=info["province"],
                lng=info["lng"], lat=info["lat"],
            )
            db.session.add(city)
            db.session.flush()
            n_cities += 1

            districts = list(info["districts"].items())
            cols = int(len(districts) ** 0.5) + 1
            for idx, (dname, base_price) in enumerate(districts):
                district = District(
                    city_id=city.id, name=dname,
                    lng=round(info["lng"] + random.uniform(-0.08, 0.08), 5),
                    lat=round(info["lat"] + random.uniform(-0.08, 0.08), 5),
                    grid_x=idx % cols, grid_y=idx // cols,
                )
                db.session.add(district)
                db.session.flush()
                n_districts += 1

                props = _make_properties(district, base_price, random.randint(22, 36))
                facils = _make_facilities(district)
                hist = _make_price_history(district, base_price)
                db.session.add_all(props + facils + hist)
                n_props += len(props)
                n_facils += len(facils)
                n_hist += len(hist)

        db.session.commit()
        print(
            f"✓ 完成：{n_cities} 城市 / {n_districts} 行政区 / "
            f"{n_props} 房源 / {n_facils} 设施 / {n_hist} 条价格走势。"
        )


if __name__ == "__main__":
    from app import app

    run_seed(app)
