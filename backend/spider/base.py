"""爬虫基类：封装「礼貌请求」与「解析→入库」的通用流程。"""
import time  # 导入本行所需的模块或对象。
from typing import Iterable  # 导入本行所需的模块或对象。

import requests  # 导入本行所需的模块或对象。

from extensions import db  # 导入本行所需的模块或对象。
from models import City, District, Property  # 导入本行所需的模块或对象。

DEFAULT_HEADERS = {  # 赋值或更新当前变量/字段。
    "User-Agent": "Mozilla/5.0 (compatible; HousingPlatform-EduCrawler/1.0)",  # 设置当前数据项或参数。
    "Accept-Language": "zh-CN,zh;q=0.9",  # 赋值或更新当前变量/字段。
}  # 结束当前数据结构或调用块。


class BaseSpider:  # 声明类并定义相关数据或行为。
    """Subclass and implement :meth:`parse`.

    The lifecycle is ``fetch -> parse -> persist``. ``parse`` should return an
    iterable of plain dicts; :meth:`persist` maps them onto ORM rows, creating
    the City / District on demand.
    """

    source_name = "base"  # 赋值或更新当前变量/字段。

    def __init__(self, delay: float = 1.5, headers: dict | None = None):  # 声明函数或方法入口。
        """初始化爬虫实例并保存运行参数。"""
        self.delay = delay  # seconds between requests — be polite
        self.session = requests.Session()  # 赋值或更新当前变量/字段。
        self.session.headers.update(headers or DEFAULT_HEADERS)  # 执行本行代码逻辑。

    # --- network ---------------------------------------------------------
    def fetch(self, url: str, **kwargs) -> str:  # 声明函数或方法入口。
        """发送 HTTP 请求并返回响应文本。"""
        resp = self.session.get(url, timeout=10, **kwargs)  # 赋值或更新当前变量/字段。
        resp.raise_for_status()  # 执行本行代码逻辑。
        time.sleep(self.delay)  # rate-limit
        return resp.text  # 返回当前逻辑的处理结果。

    # --- to be implemented by subclasses ---------------------------------
    def parse(self, html: str) -> Iterable[dict]:  # pragma: no cover - abstract
        """解析页面文本并产出结构化结果。"""
        raise NotImplementedError  # 抛出异常并交由上层处理。

    # --- persistence -----------------------------------------------------
    def persist(self, records: Iterable[dict], city_name: str, province: str = "") -> int:  # 声明函数或方法入口。
        """Insert parsed records, creating City/District rows as needed.

        Each record dict may contain: title, district, total_price, unit_price,
        area, rooms, halls, floor, total_floors, build_year, orientation,
        decoration, has_elevator, listing_type, source_url.
        """
        city = db.session.query(City).filter_by(name=city_name).first()  # 赋值或更新当前变量/字段。
        if not city:  # 根据条件判断是否进入该分支。
            city = City(name=city_name, province=province)  # 赋值或更新当前变量/字段。
            db.session.add(city)  # 把对象加入数据库会话等待提交。
            db.session.flush()  # 执行本行代码逻辑。

        district_cache: dict[str, District] = {}  # 赋值或更新当前变量/字段。
        inserted = 0  # 赋值或更新当前变量/字段。
        for rec in records:  # 遍历集合中的每一项并执行处理。
            dname = rec.get("district") or "未知"  # 赋值或更新当前变量/字段。
            district = district_cache.get(dname)  # 赋值或更新当前变量/字段。
            if not district:  # 根据条件判断是否进入该分支。
                district = (  # 赋值或更新当前变量/字段。
                    db.session.query(District)  # 执行本行代码逻辑。
                    .filter_by(city_id=city.id, name=dname)  # 赋值或更新当前变量/字段。
                    .first()  # 执行本行代码逻辑。
                )  # 结束当前数据结构或调用块。
                if not district:  # 根据条件判断是否进入该分支。
                    district = District(city_id=city.id, name=dname)  # 赋值或更新当前变量/字段。
                    db.session.add(district)  # 把对象加入数据库会话等待提交。
                    db.session.flush()  # 执行本行代码逻辑。
                district_cache[dname] = district  # 赋值或更新当前变量/字段。

            db.session.add(  # 把对象加入数据库会话等待提交。
                Property(  # 执行本行代码逻辑。
                    district_id=district.id,  # 赋值或更新当前变量/字段。
                    title=rec.get("title", ""),  # 赋值或更新当前变量/字段。
                    total_price=rec.get("total_price"),  # 赋值或更新当前变量/字段。
                    unit_price=rec.get("unit_price"),  # 赋值或更新当前变量/字段。
                    area=rec.get("area"),  # 赋值或更新当前变量/字段。
                    rooms=rec.get("rooms", 0),  # 赋值或更新当前变量/字段。
                    halls=rec.get("halls", 0),  # 赋值或更新当前变量/字段。
                    floor=rec.get("floor"),  # 赋值或更新当前变量/字段。
                    total_floors=rec.get("total_floors"),  # 赋值或更新当前变量/字段。
                    build_year=rec.get("build_year"),  # 赋值或更新当前变量/字段。
                    orientation=rec.get("orientation"),  # 赋值或更新当前变量/字段。
                    decoration=rec.get("decoration"),  # 赋值或更新当前变量/字段。
                    has_elevator=rec.get("has_elevator", False),  # 赋值或更新当前变量/字段。
                    listing_type=rec.get("listing_type", "二手房"),  # 赋值或更新当前变量/字段。
                    source=self.source_name,  # 赋值或更新当前变量/字段。
                    source_url=rec.get("source_url"),  # 赋值或更新当前变量/字段。
                )  # 结束当前数据结构或调用块。
            )  # 结束当前数据结构或调用块。
            inserted += 1  # 赋值或更新当前变量/字段。

        db.session.commit()  # 提交当前数据库事务。
        return inserted  # 返回当前逻辑的处理结果。
