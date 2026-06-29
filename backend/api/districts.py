"""行政区相关接口 /api/districts"""
from flask import Blueprint, abort

from extensions import db
from models import District, Facility
from services import analysis

from .utils import ok

bp = Blueprint("districts", __name__, url_prefix="/api/districts")


@bp.get("/<int:district_id>")
def get_district(district_id: int):
    """按编号查询区域详情，找不到时返回 404。"""
    district = db.session.get(District, district_id)
    if not district:
        abort(404)
    return ok(district.to_dict())


@bp.get("/<int:district_id>/facilities")
def district_facilities(district_id: int):
    """返回指定区域周边配套设施列表。"""
    if not db.session.get(District, district_id):
        abort(404)
    rows = (
        db.session.query(Facility)
        .filter(Facility.district_id == district_id)
        .all()
    )
    return ok([f.to_dict() for f in rows])


@bp.get("/<int:district_id>/price-trend")
def district_price_trend(district_id: int):
    """返回指定区域的房价历史趋势数据。"""
    if not db.session.get(District, district_id):
        abort(404)
    return ok(analysis.price_trend(district_id))
