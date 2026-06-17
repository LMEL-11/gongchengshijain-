"""Item 管道：
1) CleanValidatePipeline —— 类型转换、单价兜底推算、字段截断、丢弃无效条目；
2) DatabasePipeline —— 复用后端 Flask 应用与 SQLAlchemy 模型写入 Property 表，
   自动 get_or_create 城市/行政区，按 source_url 去重。
"""
import os
import sys

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


def _to_float(v):
    try:
        return float(v) if v not in (None, "") else None
    except (ValueError, TypeError):
        return None


def _to_int(v):
    f = _to_float(v)
    return int(f) if f is not None else None


def _truncate(s, n):
    if s is None:
        return None
    s = str(s).strip()
    return s[:n] if s else None


class CleanValidatePipeline:
    """类型转换 + 单价兜底 + 必要字段校验。"""

    def process_item(self, item, spider):
        a = ItemAdapter(item)

        a["total_price"] = _to_float(a.get("total_price"))
        a["unit_price"] = _to_float(a.get("unit_price"))
        a["area"] = _to_float(a.get("area"))
        for f in ("rooms", "halls", "floor", "total_floors", "build_year"):
            a[f] = _to_int(a.get(f))

        # 单价缺失则用 总价(万元)/面积 反推为 元/㎡
        if not a.get("unit_price") and a.get("total_price") and a.get("area"):
            a["unit_price"] = a["total_price"] * 10000 / a["area"]
        if a.get("unit_price"):
            a["unit_price"] = round(a["unit_price"])

        # 截断到数据库列长度，避免 MySQL 严格模式报错
        a["title"] = _truncate(a.get("title"), 200)
        a["orientation"] = _truncate(a.get("orientation"), 20)
        a["decoration"] = _truncate(a.get("decoration"), 20)
        a["source"] = _truncate(a.get("source"), 50)
        a["source_url"] = _truncate(a.get("source_url"), 500)

        if not a.get("title") or not (a.get("unit_price") or a.get("total_price")):
            raise DropItem(f"缺少必要字段(标题/价格)：{a.get('source_url')}")
        return item


class DatabasePipeline:
    """写入后端 Property 表；复用 backend 的应用工厂、配置与模型。

    每条 item 在独立的 ``with app.app_context()`` 内完成查询/写入，避免 Flask
    应用上下文在 Scrapy/Twisted 各回调间（contextvars）不共享的问题。城市/行政区
    按名称缓存其 **id**（而非 ORM 对象），跨上下文安全。
    """

    def open_spider(self, spider):
        # 把 backend/ 加入 import 路径，复用其 Flask app / DB 配置 / 模型
        backend = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "backend")
        )
        if backend not in sys.path:
            sys.path.insert(0, backend)

        from app import app  # 应用工厂在导入时已 create_app()（含 DB 配置与建表）
        from extensions import db
        from models import City, District, Property

        self.app = app
        self.db = db
        self.City, self.District, self.Property = City, District, Property

        self._province_of = self._load_province_map(backend)
        self._city_ids = {}
        self._district_ids = {}
        self._seen = set()
        self.added = 0
        self.skipped = 0
        spider.logger.info(
            "DatabasePipeline 就绪，写入：%s", app.config["SQLALCHEMY_DATABASE_URI"]
        )

    # _city_id / _district_id 必须在 app 上下文内调用
    def _load_province_map(self, backend):
        """从 backend/data/province_data.csv 建「城市名 -> 省份」映射，
        给新建城市补 province；并补充链家有站但不在 CSV 的县级市/特殊地区。"""
        import csv

        mapping = {}
        path = os.path.join(backend, "data", "province_data.csv")
        try:
            with open(path, encoding="utf-8-sig") as fh:
                for row in csv.DictReader(fh):
                    prov = (row.get("省份") or "").strip()
                    city = (row.get("城市") or "").strip()
                    if prov and city:
                        mapping[city] = prov
        except OSError:
            pass
        mapping.update({
            "江阴": "江苏", "宜兴": "江苏", "昆山": "江苏", "常熟": "江苏", "太仓": "江苏",
            "句容": "江苏", "丹阳": "江苏", "海门": "江苏",
            "义乌": "浙江",
            "涿州": "河北",
            "澄迈": "海南", "陵水": "海南", "万宁": "海南",
            "西双版纳": "云南", "大理": "云南",
            "凉山": "四川", "湘西": "湖南",
        })
        return mapping

    def _city_id(self, name):
        name = (name or "未知城市").strip()
        if name in self._city_ids:
            return self._city_ids[name]
        city = self.City.query.filter_by(name=name).first()
        if city is None:
            prov = self._province_of.get(name)
            city = self.City(name=name, province=prov)  # 经纬度留空，可后续补全
            self.db.session.add(city)
            self.db.session.flush()
        elif getattr(city, "province", None) in (None, "") and self._province_of.get(name):
            city.province = self._province_of[name]  # 回填已存在城市缺失的省份
        self._city_ids[name] = city.id
        return city.id

    def _district_id(self, city_id, name, lng=None, lat=None):
        name = (name or "未知区域").strip()
        key = (city_id, name)
        if key in self._district_ids:
            return self._district_ids[key]
        d = self.District.query.filter_by(city_id=city_id, name=name).first()
        if d is None:
            d = self.District(city_id=city_id, name=name, lng=lng, lat=lat)
            self.db.session.add(d)
            self.db.session.flush()
        self._district_ids[key] = d.id
        return d.id

    def process_item(self, item, spider):
        a = ItemAdapter(item)
        url = a.get("source_url")
        if url and url in self._seen:
            self.skipped += 1
            return item

        with self.app.app_context():
            try:
                if url and self.Property.query.filter_by(source_url=url).first() is not None:
                    self._seen.add(url)
                    self.skipped += 1
                    return item

                city_id = self._city_id(a.get("city"))
                district_id = self._district_id(
                    city_id, a.get("district"), a.get("lng"), a.get("lat")
                )
                elev = a.get("has_elevator")
                self.db.session.add(
                    self.Property(
                        district_id=district_id,
                        title=a.get("title"),
                        total_price=a.get("total_price"),
                        unit_price=a.get("unit_price"),
                        area=a.get("area"),
                        rooms=a.get("rooms") or 0,
                        halls=a.get("halls") or 0,
                        floor=a.get("floor"),
                        total_floors=a.get("total_floors"),
                        build_year=a.get("build_year"),
                        orientation=a.get("orientation"),
                        decoration=a.get("decoration"),
                        has_elevator=bool(elev) if elev is not None else False,
                        listing_type=a.get("listing_type") or "二手房",
                        lng=a.get("lng"),
                        lat=a.get("lat"),
                        source=a.get("source") or "lianjia",
                        source_url=url,
                    )
                )
                self.db.session.commit()
            except Exception:
                self.db.session.rollback()
                # 回滚后清空 id 缓存，避免引用未提交的城市/区
                self._city_ids.clear()
                self._district_ids.clear()
                spider.logger.exception("写入失败，已跳过：%s", url)
                return item

        self._seen.add(url)
        self.added += 1
        if self.added % 20 == 0:
            spider.logger.info("已写入 %d 条 ...", self.added)
        return item

    def close_spider(self, spider):
        spider.logger.info(
            "入库完成：新增 %d 条，跳过(重复) %d 条。", self.added, self.skipped
        )
