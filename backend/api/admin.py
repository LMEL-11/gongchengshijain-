"""管理后台蓝图 —— 房源 CRUD（仅管理员可访问）。"""
import math

from flask import Blueprint, abort, jsonify, request

from extensions import db
from models import District, Property, PropertyTransaction
from services.property_details import get_property_transaction_details
from .decorators import admin_required
from .utils import get_float, get_int, ok

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

TRANSACTION_FIELDS = (
    "listing_date",
    "ownership_type",
    "property_right",
    "mortgage",
    "selling_point",
    "community_intro",
    "layout_intro",
    "transport_intro",
)


def _clean_text(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _transaction_payload(body):
    return {field: _clean_text(body.get(field)) for field in TRANSACTION_FIELDS}


def _sync_transaction(prop, body):
    if not any(field in body for field in TRANSACTION_FIELDS):
        return

    payload = _transaction_payload(body)
    if not any(payload.values()):
        if prop.transaction:
            db.session.delete(prop.transaction)
        return

    if not prop.transaction:
        prop.transaction = PropertyTransaction()
    for field, value in payload.items():
        setattr(prop.transaction, field, value)


def _property_dict(prop):
    data = prop.to_dict(detail=True)
    data["transaction"] = get_property_transaction_details(prop)
    return data


@bp.get("/properties")
@admin_required
def list_properties():
    page = max(get_int("page", 1), 1)
    page_size = min(max(get_int("page_size", 20), 1), 100)
    keyword = (request.args.get("keyword") or "").strip()
    district_id = get_int("district_id")

    q = db.session.query(Property)
    if district_id:
        q = q.filter(Property.district_id == district_id)
    if keyword:
        q = q.filter(Property.title.contains(keyword))

    total = q.count()
    pages = max(math.ceil(total / page_size), 1)
    items = (
        q.order_by(Property.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ok(
        {
            "items": [_property_dict(p) for p in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }
    )


@bp.get("/properties/<int:id>")
@admin_required
def get_property(id):
    prop = db.session.get(Property, id)
    if prop is None:
        abort(404)
    return ok(_property_dict(prop))


@bp.post("/properties")
@admin_required
def create_property():
    body = request.get_json(silent=True) or {}

    title = (body.get("title") or "").strip()
    if not title:
        return jsonify(code=1, message="房源标题不能为空"), 400

    district_id = body.get("district_id")
    if not district_id or db.session.get(District, district_id) is None:
        return jsonify(code=1, message="所属区域无效"), 400

    prop = Property(
        district_id=district_id,
        title=title,
        total_price=body.get("total_price"),
        unit_price=body.get("unit_price"),
        area=body.get("area"),
        rooms=body.get("rooms", 0),
        halls=body.get("halls", 0),
        floor=body.get("floor"),
        total_floors=body.get("total_floors"),
        build_year=body.get("build_year"),
        orientation=body.get("orientation", ""),
        decoration=body.get("decoration", ""),
        has_elevator=body.get("has_elevator", False),
        listing_type=body.get("listing_type", "二手房"),
        lng=body.get("lng"),
        lat=body.get("lat"),
        source=body.get("source", "manual"),
        source_url=body.get("source_url", ""),
    )
    db.session.add(prop)
    _sync_transaction(prop, body)
    db.session.commit()
    return ok(_property_dict(prop)), 201


@bp.put("/properties/<int:id>")
@admin_required
def update_property(id):
    prop = db.session.get(Property, id)
    if prop is None:
        abort(404)

    body = request.get_json(silent=True) or {}

    if "title" in body:
        title = (body["title"] or "").strip()
        if not title:
            return jsonify(code=1, message="房源标题不能为空"), 400
        prop.title = title

    if "district_id" in body:
        did = body["district_id"]
        if db.session.get(District, did) is None:
            return jsonify(code=1, message="所属区域无效"), 400
        prop.district_id = did

    # Numeric / string / bool fields — only update when present
    for field in (
        "total_price",
        "unit_price",
        "area",
        "rooms",
        "halls",
        "floor",
        "total_floors",
        "build_year",
        "orientation",
        "decoration",
        "has_elevator",
        "listing_type",
        "lng",
        "lat",
        "source",
        "source_url",
    ):
        if field in body:
            setattr(prop, field, body[field])

    _sync_transaction(prop, body)
    db.session.commit()
    return ok(_property_dict(prop))


@bp.delete("/properties/<int:id>")
@admin_required
def delete_property(id):
    prop = db.session.get(Property, id)
    if prop is None:
        abort(404)
    db.session.delete(prop)
    db.session.commit()
    return ok(None, message="已删除")
