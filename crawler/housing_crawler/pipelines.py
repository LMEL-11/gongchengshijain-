"""Item 管道：
1) CleanValidatePipeline —— 类型转换、单价兜底推算、字段截断、丢弃无效条目；
2) DatabasePipeline —— 复用后端 Flask 应用与 SQLAlchemy 模型写入 Property 表，
   自动 get_or_create 城市/行政区，按 source_url 去重。
"""
import os  # 逐行注释：导入本行所需的模块或对象。
import sys  # 逐行注释：导入本行所需的模块或对象。

from itemadapter import ItemAdapter  # 逐行注释：导入本行所需的模块或对象。
from scrapy.exceptions import DropItem  # 逐行注释：导入本行所需的模块或对象。


def _to_float(v):  # 逐行注释：声明函数或方法入口。
    """将输入值安全转换为浮点数。"""
    try:  # 逐行注释：开始执行可能出现异常的逻辑。
        return float(v) if v not in (None, "") else None  # 逐行注释：返回当前逻辑的处理结果。
    except (ValueError, TypeError):  # 逐行注释：捕获异常并执行错误处理。
        return None  # 逐行注释：返回当前逻辑的处理结果。


def _to_int(v):  # 逐行注释：声明函数或方法入口。
    """将输入值安全转换为整数。"""
    f = _to_float(v)  # 逐行注释：赋值或更新当前变量/字段。
    return int(f) if f is not None else None  # 逐行注释：返回当前逻辑的处理结果。


def _truncate(s, n):  # 逐行注释：声明函数或方法入口。
    """按最大长度截断字符串并保留空值语义。"""
    if s is None:  # 逐行注释：根据条件判断是否进入该分支。
        return None  # 逐行注释：返回当前逻辑的处理结果。
    s = str(s).strip()  # 逐行注释：赋值或更新当前变量/字段。
    return s[:n] if s else None  # 逐行注释：返回当前逻辑的处理结果。


class CleanValidatePipeline:  # 逐行注释：声明类并定义相关数据或行为。
    """类型转换 + 单价兜底 + 必要字段校验。"""

    def process_item(self, item, spider):  # 逐行注释：声明函数或方法入口。
        """清洗、校验或入库单条爬取房源数据。"""
        a = ItemAdapter(item)  # 逐行注释：赋值或更新当前变量/字段。

        a["total_price"] = _to_float(a.get("total_price"))  # 逐行注释：赋值或更新当前变量/字段。
        a["unit_price"] = _to_float(a.get("unit_price"))  # 逐行注释：赋值或更新当前变量/字段。
        a["area"] = _to_float(a.get("area"))  # 逐行注释：赋值或更新当前变量/字段。
        for f in ("rooms", "halls", "floor", "total_floors", "build_year"):  # 逐行注释：遍历集合中的每一项并执行处理。
            a[f] = _to_int(a.get(f))  # 逐行注释：赋值或更新当前变量/字段。

        # 单价缺失则用 总价(万元)/面积 反推为 元/㎡
        if not a.get("unit_price") and a.get("total_price") and a.get("area"):  # 逐行注释：根据条件判断是否进入该分支。
            a["unit_price"] = a["total_price"] * 10000 / a["area"]  # 逐行注释：赋值或更新当前变量/字段。
        if a.get("unit_price"):  # 逐行注释：根据条件判断是否进入该分支。
            a["unit_price"] = round(a["unit_price"])  # 逐行注释：赋值或更新当前变量/字段。

        # 截断到数据库列长度，避免 MySQL 严格模式报错
        a["title"] = _truncate(a.get("title"), 200)  # 逐行注释：赋值或更新当前变量/字段。
        a["orientation"] = _truncate(a.get("orientation"), 20)  # 逐行注释：赋值或更新当前变量/字段。
        a["decoration"] = _truncate(a.get("decoration"), 20)  # 逐行注释：赋值或更新当前变量/字段。
        a["source"] = _truncate(a.get("source"), 50)  # 逐行注释：赋值或更新当前变量/字段。
        a["source_url"] = _truncate(a.get("source_url"), 500)  # 逐行注释：赋值或更新当前变量/字段。

        if not a.get("title") or not (a.get("unit_price") or a.get("total_price")):  # 逐行注释：根据条件判断是否进入该分支。
            raise DropItem(f"缺少必要字段(标题/价格)：{a.get('source_url')}")  # 逐行注释：抛出异常并交由上层处理。
        return item  # 逐行注释：返回当前逻辑的处理结果。


class DatabasePipeline:  # 逐行注释：声明类并定义相关数据或行为。
    """写入后端 Property 表；复用 backend 的应用工厂、配置与模型。

    每条 item 在独立的 ``with app.app_context()`` 内完成查询/写入，避免 Flask
    应用上下文在 Scrapy/Twisted 各回调间（contextvars）不共享的问题。城市/行政区
    按名称缓存其 **id**（而非 ORM 对象），跨上下文安全。
    """

    def open_spider(self, spider):  # 逐行注释：声明函数或方法入口。
        """爬虫启动时初始化数据库连接、建表和缓存。"""
        # 把 backend/ 加入 import 路径，复用其 Flask app / DB 配置 / 模型
        backend = os.path.abspath(  # 逐行注释：赋值或更新当前变量/字段。
            os.path.join(os.path.dirname(__file__), "..", "..", "backend")  # 逐行注释：执行本行代码逻辑。
        )  # 逐行注释：结束当前数据结构或调用块。
        if backend not in sys.path:  # 逐行注释：根据条件判断是否进入该分支。
            sys.path.insert(0, backend)  # 逐行注释：执行本行代码逻辑。

        from app import app  # 应用工厂在导入时已 create_app()（含 DB 配置与建表）
        from extensions import db  # 逐行注释：导入本行所需的模块或对象。
        from models import City, District, Property  # 逐行注释：导入本行所需的模块或对象。

        self.app = app  # 逐行注释：赋值或更新当前变量/字段。
        self.db = db  # 逐行注释：赋值或更新当前变量/字段。
        self.City, self.District, self.Property = City, District, Property  # 逐行注释：赋值或更新当前变量/字段。

        self._province_of = self._load_province_map(backend)  # 逐行注释：赋值或更新当前变量/字段。
        self._city_ids = {}  # 逐行注释：赋值或更新当前变量/字段。
        self._district_ids = {}  # 逐行注释：赋值或更新当前变量/字段。
        self._seen = set()  # 逐行注释：赋值或更新当前变量/字段。
        self.added = 0  # 逐行注释：赋值或更新当前变量/字段。
        self.skipped = 0  # 逐行注释：赋值或更新当前变量/字段。
        spider.logger.info(  # 逐行注释：执行本行代码逻辑。
            "DatabasePipeline 就绪，写入：%s", app.config["SQLALCHEMY_DATABASE_URI"]  # 逐行注释：执行本行代码逻辑。
        )  # 逐行注释：结束当前数据结构或调用块。

    # _city_id / _district_id 必须在 app 上下文内调用
    def _load_province_map(self, backend):  # 逐行注释：声明函数或方法入口。
        """从 backend/data/province_data.csv 建「城市名 -> 省份」映射，
        给新建城市补 province；并补充链家有站但不在 CSV 的县级市/特殊地区。"""
        import csv  # 逐行注释：导入本行所需的模块或对象。

        mapping = {}  # 逐行注释：赋值或更新当前变量/字段。
        path = os.path.join(backend, "data", "province_data.csv")  # 逐行注释：赋值或更新当前变量/字段。
        try:  # 逐行注释：开始执行可能出现异常的逻辑。
            with open(path, encoding="utf-8-sig") as fh:  # 逐行注释：进入上下文管理器并自动处理资源。
                for row in csv.DictReader(fh):  # 逐行注释：遍历集合中的每一项并执行处理。
                    prov = (row.get("省份") or "").strip()  # 逐行注释：赋值或更新当前变量/字段。
                    city = (row.get("城市") or "").strip()  # 逐行注释：赋值或更新当前变量/字段。
                    if prov and city:  # 逐行注释：根据条件判断是否进入该分支。
                        mapping[city] = prov  # 逐行注释：赋值或更新当前变量/字段。
        except OSError:  # 逐行注释：捕获异常并执行错误处理。
            pass  # 逐行注释：保留语法占位以便后续扩展。
        mapping.update({  # 逐行注释：执行本行代码逻辑。
            "江阴": "江苏", "宜兴": "江苏", "昆山": "江苏", "常熟": "江苏", "太仓": "江苏",  # 逐行注释：设置当前数据项或参数。
            "句容": "江苏", "丹阳": "江苏", "海门": "江苏",  # 逐行注释：设置当前数据项或参数。
            "义乌": "浙江",  # 逐行注释：设置当前数据项或参数。
            "涿州": "河北",  # 逐行注释：设置当前数据项或参数。
            "澄迈": "海南", "陵水": "海南", "万宁": "海南",  # 逐行注释：设置当前数据项或参数。
            "西双版纳": "云南", "大理": "云南",  # 逐行注释：设置当前数据项或参数。
            "凉山": "四川", "湘西": "湖南",  # 逐行注释：设置当前数据项或参数。
        })  # 逐行注释：执行本行代码逻辑。
        return mapping  # 逐行注释：返回当前逻辑的处理结果。

    def _city_id(self, name):  # 逐行注释：声明函数或方法入口。
        """获取或创建城市记录并返回城市编号。"""
        name = (name or "未知城市").strip()  # 逐行注释：赋值或更新当前变量/字段。
        if name in self._city_ids:  # 逐行注释：根据条件判断是否进入该分支。
            return self._city_ids[name]  # 逐行注释：返回当前逻辑的处理结果。
        city = self.City.query.filter_by(name=name).first()  # 逐行注释：赋值或更新当前变量/字段。
        if city is None:  # 逐行注释：根据条件判断是否进入该分支。
            prov = self._province_of.get(name)  # 逐行注释：赋值或更新当前变量/字段。
            city = self.City(name=name, province=prov)  # 经纬度留空，可后续补全
            self.db.session.add(city)  # 逐行注释：把对象加入数据库会话等待提交。
            self.db.session.flush()  # 逐行注释：执行本行代码逻辑。
        elif getattr(city, "province", None) in (None, "") and self._province_of.get(name):  # 逐行注释：根据条件判断是否进入该分支。
            city.province = self._province_of[name]  # 回填已存在城市缺失的省份
        self._city_ids[name] = city.id  # 逐行注释：赋值或更新当前变量/字段。
        return city.id  # 逐行注释：返回当前逻辑的处理结果。

    def _district_id(self, city_id, name, lng=None, lat=None):  # 逐行注释：声明函数或方法入口。
        """获取或创建区域记录并返回区域编号。"""
        name = (name or "未知区域").strip()  # 逐行注释：赋值或更新当前变量/字段。
        key = (city_id, name)  # 逐行注释：赋值或更新当前变量/字段。
        if key in self._district_ids:  # 逐行注释：根据条件判断是否进入该分支。
            return self._district_ids[key]  # 逐行注释：返回当前逻辑的处理结果。
        d = self.District.query.filter_by(city_id=city_id, name=name).first()  # 逐行注释：赋值或更新当前变量/字段。
        if d is None:  # 逐行注释：根据条件判断是否进入该分支。
            d = self.District(city_id=city_id, name=name, lng=lng, lat=lat)  # 逐行注释：赋值或更新当前变量/字段。
            self.db.session.add(d)  # 逐行注释：把对象加入数据库会话等待提交。
            self.db.session.flush()  # 逐行注释：执行本行代码逻辑。
        self._district_ids[key] = d.id  # 逐行注释：赋值或更新当前变量/字段。
        return d.id  # 逐行注释：返回当前逻辑的处理结果。

    def process_item(self, item, spider):  # 逐行注释：声明函数或方法入口。
        """清洗、校验或入库单条爬取房源数据。"""
        a = ItemAdapter(item)  # 逐行注释：赋值或更新当前变量/字段。
        url = a.get("source_url")  # 逐行注释：赋值或更新当前变量/字段。
        if url and url in self._seen:  # 逐行注释：根据条件判断是否进入该分支。
            self.skipped += 1  # 逐行注释：赋值或更新当前变量/字段。
            return item  # 逐行注释：返回当前逻辑的处理结果。

        with self.app.app_context():  # 逐行注释：进入上下文管理器并自动处理资源。
            try:  # 逐行注释：开始执行可能出现异常的逻辑。
                if url and self.Property.query.filter_by(source_url=url).first() is not None:  # 逐行注释：根据条件判断是否进入该分支。
                    self._seen.add(url)  # 逐行注释：执行本行代码逻辑。
                    self.skipped += 1  # 逐行注释：赋值或更新当前变量/字段。
                    return item  # 逐行注释：返回当前逻辑的处理结果。

                city_id = self._city_id(a.get("city"))  # 逐行注释：赋值或更新当前变量/字段。
                district_id = self._district_id(  # 逐行注释：赋值或更新当前变量/字段。
                    city_id, a.get("district"), a.get("lng"), a.get("lat")  # 逐行注释：执行本行代码逻辑。
                )  # 逐行注释：结束当前数据结构或调用块。
                elev = a.get("has_elevator")  # 逐行注释：赋值或更新当前变量/字段。
                self.db.session.add(  # 逐行注释：把对象加入数据库会话等待提交。
                    self.Property(  # 逐行注释：执行本行代码逻辑。
                        district_id=district_id,  # 逐行注释：赋值或更新当前变量/字段。
                        title=a.get("title"),  # 逐行注释：赋值或更新当前变量/字段。
                        total_price=a.get("total_price"),  # 逐行注释：赋值或更新当前变量/字段。
                        unit_price=a.get("unit_price"),  # 逐行注释：赋值或更新当前变量/字段。
                        area=a.get("area"),  # 逐行注释：赋值或更新当前变量/字段。
                        rooms=a.get("rooms") or 0,  # 逐行注释：赋值或更新当前变量/字段。
                        halls=a.get("halls") or 0,  # 逐行注释：赋值或更新当前变量/字段。
                        floor=a.get("floor"),  # 逐行注释：赋值或更新当前变量/字段。
                        total_floors=a.get("total_floors"),  # 逐行注释：赋值或更新当前变量/字段。
                        build_year=a.get("build_year"),  # 逐行注释：赋值或更新当前变量/字段。
                        orientation=a.get("orientation"),  # 逐行注释：赋值或更新当前变量/字段。
                        decoration=a.get("decoration"),  # 逐行注释：赋值或更新当前变量/字段。
                        has_elevator=bool(elev) if elev is not None else False,  # 逐行注释：赋值或更新当前变量/字段。
                        listing_type=a.get("listing_type") or "二手房",  # 逐行注释：赋值或更新当前变量/字段。
                        lng=a.get("lng"),  # 逐行注释：赋值或更新当前变量/字段。
                        lat=a.get("lat"),  # 逐行注释：赋值或更新当前变量/字段。
                        source=a.get("source") or "lianjia",  # 逐行注释：赋值或更新当前变量/字段。
                        source_url=url,  # 逐行注释：赋值或更新当前变量/字段。
                    )  # 逐行注释：结束当前数据结构或调用块。
                )  # 逐行注释：结束当前数据结构或调用块。
                self.db.session.commit()  # 逐行注释：提交当前数据库事务。
            except Exception:  # 逐行注释：捕获异常并执行错误处理。
                self.db.session.rollback()  # 逐行注释：执行本行代码逻辑。
                # 回滚后清空 id 缓存，避免引用未提交的城市/区
                self._city_ids.clear()  # 逐行注释：执行本行代码逻辑。
                self._district_ids.clear()  # 逐行注释：执行本行代码逻辑。
                spider.logger.exception("写入失败，已跳过：%s", url)  # 逐行注释：执行本行代码逻辑。
                return item  # 逐行注释：返回当前逻辑的处理结果。

        self._seen.add(url)  # 逐行注释：执行本行代码逻辑。
        self.added += 1  # 逐行注释：赋值或更新当前变量/字段。
        if self.added % 20 == 0:  # 逐行注释：根据条件判断是否进入该分支。
            spider.logger.info("已写入 %d 条 ...", self.added)  # 逐行注释：执行本行代码逻辑。
        return item  # 逐行注释：返回当前逻辑的处理结果。

    def close_spider(self, spider):  # 逐行注释：声明函数或方法入口。
        """爬虫关闭时提交剩余事务并释放数据库连接。"""
        spider.logger.info(  # 逐行注释：执行本行代码逻辑。
            "入库完成：新增 %d 条，跳过(重复) %d 条。", self.added, self.skipped  # 逐行注释：执行本行代码逻辑。
        )  # 逐行注释：结束当前数据结构或调用块。
