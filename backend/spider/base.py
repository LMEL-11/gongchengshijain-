"""爬虫基类：封装「礼貌请求」与「解析→入库」的通用流程。"""  # 保留字符串内容，作为说明文本或页面展示文案。
import time  # 导入 time 模块，为当前文件提供所需功能。
from typing import Iterable  # 从 typing 导入 Iterable，供本文件后续逻辑调用。

import requests  # 导入 requests 模块，为当前文件提供所需功能。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import City, District, Property  # 从 models 导入 City, District, Property，供本文件后续逻辑调用。

DEFAULT_HEADERS = {  # 设置 DEFAULT_HEADERS 的值，供后续业务判断、查询或响应组装使用。
    "User-Agent": "Mozilla/5.0 (compatible; HousingPlatform-EduCrawler/1.0)",  # 保留字符串内容，作为说明文本或页面展示文案。
    "Accept-Language": "zh-CN,zh;q=0.9",  # 设置 "Accept-Language": "zh-CN,zh;q 的值，供后续业务判断、查询或响应组装使用。
}  # 结束当前多行数据结构或函数调用。


class BaseSpider:  # 定义 BaseSpider 类，封装对应的数据结构或业务行为。
    """Subclass and implement :meth:`parse`.

    The lifecycle is ``fetch -> parse -> persist``. ``parse`` should return an
    iterable of plain dicts; :meth:`persist` maps them onto ORM rows, creating
    the City / District on demand.
    """

    source_name = "base"  # 设置 source_name 的值，供后续业务判断、查询或响应组装使用。

    def __init__(self, delay: float = 1.5, headers: dict | None = None):  # 定义 __init__ 函数，集中处理这一段业务逻辑。
        """初始化爬虫实例并保存运行参数。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        self.delay = delay  # 设置 self.delay 的值，供后续业务判断、查询或响应组装使用。
        self.session = requests.Session()  # 设置 self.session 的值，供后续业务判断、查询或响应组装使用。
        self.session.headers.update(headers or DEFAULT_HEADERS)  # 执行当前代码行对应的业务处理步骤。

    # --- network ---------------------------------------------------------
    def fetch(self, url: str, **kwargs) -> str:  # 定义 fetch 函数，集中处理这一段业务逻辑。
        """发送 HTTP 请求并返回响应文本。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        resp = self.session.get(url, timeout=10, **kwargs)  # 设置 resp 的值，供后续业务判断、查询或响应组装使用。
        resp.raise_for_status()  # 执行当前代码行对应的业务处理步骤。
        time.sleep(self.delay)  # 执行当前代码行对应的业务处理步骤。
        return resp.text  # 返回处理后的结果给调用方继续使用。

    # --- to be implemented by subclasses ---------------------------------
    def parse(self, html: str) -> Iterable[dict]:  # pragma: no cover - abstract
        """解析页面文本并产出结构化结果。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        raise NotImplementedError  # 主动抛出异常，提示当前流程无法继续。

    # --- persistence -----------------------------------------------------
    def persist(self, records: Iterable[dict], city_name: str, province: str = "") -> int:  # 定义 persist 函数，集中处理这一段业务逻辑。
        """Insert parsed records, creating City/District rows as needed.

        Each record dict may contain: title, district, total_price, unit_price,
        area, rooms, halls, floor, total_floors, build_year, orientation,
        decoration, has_elevator, listing_type, source_url.
        """
        city = db.session.query(City).filter_by(name=city_name).first()  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        if not city:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            city = City(name=city_name, province=province)  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
            db.session.add(city)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            db.session.flush()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。

        district_cache: dict[str, District] = {}  # 设置 district_cache: dict[str, District 的值，供后续业务判断、查询或响应组装使用。
        inserted = 0  # 设置 inserted 的值，供后续业务判断、查询或响应组装使用。
        for rec in records:  # 遍历当前数据集合，逐项完成处理。
            dname = rec.get("district") or "未知"  # 设置 dname 的值，供后续业务判断、查询或响应组装使用。
            district = district_cache.get(dname)  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
            if not district:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                district = (  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
                    db.session.query(District)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
                    .filter_by(city_id=city.id, name=dname)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
                    .first()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
                )  # 结束当前多行数据结构或函数调用。
                if not district:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    district = District(city_id=city.id, name=dname)  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
                    db.session.add(district)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
                    db.session.flush()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
                district_cache[dname] = district  # 设置 district_cache[dname 的值，供后续业务判断、查询或响应组装使用。

            db.session.add(  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
                Property(  # 执行当前代码行对应的业务处理步骤。
                    district_id=district.id,  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
                    title=rec.get("title", ""),  # 设置 title 的值，供后续业务判断、查询或响应组装使用。
                    total_price=rec.get("total_price"),  # 设置 total_price 的值，供后续业务判断、查询或响应组装使用。
                    unit_price=rec.get("unit_price"),  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
                    area=rec.get("area"),  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
                    rooms=rec.get("rooms", 0),  # 设置 rooms 的值，供后续业务判断、查询或响应组装使用。
                    halls=rec.get("halls", 0),  # 设置 halls 的值，供后续业务判断、查询或响应组装使用。
                    floor=rec.get("floor"),  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
                    total_floors=rec.get("total_floors"),  # 设置 total_floors 的值，供后续业务判断、查询或响应组装使用。
                    build_year=rec.get("build_year"),  # 设置 build_year 的值，供后续业务判断、查询或响应组装使用。
                    orientation=rec.get("orientation"),  # 设置 orientation 的值，供后续业务判断、查询或响应组装使用。
                    decoration=rec.get("decoration"),  # 设置 decoration 的值，供后续业务判断、查询或响应组装使用。
                    has_elevator=rec.get("has_elevator", False),  # 设置 has_elevator 的值，供后续业务判断、查询或响应组装使用。
                    listing_type=rec.get("listing_type", "二手房"),  # 设置 listing_type 的值，供后续业务判断、查询或响应组装使用。
                    source=self.source_name,  # 设置 source 的值，供后续业务判断、查询或响应组装使用。
                    source_url=rec.get("source_url"),  # 设置 source_url 的值，供后续业务判断、查询或响应组装使用。
                )  # 结束当前多行数据结构或函数调用。
            )  # 结束当前多行数据结构或函数调用。
            inserted += 1  # 设置 inserted + 的值，供后续业务判断、查询或响应组装使用。

        db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
        return inserted  # 返回处理后的结果给调用方继续使用。
