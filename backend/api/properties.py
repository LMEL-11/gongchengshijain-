"""房源相关接口 /api/properties"""
from flask import Blueprint, abort, request

from extensions import db
from models import District, Facility, Property
from services.property_details import get_property_transaction_details

from .utils import get_float, get_int, ok

bp = Blueprint("properties", __name__, url_prefix="/api/properties")

_SORTS = {
    "price_asc": Property.total_price.asc(),
    "price_desc": Property.total_price.desc(),
    "unit_asc": Property.unit_price.asc(),
    "unit_desc": Property.unit_price.desc(),
    "area_desc": Property.area.desc(),
    "newest": Property.created_at.desc(),
}


@bp.get("")
def list_properties():
    """Filterable, sortable, paginated listing search."""
    query = db.session.query(Property).join(District, Property.district_id == District.id)

    city_id = get_int("city_id")
    district_id = get_int("district_id")
    listing_type = request.args.get("listing_type")
    keyword = (request.args.get("keyword") or "").strip()
    rooms = get_int("rooms")
    min_total = get_float("min_total_price")
    max_total = get_float("max_total_price")
    min_unit = get_float("min_unit_price")
    max_unit = get_float("max_unit_price")

    if city_id:
        query = query.filter(District.city_id == city_id)
    if district_id:
        query = query.filter(Property.district_id == district_id)
    if listing_type:
        query = query.filter(Property.listing_type == listing_type)
    if keyword:
        query = query.filter(Property.title.like(f"%{keyword}%"))
    if rooms is not None:
        # rooms>=4 treated as "4室及以上"
        query = query.filter(Property.rooms >= 4) if rooms >= 4 else query.filter(Property.rooms == rooms)
    if min_total is not None:
        query = query.filter(Property.total_price >= min_total)
    if max_total is not None:
        query = query.filter(Property.total_price <= max_total)
    if min_unit is not None:
        query = query.filter(Property.unit_price >= min_unit)
    if max_unit is not None:
        query = query.filter(Property.unit_price <= max_unit)

    query = query.order_by(_SORTS.get(request.args.get("sort", "newest"), Property.created_at.desc()))

    page = max(get_int("page", 1), 1)
    page_size = min(max(get_int("page_size", 12), 1), 100)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return ok(
        {
            "items": [p.to_dict() for p in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        }
    )


@bp.get("/<int:property_id>")
def get_property(property_id: int):
    """查询单个房源详情，找不到时返回 404。"""
    prop = db.session.get(Property, property_id)
    if not prop:
        abort(404)
    facilities = (
        db.session.query(Facility)
        .filter(Facility.district_id == prop.district_id)
        .all()
    )
    data = prop.to_dict(detail=True)
    data["facilities"] = [f.to_dict() for f in facilities]
    data["transaction"] = get_property_transaction_details(prop)
    return ok(data)
