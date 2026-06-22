"""统计 / 分析 / 预测接口 /api/stats"""
from flask import Blueprint, request

from services import analysis, prediction

from .utils import get_int, ok

bp = Blueprint("stats", __name__, url_prefix="/api/stats")


@bp.get("/overview")
def overview():
    return ok(analysis.overview())


@bp.get("/district-ranking")
def district_ranking():
    city_id = get_int("city_id", 1)
    return ok(analysis.district_ranking(city_id))


@bp.get("/price-distribution")
def price_distribution():
    city_id = get_int("city_id", 1)
    return ok(analysis.price_distribution(city_id))


@bp.get("/investment")
def investment():
    """各区投资评分排行（价格洼地 × 涨幅 × 配套）。"""
    city_id = get_int("city_id", 1)
    return ok(analysis.investment_ranking(city_id))


@bp.get("/price-trend")
def price_trend():
    district_id = get_int("district_id")
    if not district_id:
        return ok([])
    return ok(analysis.price_trend(district_id))


@bp.get("/listing-profile")
def listing_profile():
    district_id = get_int("district_id")
    if not district_id:
        return ok({})
    return ok(analysis.listing_profile(district_id))


@bp.post("/predict")
def predict():
    payload = request.get_json(silent=True) or {}
    return ok(prediction.predict(payload))


@bp.post("/predict/retrain")
def retrain():
    """Force a model re-train.

    If ``district_id`` is provided, retrain that district's model immediately.
    Without it, clear cached district models; each selected district will be
    retrained lazily on the next prediction.
    """
    payload = request.get_json(silent=True) or {}
    district_id = payload.get("district_id") or request.args.get("district_id", type=int)
    fitted = prediction.train(district_id=district_id, force=True)
    if district_id:
        return ok({
            "district_id": district_id,
            "fitted": fitted,
            "model": "district_random_forest" if fitted else "heuristic",
        })
    return ok({"fitted": False, "model": "lazy_district_models", "cache_cleared": True})
