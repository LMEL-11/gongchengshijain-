"""爬虫基类：封装「礼貌请求」与「解析→入库」的通用流程。"""
import time  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from typing import Iterable  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

import requests  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import City, District, Property  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

DEFAULT_HEADERS = {  # 初始化DEFAULT_HEADERS中间数据字典，用于承载接口返回或中间聚合结果。
    "User-Agent": "Mozilla/5.0 (compatible; HousingPlatform-EduCrawler/1.0)",  # 把User-Agent字段写入响应数据，供前端页面、图表或后续接口读取。
    "Accept-Language": "zh-CN,zh;q=0.9",  # 把Accept-Language字段写入响应数据，供前端页面、图表或后续接口读取。
}  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


class BaseSpider:  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """Subclass and implement :meth:`parse`.

    The lifecycle is ``fetch -> parse -> persist``. ``parse`` should return an
    iterable of plain dicts; :meth:`persist` maps them onto ORM rows, creating
    the City / District on demand.
    """

    source_name = "base"  # 计算或更新source_name中间数据，作为后续业务判断、统计或响应组装的输入。

    def __init__(self, delay: float = 1.5, headers: dict | None = None):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """初始化爬虫实例并保存运行参数。"""
        self.delay = delay  # seconds between requests — be polite
        self.session = requests.Session()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.session.headers.update(headers or DEFAULT_HEADERS)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    # --- network ---------------------------------------------------------
    def fetch(self, url: str, **kwargs) -> str:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """发送 HTTP 请求并返回响应文本。"""
        resp = self.session.get(url, timeout=10, **kwargs)  # 计算或更新resp中间数据，作为后续业务判断、统计或响应组装的输入。
        resp.raise_for_status()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        time.sleep(self.delay)  # rate-limit
        return resp.text  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    # --- to be implemented by subclasses ---------------------------------
    def parse(self, html: str) -> Iterable[dict]:  # pragma: no cover - abstract
        """解析页面文本并产出结构化结果。"""
        raise NotImplementedError  # 把无法继续处理的异常上抛，交给调用方统一响应。

    # --- persistence -----------------------------------------------------
    def persist(self, records: Iterable[dict], city_name: str, province: str = "") -> int:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """Insert parsed records, creating City/District rows as needed.

        Each record dict may contain: title, district, total_price, unit_price,
        area, rooms, halls, floor, total_floors, build_year, orientation,
        decoration, has_elevator, listing_type, source_url.
        """
        city = db.session.query(City).filter_by(name=city_name).first()  # 创建city中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
        if not city:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            city = City(name=city_name, province=province)  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
            db.session.add(city)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            db.session.flush()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。

        district_cache: dict[str, District] = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        inserted = 0  # 计算或更新inserted中间数据，作为后续业务判断、统计或响应组装的输入。
        for rec in records:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            dname = rec.get("district") or "未知"  # 计算或更新dname中间数据，作为后续业务判断、统计或响应组装的输入。
            district = district_cache.get(dname)  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
            if not district:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                district = (  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
                    db.session.query(District)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                    .filter_by(city_id=city.id, name=dname)  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
                    .first()  # 执行查询并取回结果，作为后续数据转换的输入。
                )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
                if not district:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                    district = District(city_id=city.id, name=dname)  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
                    db.session.add(district)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
                    db.session.flush()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
                district_cache[dname] = district  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

            db.session.add(  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
                Property(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                    district_id=district.id,  # 计算或更新行政区编号，作为后续业务判断、统计或响应组装的输入。
                    title=rec.get("title", ""),  # 计算或更新title中间数据，作为后续业务判断、统计或响应组装的输入。
                    total_price=rec.get("total_price"),  # 计算或更新total_price中间数据，作为后续业务判断、统计或响应组装的输入。
                    unit_price=rec.get("unit_price"),  # 计算或更新unit_price中间数据，作为后续业务判断、统计或响应组装的输入。
                    area=rec.get("area"),  # 计算或更新area中间数据，作为后续业务判断、统计或响应组装的输入。
                    rooms=rec.get("rooms", 0),  # 计算或更新rooms中间数据，作为后续业务判断、统计或响应组装的输入。
                    halls=rec.get("halls", 0),  # 计算或更新halls中间数据，作为后续业务判断、统计或响应组装的输入。
                    floor=rec.get("floor"),  # 计算或更新floor中间数据，作为后续业务判断、统计或响应组装的输入。
                    total_floors=rec.get("total_floors"),  # 计算或更新total_floors中间数据，作为后续业务判断、统计或响应组装的输入。
                    build_year=rec.get("build_year"),  # 计算或更新build_year中间数据，作为后续业务判断、统计或响应组装的输入。
                    orientation=rec.get("orientation"),  # 计算或更新orientation中间数据，作为后续业务判断、统计或响应组装的输入。
                    decoration=rec.get("decoration"),  # 计算或更新decoration中间数据，作为后续业务判断、统计或响应组装的输入。
                    has_elevator=rec.get("has_elevator", False),  # 计算或更新has_elevator中间数据，作为后续业务判断、统计或响应组装的输入。
                    listing_type=rec.get("listing_type", "二手房"),  # 计算或更新listing_type中间数据，作为后续业务判断、统计或响应组装的输入。
                    source=self.source_name,  # 计算或更新source中间数据，作为后续业务判断、统计或响应组装的输入。
                    source_url=rec.get("source_url"),  # 计算或更新source_url中间数据，作为后续业务判断、统计或响应组装的输入。
                )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            inserted += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
        return inserted  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
