"""Item 管道：
1) CleanValidatePipeline —— 类型转换、单价兜底推算、字段截断、丢弃无效条目；
2) DatabasePipeline —— 复用后端 Flask 应用与 SQLAlchemy 模型写入 Property 表，
   自动 get_or_create 城市/行政区，按 source_url 去重。
"""
import os  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
import sys  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from itemadapter import ItemAdapter  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from scrapy.exceptions import DropItem  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


def _to_float(v):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """将输入值安全转换为浮点数。"""
    try:  # 开始执行可能失败的外部访问、数据转换或数据库操作。
        return float(v) if v not in (None, "") else None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    except (ValueError, TypeError):  # 捕获异常并转换为可控的错误处理或提示信息。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _to_int(v):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """将输入值安全转换为整数。"""
    f = _to_float(v)  # 计算或更新f中间数据，作为后续业务判断、统计或响应组装的输入。
    return int(f) if f is not None else None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _truncate(s, n):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """按最大长度截断字符串并保留空值语义。"""
    if s is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    s = str(s).strip()  # 计算或更新s中间数据，作为后续业务判断、统计或响应组装的输入。
    return s[:n] if s else None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


class CleanValidatePipeline:  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """类型转换 + 单价兜底 + 必要字段校验。"""

    def process_item(self, item, spider):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """清洗、校验或入库单条爬取房源数据。"""
        a = ItemAdapter(item)  # 计算或更新a中间数据，作为后续业务判断、统计或响应组装的输入。

        # 页面解析出的 item 字段都是弱类型文本，入库前先统一转换成价格、面积、楼层等数值。
        a["total_price"] = _to_float(a.get("total_price"))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        a["unit_price"] = _to_float(a.get("unit_price"))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        a["area"] = _to_float(a.get("area"))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        for f in ("rooms", "halls", "floor", "total_floors", "build_year"):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            a[f] = _to_int(a.get(f))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        # 单价缺失则用 总价(万元)/面积 反推为 元/㎡
        if not a.get("unit_price") and a.get("total_price") and a.get("area"):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            a["unit_price"] = a["total_price"] * 10000 / a["area"]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        if a.get("unit_price"):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            a["unit_price"] = round(a["unit_price"])  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        # 截断到数据库列长度，避免 MySQL 严格模式报错
        a["title"] = _truncate(a.get("title"), 200)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        a["orientation"] = _truncate(a.get("orientation"), 20)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        a["decoration"] = _truncate(a.get("decoration"), 20)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        a["source"] = _truncate(a.get("source"), 50)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        a["source_url"] = _truncate(a.get("source_url"), 500)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        # 标题和价格是房源展示、去重排查和后续统计的底线，缺失则直接丢弃。
        if not a.get("title") or not (a.get("unit_price") or a.get("total_price")):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            raise DropItem(f"缺少必要字段(标题/价格)：{a.get('source_url')}")  # 把无法继续处理的异常上抛，交给调用方统一响应。
        return item  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


class DatabasePipeline:  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """写入后端 Property 表；复用 backend 的应用工厂、配置与模型。

    每条 item 在独立的 ``with app.app_context()`` 内完成查询/写入，避免 Flask
    应用上下文在 Scrapy/Twisted 各回调间（contextvars）不共享的问题。城市/行政区
    按名称缓存其 **id**（而非 ORM 对象），跨上下文安全。
    """

    def open_spider(self, spider):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """爬虫启动时初始化数据库连接、建表和缓存。"""
        # 把 backend/ 加入 import 路径，复用其 Flask app / DB 配置 / 模型
        backend = os.path.abspath(  # 计算或更新backend中间数据，作为后续业务判断、统计或响应组装的输入。
            os.path.join(os.path.dirname(__file__), "..", "..", "backend")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        if backend not in sys.path:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            sys.path.insert(0, backend)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        from app import app  # 应用工厂在导入时已 create_app()（含 DB 配置与建表）
        from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
        from models import City, District, Property  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

        self.app = app  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.db = db  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.City, self.District, self.Property = City, District, Property  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        self._province_of = self._load_province_map(backend)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self._city_ids = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self._district_ids = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self._seen = set()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.added = 0  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.skipped = 0  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        spider.logger.info(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "DatabasePipeline 就绪，写入：%s", app.config["SQLALCHEMY_DATABASE_URI"]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    # _city_id / _district_id 必须在 app 上下文内调用
    def _load_province_map(self, backend):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """从 backend/data/province_data.csv 建「城市名 -> 省份」映射，
        给新建城市补 province；并补充链家有站但不在 CSV 的县级市/特殊地区。"""
        import csv  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

        mapping = {}  # 初始化mapping中间数据字典，用于承载接口返回或中间聚合结果。
        path = os.path.join(backend, "data", "province_data.csv")  # 计算或更新地图钻取路径，作为后续业务判断、统计或响应组装的输入。
        try:  # 开始执行可能失败的外部访问、数据转换或数据库操作。
            with open(path, encoding="utf-8-sig") as fh:  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
                for row in csv.DictReader(fh):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
                    prov = (row.get("省份") or "").strip()  # 计算或更新prov中间数据，作为后续业务判断、统计或响应组装的输入。
                    city = (row.get("城市") or "").strip()  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
                    if prov and city:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                        mapping[city] = prov  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        except OSError:  # 捕获异常并转换为可控的错误处理或提示信息。
            pass  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        mapping.update({  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "江阴": "江苏", "宜兴": "江苏", "昆山": "江苏", "常熟": "江苏", "太仓": "江苏",  # 把江阴字段写入响应数据，供前端页面、图表或后续接口读取。
            "句容": "江苏", "丹阳": "江苏", "海门": "江苏",  # 把句容字段写入响应数据，供前端页面、图表或后续接口读取。
            "义乌": "浙江",  # 把义乌字段写入响应数据，供前端页面、图表或后续接口读取。
            "涿州": "河北",  # 把涿州字段写入响应数据，供前端页面、图表或后续接口读取。
            "澄迈": "海南", "陵水": "海南", "万宁": "海南",  # 把澄迈字段写入响应数据，供前端页面、图表或后续接口读取。
            "西双版纳": "云南", "大理": "云南",  # 把西双版纳字段写入响应数据，供前端页面、图表或后续接口读取。
            "凉山": "四川", "湘西": "湖南",  # 把凉山字段写入响应数据，供前端页面、图表或后续接口读取。
        })  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return mapping  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    def _city_id(self, name):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """获取或创建城市记录并返回城市编号。"""
        name = (name or "未知城市").strip()  # 计算或更新name中间数据，作为后续业务判断、统计或响应组装的输入。
        if name in self._city_ids:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            return self._city_ids[name]  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        city = self.City.query.filter_by(name=name).first()  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
        if city is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            prov = self._province_of.get(name)  # 计算或更新prov中间数据，作为后续业务判断、统计或响应组装的输入。
            city = self.City(name=name, province=prov)  # 经纬度留空，可后续补全
            self.db.session.add(city)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            self.db.session.flush()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        elif getattr(city, "province", None) in (None, "") and self._province_of.get(name):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            city.province = self._province_of[name]  # 回填已存在城市缺失的省份
        self._city_ids[name] = city.id  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return city.id  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    def _district_id(self, city_id, name, lng=None, lat=None):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """获取或创建区域记录并返回区域编号。"""
        name = (name or "未知区域").strip()  # 计算或更新name中间数据，作为后续业务判断、统计或响应组装的输入。
        key = (city_id, name)  # 计算或更新key中间数据，作为后续业务判断、统计或响应组装的输入。
        if key in self._district_ids:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            return self._district_ids[key]  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        d = self.District.query.filter_by(city_id=city_id, name=name).first()  # 计算或更新d中间数据，作为后续业务判断、统计或响应组装的输入。
        if d is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            d = self.District(city_id=city_id, name=name, lng=lng, lat=lat)  # 计算或更新d中间数据，作为后续业务判断、统计或响应组装的输入。
            self.db.session.add(d)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            self.db.session.flush()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self._district_ids[key] = d.id  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return d.id  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    def process_item(self, item, spider):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """清洗、校验或入库单条爬取房源数据。"""
        a = ItemAdapter(item)  # 计算或更新a中间数据，作为后续业务判断、统计或响应组装的输入。
        url = a.get("source_url")  # 计算或更新url中间数据，作为后续业务判断、统计或响应组装的输入。
        # _seen 负责本轮爬取内去重，数据库查询负责历史数据去重。
        if url and url in self._seen:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            self.skipped += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            return item  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

        with self.app.app_context():  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
            try:  # 开始执行可能失败的外部访问、数据转换或数据库操作。
                if url and self.Property.query.filter_by(source_url=url).first() is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                    self._seen.add(url)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                    self.skipped += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                    return item  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

                # 先解析外键归属，再把已清洗 item 映射到后端 Property 模型。
                city_id = self._city_id(a.get("city"))  # 计算或更新城市编号，作为后续业务判断、统计或响应组装的输入。
                district_id = self._district_id(  # 计算或更新行政区编号，作为后续业务判断、统计或响应组装的输入。
                    city_id, a.get("district"), a.get("lng"), a.get("lat")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
                elev = a.get("has_elevator")  # 计算或更新elev中间数据，作为后续业务判断、统计或响应组装的输入。
                self.db.session.add(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                    self.Property(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                        district_id=district_id,  # 计算或更新行政区编号，作为后续业务判断、统计或响应组装的输入。
                        title=a.get("title"),  # 计算或更新title中间数据，作为后续业务判断、统计或响应组装的输入。
                        total_price=a.get("total_price"),  # 计算或更新total_price中间数据，作为后续业务判断、统计或响应组装的输入。
                        unit_price=a.get("unit_price"),  # 计算或更新unit_price中间数据，作为后续业务判断、统计或响应组装的输入。
                        area=a.get("area"),  # 计算或更新area中间数据，作为后续业务判断、统计或响应组装的输入。
                        rooms=a.get("rooms") or 0,  # 计算或更新rooms中间数据，作为后续业务判断、统计或响应组装的输入。
                        halls=a.get("halls") or 0,  # 计算或更新halls中间数据，作为后续业务判断、统计或响应组装的输入。
                        floor=a.get("floor"),  # 计算或更新floor中间数据，作为后续业务判断、统计或响应组装的输入。
                        total_floors=a.get("total_floors"),  # 计算或更新total_floors中间数据，作为后续业务判断、统计或响应组装的输入。
                        build_year=a.get("build_year"),  # 计算或更新build_year中间数据，作为后续业务判断、统计或响应组装的输入。
                        orientation=a.get("orientation"),  # 计算或更新orientation中间数据，作为后续业务判断、统计或响应组装的输入。
                        decoration=a.get("decoration"),  # 计算或更新decoration中间数据，作为后续业务判断、统计或响应组装的输入。
                        has_elevator=bool(elev) if elev is not None else False,  # 计算或更新has_elevator中间数据，作为后续业务判断、统计或响应组装的输入。
                        listing_type=a.get("listing_type") or "二手房",  # 计算或更新listing_type中间数据，作为后续业务判断、统计或响应组装的输入。
                        lng=a.get("lng"),  # 计算或更新lng中间数据，作为后续业务判断、统计或响应组装的输入。
                        lat=a.get("lat"),  # 计算或更新lat中间数据，作为后续业务判断、统计或响应组装的输入。
                        source=a.get("source") or "lianjia",  # 计算或更新source中间数据，作为后续业务判断、统计或响应组装的输入。
                        source_url=url,  # 计算或更新source_url中间数据，作为后续业务判断、统计或响应组装的输入。
                    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
                )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
                self.db.session.commit()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            except Exception:  # 捕获异常并转换为可控的错误处理或提示信息。
                self.db.session.rollback()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                # 回滚后清空 id 缓存，避免引用未提交的城市/区
                self._city_ids.clear()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                self._district_ids.clear()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                spider.logger.exception("写入失败，已跳过：%s", url)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                return item  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

        self._seen.add(url)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.added += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        if self.added % 20 == 0:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            spider.logger.info("已写入 %d 条 ...", self.added)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return item  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    def close_spider(self, spider):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """爬虫关闭时提交剩余事务并释放数据库连接。"""
        spider.logger.info(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "入库完成：新增 %d 条，跳过(重复) %d 条。", self.added, self.skipped  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
