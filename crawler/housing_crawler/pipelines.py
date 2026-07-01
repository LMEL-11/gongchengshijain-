"""Item 管道：
1) CleanValidatePipeline —— 类型转换、单价兜底推算、字段截断、丢弃无效条目；
2) DatabasePipeline —— 复用后端 Flask 应用与 SQLAlchemy 模型写入 Property 表，
   自动 get_or_create 城市/行政区，按 source_url 去重。
"""
import os  # 导入 os 模块，为当前文件提供所需功能。
import sys  # 导入 sys 模块，为当前文件提供所需功能。

from itemadapter import ItemAdapter  # 从 itemadapter 导入 ItemAdapter，供本文件后续逻辑调用。
from scrapy.exceptions import DropItem  # 从 scrapy.exceptions 导入 DropItem，供本文件后续逻辑调用。


def _to_float(v):  # 定义 _to_float 函数，集中处理这一段业务逻辑。
    """将输入值安全转换为浮点数。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    try:  # 开始执行可能抛出异常的代码块。
        return float(v) if v not in (None, "") else None  # 返回处理后的结果给调用方继续使用。
    except (ValueError, TypeError):  # 捕获指定异常，并转入可控的错误处理流程。
        return None  # 返回处理后的结果给调用方继续使用。


def _to_int(v):  # 定义 _to_int 函数，集中处理这一段业务逻辑。
    """将输入值安全转换为整数。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    f = _to_float(v)  # 设置 f 的值，供后续业务判断、查询或响应组装使用。
    return int(f) if f is not None else None  # 返回处理后的结果给调用方继续使用。


def _truncate(s, n):  # 定义 _truncate 函数，集中处理这一段业务逻辑。
    """按最大长度截断字符串并保留空值语义。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if s is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return None  # 返回处理后的结果给调用方继续使用。
    s = str(s).strip()  # 设置 s 的值，供后续业务判断、查询或响应组装使用。
    return s[:n] if s else None  # 返回处理后的结果给调用方继续使用。


class CleanValidatePipeline:  # 定义 CleanValidatePipeline 类，封装对应的数据结构或业务行为。
    """类型转换 + 单价兜底 + 必要字段校验。"""  # 保留字符串内容，作为说明文本或页面展示文案。

    def process_item(self, item, spider):  # 定义 process_item 函数，集中处理这一段业务逻辑。
        """清洗、校验或入库单条爬取房源数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        a = ItemAdapter(item)  # 设置 a 的值，供后续业务判断、查询或响应组装使用。

        # 页面解析出的 item 字段都是弱类型文本，入库前先统一转换成价格、面积、楼层等数值。
        a["total_price"] = _to_float(a.get("total_price"))  # 设置 a["total_price" 的值，供后续业务判断、查询或响应组装使用。
        a["unit_price"] = _to_float(a.get("unit_price"))  # 设置 a["unit_price" 的值，供后续业务判断、查询或响应组装使用。
        a["area"] = _to_float(a.get("area"))  # 设置 a["area" 的值，供后续业务判断、查询或响应组装使用。
        for f in ("rooms", "halls", "floor", "total_floors", "build_year"):  # 遍历当前数据集合，逐项完成处理。
            a[f] = _to_int(a.get(f))  # 设置 a[f 的值，供后续业务判断、查询或响应组装使用。

        # 单价缺失则用 总价(万元)/面积 反推为 元/㎡
        if not a.get("unit_price") and a.get("total_price") and a.get("area"):  # 判断当前条件是否成立，决定是否进入对应处理分支。
            a["unit_price"] = a["total_price"] * 10000 / a["area"]  # 设置 a["unit_price" 的值，供后续业务判断、查询或响应组装使用。
        if a.get("unit_price"):  # 判断当前条件是否成立，决定是否进入对应处理分支。
            a["unit_price"] = round(a["unit_price"])  # 设置 a["unit_price" 的值，供后续业务判断、查询或响应组装使用。

        # 截断到数据库列长度，避免 MySQL 严格模式报错
        a["title"] = _truncate(a.get("title"), 200)  # 设置 a["title" 的值，供后续业务判断、查询或响应组装使用。
        a["orientation"] = _truncate(a.get("orientation"), 20)  # 设置 a["orientation" 的值，供后续业务判断、查询或响应组装使用。
        a["decoration"] = _truncate(a.get("decoration"), 20)  # 设置 a["decoration" 的值，供后续业务判断、查询或响应组装使用。
        a["source"] = _truncate(a.get("source"), 50)  # 设置 a["source" 的值，供后续业务判断、查询或响应组装使用。
        a["source_url"] = _truncate(a.get("source_url"), 500)  # 设置 a["source_url" 的值，供后续业务判断、查询或响应组装使用。

        # 标题和价格是房源展示、去重排查和后续统计的底线，缺失则直接丢弃。
        if not a.get("title") or not (a.get("unit_price") or a.get("total_price")):  # 判断当前条件是否成立，决定是否进入对应处理分支。
            raise DropItem(f"缺少必要字段(标题/价格)：{a.get('source_url')}")  # 主动抛出异常，提示当前流程无法继续。
        return item  # 返回处理后的结果给调用方继续使用。


class DatabasePipeline:  # 定义 DatabasePipeline 类，封装对应的数据结构或业务行为。
    """写入后端 Property 表；复用 backend 的应用工厂、配置与模型。

    每条 item 在独立的 ``with app.app_context()`` 内完成查询/写入，避免 Flask
    应用上下文在 Scrapy/Twisted 各回调间（contextvars）不共享的问题。城市/行政区
    按名称缓存其 **id**（而非 ORM 对象），跨上下文安全。
    """

    def open_spider(self, spider):  # 定义 open_spider 函数，集中处理这一段业务逻辑。
        """爬虫启动时初始化数据库连接、建表和缓存。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        # 把 backend/ 加入 import 路径，复用其 Flask app / DB 配置 / 模型
        backend = os.path.abspath(  # 设置 backend 的值，供后续业务判断、查询或响应组装使用。
            os.path.join(os.path.dirname(__file__), "..", "..", "backend")  # 把关联表纳入查询，获取跨表维度的数据。
        )  # 结束当前多行数据结构或函数调用。
        if backend not in sys.path:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            sys.path.insert(0, backend)  # 执行当前代码行对应的业务处理步骤。

        from app import app  # 从 app 导入 app，供本文件后续逻辑调用。
        from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
        from models import City, District, Property  # 从 models 导入 City, District, Property，供本文件后续逻辑调用。

        self.app = app  # 设置 self.app 的值，供后续业务判断、查询或响应组装使用。
        self.db = db  # 设置 self.db 的值，供后续业务判断、查询或响应组装使用。
        self.City, self.District, self.Property = City, District, Property  # 设置 self.City, self.District, self.Property 的值，供后续业务判断、查询或响应组装使用。

        self._province_of = self._load_province_map(backend)  # 设置 self._province_of 的值，供后续业务判断、查询或响应组装使用。
        self._city_ids = {}  # 设置 self._city_ids 的值，供后续业务判断、查询或响应组装使用。
        self._district_ids = {}  # 设置 self._district_ids 的值，供后续业务判断、查询或响应组装使用。
        self._seen = set()  # 设置 self._seen 的值，供后续业务判断、查询或响应组装使用。
        self.added = 0  # 设置 self.added 的值，供后续业务判断、查询或响应组装使用。
        self.skipped = 0  # 设置 self.skipped 的值，供后续业务判断、查询或响应组装使用。
        spider.logger.info(  # 执行当前代码行对应的业务处理步骤。
            "DatabasePipeline 就绪，写入：%s", app.config["SQLALCHEMY_DATABASE_URI"]  # 保留字符串内容，作为说明文本或页面展示文案。
        )  # 结束当前多行数据结构或函数调用。

    # _city_id / _district_id 必须在 app 上下文内调用
    def _load_province_map(self, backend):  # 定义 _load_province_map 函数，集中处理这一段业务逻辑。
        """从 backend/data/province_data.csv 建「城市名 -> 省份」映射，
        给新建城市补 province；并补充链家有站但不在 CSV 的县级市/特殊地区。"""
        import csv  # 导入 csv 模块，为当前文件提供所需功能。

        mapping = {}  # 设置 mapping 的值，供后续业务判断、查询或响应组装使用。
        path = os.path.join(backend, "data", "province_data.csv")  # 把关联表纳入查询，获取跨表维度的数据。
        try:  # 开始执行可能抛出异常的代码块。
            with open(path, encoding="utf-8-sig") as fh:  # 进入上下文管理流程，自动处理资源打开和释放。
                for row in csv.DictReader(fh):  # 遍历当前数据集合，逐项完成处理。
                    prov = (row.get("省份") or "").strip()  # 设置 prov 的值，供后续业务判断、查询或响应组装使用。
                    city = (row.get("城市") or "").strip()  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
                    if prov and city:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                        mapping[city] = prov  # 设置 mapping[city 的值，供后续业务判断、查询或响应组装使用。
        except OSError:  # 捕获指定异常，并转入可控的错误处理流程。
            pass  # 保留空实现位置，表示这里暂不执行额外逻辑。
        mapping.update({  # 执行当前代码行对应的业务处理步骤。
            "江阴": "江苏", "宜兴": "江苏", "昆山": "江苏", "常熟": "江苏", "太仓": "江苏",  # 保留字符串内容，作为说明文本或页面展示文案。
            "句容": "江苏", "丹阳": "江苏", "海门": "江苏",  # 保留字符串内容，作为说明文本或页面展示文案。
            "义乌": "浙江",  # 保留字符串内容，作为说明文本或页面展示文案。
            "涿州": "河北",  # 保留字符串内容，作为说明文本或页面展示文案。
            "澄迈": "海南", "陵水": "海南", "万宁": "海南",  # 保留字符串内容，作为说明文本或页面展示文案。
            "西双版纳": "云南", "大理": "云南",  # 保留字符串内容，作为说明文本或页面展示文案。
            "凉山": "四川", "湘西": "湖南",  # 保留字符串内容，作为说明文本或页面展示文案。
        })  # 结束当前多行数据结构或函数调用。
        return mapping  # 返回处理后的结果给调用方继续使用。

    def _city_id(self, name):  # 定义 _city_id 函数，集中处理这一段业务逻辑。
        """获取或创建城市记录并返回城市编号。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        name = (name or "未知城市").strip()  # 设置 name 的值，供后续业务判断、查询或响应组装使用。
        if name in self._city_ids:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            return self._city_ids[name]  # 返回处理后的结果给调用方继续使用。
        city = self.City.query.filter_by(name=name).first()  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        if city is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            prov = self._province_of.get(name)  # 设置 prov 的值，供后续业务判断、查询或响应组装使用。
            city = self.City(name=name, province=prov)  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
            self.db.session.add(city)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            self.db.session.flush()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
        elif getattr(city, "province", None) in (None, "") and self._province_of.get(name):  # 在前一个条件不成立时，继续判断这个补充分支。
            city.province = self._province_of[name]  # 设置 city.province 的值，供后续业务判断、查询或响应组装使用。
        self._city_ids[name] = city.id  # 设置 self._city_ids[name 的值，供后续业务判断、查询或响应组装使用。
        return city.id  # 返回处理后的结果给调用方继续使用。

    def _district_id(self, city_id, name, lng=None, lat=None):  # 定义 _district_id 函数，集中处理这一段业务逻辑。
        """获取或创建区域记录并返回区域编号。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        name = (name or "未知区域").strip()  # 设置 name 的值，供后续业务判断、查询或响应组装使用。
        key = (city_id, name)  # 设置 key 的值，供后续业务判断、查询或响应组装使用。
        if key in self._district_ids:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            return self._district_ids[key]  # 返回处理后的结果给调用方继续使用。
        d = self.District.query.filter_by(city_id=city_id, name=name).first()  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        if d is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            d = self.District(city_id=city_id, name=name, lng=lng, lat=lat)  # 设置 d 的值，供后续业务判断、查询或响应组装使用。
            self.db.session.add(d)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            self.db.session.flush()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
        self._district_ids[key] = d.id  # 设置 self._district_ids[key 的值，供后续业务判断、查询或响应组装使用。
        return d.id  # 返回处理后的结果给调用方继续使用。

    def process_item(self, item, spider):  # 定义 process_item 函数，集中处理这一段业务逻辑。
        """清洗、校验或入库单条爬取房源数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        a = ItemAdapter(item)  # 设置 a 的值，供后续业务判断、查询或响应组装使用。
        url = a.get("source_url")  # 设置 url 的值，供后续业务判断、查询或响应组装使用。
        # _seen 负责本轮爬取内去重，数据库查询负责历史数据去重。
        if url and url in self._seen:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            self.skipped += 1  # 设置 self.skipped + 的值，供后续业务判断、查询或响应组装使用。
            return item  # 返回处理后的结果给调用方继续使用。

        with self.app.app_context():  # 进入上下文管理流程，自动处理资源打开和释放。
            try:  # 开始执行可能抛出异常的代码块。
                if url and self.Property.query.filter_by(source_url=url).first() is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    self._seen.add(url)  # 执行当前代码行对应的业务处理步骤。
                    self.skipped += 1  # 设置 self.skipped + 的值，供后续业务判断、查询或响应组装使用。
                    return item  # 返回处理后的结果给调用方继续使用。

                # 先解析外键归属，再把已清洗 item 映射到后端 Property 模型。
                city_id = self._city_id(a.get("city"))  # 设置 city_id 的值，供后续业务判断、查询或响应组装使用。
                district_id = self._district_id(  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
                    city_id, a.get("district"), a.get("lng"), a.get("lat")  # 执行当前代码行对应的业务处理步骤。
                )  # 结束当前多行数据结构或函数调用。
                elev = a.get("has_elevator")  # 设置 elev 的值，供后续业务判断、查询或响应组装使用。
                self.db.session.add(  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
                    self.Property(  # 执行当前代码行对应的业务处理步骤。
                        district_id=district_id,  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
                        title=a.get("title"),  # 设置 title 的值，供后续业务判断、查询或响应组装使用。
                        total_price=a.get("total_price"),  # 设置 total_price 的值，供后续业务判断、查询或响应组装使用。
                        unit_price=a.get("unit_price"),  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
                        area=a.get("area"),  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
                        rooms=a.get("rooms") or 0,  # 设置 rooms 的值，供后续业务判断、查询或响应组装使用。
                        halls=a.get("halls") or 0,  # 设置 halls 的值，供后续业务判断、查询或响应组装使用。
                        floor=a.get("floor"),  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
                        total_floors=a.get("total_floors"),  # 设置 total_floors 的值，供后续业务判断、查询或响应组装使用。
                        build_year=a.get("build_year"),  # 设置 build_year 的值，供后续业务判断、查询或响应组装使用。
                        orientation=a.get("orientation"),  # 设置 orientation 的值，供后续业务判断、查询或响应组装使用。
                        decoration=a.get("decoration"),  # 设置 decoration 的值，供后续业务判断、查询或响应组装使用。
                        has_elevator=bool(elev) if elev is not None else False,  # 设置 has_elevator 的值，供后续业务判断、查询或响应组装使用。
                        listing_type=a.get("listing_type") or "二手房",  # 设置 listing_type 的值，供后续业务判断、查询或响应组装使用。
                        lng=a.get("lng"),  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
                        lat=a.get("lat"),  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。
                        source=a.get("source") or "lianjia",  # 设置 source 的值，供后续业务判断、查询或响应组装使用。
                        source_url=url,  # 设置 source_url 的值，供后续业务判断、查询或响应组装使用。
                    )  # 结束当前多行数据结构或函数调用。
                )  # 结束当前多行数据结构或函数调用。
                self.db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            except Exception:  # 捕获指定异常，并转入可控的错误处理流程。
                self.db.session.rollback()  # 执行当前代码行对应的业务处理步骤。
                # 回滚后清空 id 缓存，避免引用未提交的城市/区
                self._city_ids.clear()  # 执行当前代码行对应的业务处理步骤。
                self._district_ids.clear()  # 执行当前代码行对应的业务处理步骤。
                spider.logger.exception("写入失败，已跳过：%s", url)  # 执行当前代码行对应的业务处理步骤。
                return item  # 返回处理后的结果给调用方继续使用。

        self._seen.add(url)  # 执行当前代码行对应的业务处理步骤。
        self.added += 1  # 设置 self.added + 的值，供后续业务判断、查询或响应组装使用。
        if self.added % 20 == 0:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            spider.logger.info("已写入 %d 条 ...", self.added)  # 执行当前代码行对应的业务处理步骤。
        return item  # 返回处理后的结果给调用方继续使用。

    def close_spider(self, spider):  # 定义 close_spider 函数，集中处理这一段业务逻辑。
        """爬虫关闭时提交剩余事务并释放数据库连接。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        spider.logger.info(  # 执行当前代码行对应的业务处理步骤。
            "入库完成：新增 %d 条，跳过(重复) %d 条。", self.added, self.skipped  # 保留字符串内容，作为说明文本或页面展示文案。
        )  # 结束当前多行数据结构或函数调用。
