"""爬虫基类：封装「礼貌请求」与「解析→入库」的通用流程。"""
import time
from typing import Iterable

import requests

from extensions import db
from models import City, District, Property

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HousingPlatform-EduCrawler/1.0)",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


class BaseSpider:
    """Subclass and implement :meth:`parse`.

    The lifecycle is ``fetch -> parse -> persist``. ``parse`` should return an
    iterable of plain dicts; :meth:`persist` maps them onto ORM rows, creating
    the City / District on demand.
    """

    source_name = "base"

    def __init__(self, delay: float = 1.5, headers: dict | None = None):
        self.delay = delay  # seconds between requests — be polite
        self.session = requests.Session()
        self.session.headers.update(headers or DEFAULT_HEADERS)

    # --- network ---------------------------------------------------------
    def fetch(self, url: str, **kwargs) -> str:
        resp = self.session.get(url, timeout=10, **kwargs)
        resp.raise_for_status()
        time.sleep(self.delay)  # rate-limit
        return resp.text

    # --- to be implemented by subclasses ---------------------------------
    def parse(self, html: str) -> Iterable[dict]:  # pragma: no cover - abstract
        raise NotImplementedError

    # --- persistence -----------------------------------------------------
    def persist(self, records: Iterable[dict], city_name: str, province: str = "") -> int:
        """Insert parsed records, creating City/District rows as needed.

        Each record dict may contain: title, district, total_price, unit_price,
        area, rooms, halls, floor, total_floors, build_year, orientation,
        decoration, has_elevator, listing_type, source_url.
        """
        city = db.session.query(City).filter_by(name=city_name).first()
        if not city:
            city = City(name=city_name, province=province)
            db.session.add(city)
            db.session.flush()

        district_cache: dict[str, District] = {}
        inserted = 0
        for rec in records:
            dname = rec.get("district") or "未知"
            district = district_cache.get(dname)
            if not district:
                district = (
                    db.session.query(District)
                    .filter_by(city_id=city.id, name=dname)
                    .first()
                )
                if not district:
                    district = District(city_id=city.id, name=dname)
                    db.session.add(district)
                    db.session.flush()
                district_cache[dname] = district

            db.session.add(
                Property(
                    district_id=district.id,
                    title=rec.get("title", ""),
                    total_price=rec.get("total_price"),
                    unit_price=rec.get("unit_price"),
                    area=rec.get("area"),
                    rooms=rec.get("rooms", 0),
                    halls=rec.get("halls", 0),
                    floor=rec.get("floor"),
                    total_floors=rec.get("total_floors"),
                    build_year=rec.get("build_year"),
                    orientation=rec.get("orientation"),
                    decoration=rec.get("decoration"),
                    has_elevator=rec.get("has_elevator", False),
                    listing_type=rec.get("listing_type", "二手房"),
                    source=self.source_name,
                    source_url=rec.get("source_url"),
                )
            )
            inserted += 1

        db.session.commit()
        return inserted
