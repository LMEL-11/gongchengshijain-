"""配套设施接口 /api/facilities"""
from flask import Blueprint, request

from extensions import db
from models import Facility
from models.facility import FACILITY_CATEGORIES

from .utils import get_int, ok

bp = Blueprint("facilities", __name__, url_prefix="/api/facilities")


@bp.get("")
def list_facilities():
    """List facilities, optionally filtered by district and/or category."""
    query = db.session.query(Facility)
    district_id = get_int("district_id")
    category = request.args.get("category")
    if district_id:
        query = query.filter(Facility.district_id == district_id)
    if category:
        query = query.filter(Facility.category == category)
    return ok([f.to_dict() for f in query.all()])


@bp.get("/categories")
def categories():
    """Facility category legend (key -> 中文名)."""
    return ok([{"key": k, "label": v} for k, v in FACILITY_CATEGORIES.items()])
