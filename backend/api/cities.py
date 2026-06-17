"""城市相关接口 /api/cities"""
from flask import Blueprint, abort

from extensions import db
from models import City
from services import analysis

from .utils import ok

bp = Blueprint("cities", __name__, url_prefix="/api/cities")


@bp.get("")
def list_cities():
    cities = db.session.query(City).order_by(City.id).all()
    return ok([c.to_dict() for c in cities])


@bp.get("/<int:city_id>")
def get_city(city_id: int):
    city = db.session.get(City, city_id)
    if not city:
        abort(404)
    return ok(city.to_dict())


@bp.get("/<int:city_id>/districts")
def city_districts(city_id: int):
    """Districts of a city with price stats, ranked high→low (drives 3D map)."""
    if not db.session.get(City, city_id):
        abort(404)
    return ok(analysis.district_ranking(city_id))
