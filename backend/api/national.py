"""全国二手房数据接口 /api/national（供大屏使用）。"""
from flask import Blueprint, request

from services import national

from .utils import ok

bp = Blueprint("national", __name__, url_prefix="/api/national")


@bp.get("/summary")
def summary():
    return ok(national.summary())


@bp.get("/provinces")
def provinces():
    """各省二手房聚合（用于全国地图着色 + 省份排行）。"""
    return ok(national.provinces())


@bp.get("/cities")
def cities():
    """某省下属城市二手房（用于省级地图着色 + 城市排行）。"""
    province = request.args.get("province", "")
    return ok(national.cities(province))


# ===== 真实采集房源（Property 表）驱动的大屏数据 =====
@bp.get("/real/summary")
def real_summary():
    """真实房源总量 / 覆盖省市商圈 / 均价 / 城市 TOP / 户型分布。"""
    return ok(national.real_summary())


@bp.get("/real/provinces")
def real_provinces():
    """各省真实房源数（全国地图着色 + 省份排行）。"""
    return ok(national.real_provinces())


@bp.get("/real/cities")
def real_cities():
    """某省真实房源数（省级地图着色 + 城市排行）。"""
    return ok(national.real_cities(request.args.get("province", "")))


@bp.get("/real/districts")
def real_districts():
    """某城市各商圈真实房源数（市级下钻侧栏排行）。"""
    return ok(national.real_districts(request.args.get("city", "")))
