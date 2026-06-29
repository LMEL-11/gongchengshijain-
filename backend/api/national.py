"""全国二手房数据接口 /api/national（供大屏使用）。"""
from flask import Blueprint, request  # 逐行注释：导入本行所需的模块或对象。

from services import national  # 逐行注释：导入本行所需的模块或对象。

from .utils import get_int, ok  # 逐行注释：导入本行所需的模块或对象。

bp = Blueprint("national", __name__, url_prefix="/api/national")  # 逐行注释：赋值或更新当前变量/字段。


@bp.get("/summary")  # 逐行注释：应用装饰器配置路由、权限或命令。
def summary():  # 逐行注释：声明函数或方法入口。
    """返回全国或真实数据模式的总览统计信息。"""
    return ok(national.summary())  # 逐行注释：返回当前逻辑的处理结果。


@bp.get("/provinces")  # 逐行注释：应用装饰器配置路由、权限或命令。
def provinces():  # 逐行注释：声明函数或方法入口。
    """各省二手房聚合（用于全国地图着色 + 省份排行）。"""
    return ok(national.provinces())  # 逐行注释：返回当前逻辑的处理结果。


@bp.get("/cities")  # 逐行注释：应用装饰器配置路由、权限或命令。
def cities():  # 逐行注释：声明函数或方法入口。
    """某省下属城市二手房（用于省级地图着色 + 城市排行）。"""
    province = request.args.get("province", "")  # 逐行注释：赋值或更新当前变量/字段。
    return ok(national.cities(province))  # 逐行注释：返回当前逻辑的处理结果。


# ===== 真实采集房源（Property 表）驱动的大屏数据 =====
@bp.get("/real/summary")  # 逐行注释：应用装饰器配置路由、权限或命令。
def real_summary():  # 逐行注释：声明函数或方法入口。
    """真实房源总量 / 覆盖省市商圈 / 均价 / 城市 TOP / 户型分布。"""
    return ok(national.real_summary())  # 逐行注释：返回当前逻辑的处理结果。


@bp.get("/real/provinces")  # 逐行注释：应用装饰器配置路由、权限或命令。
def real_provinces():  # 逐行注释：声明函数或方法入口。
    """各省真实房源数（全国地图着色 + 省份排行）。"""
    return ok(national.real_provinces())  # 逐行注释：返回当前逻辑的处理结果。


@bp.get("/real/cities")  # 逐行注释：应用装饰器配置路由、权限或命令。
def real_cities():  # 逐行注释：声明函数或方法入口。
    """某省真实房源数（省级地图着色 + 城市排行）。"""
    return ok(national.real_cities(request.args.get("province", "")))  # 逐行注释：返回当前逻辑的处理结果。


@bp.get("/real/districts")  # 逐行注释：应用装饰器配置路由、权限或命令。
def real_districts():  # 逐行注释：声明函数或方法入口。
    """某城市各商圈真实房源数（市级下钻侧栏排行）。"""
    return ok(national.real_districts(request.args.get("city", "")))  # 逐行注释：返回当前逻辑的处理结果。


@bp.get("/real/area-properties")  # 逐行注释：应用装饰器配置路由、权限或命令。
def real_area_properties():  # 逐行注释：声明函数或方法入口。
    """某城市行政区内可定位房源点（用于大屏内嵌百度地图）。"""
    city = request.args.get("city", "")  # 逐行注释：赋值或更新当前变量/字段。
    area = request.args.get("area", "")  # 逐行注释：赋值或更新当前变量/字段。
    limit = get_int("limit", 800)  # 逐行注释：赋值或更新当前变量/字段。
    return ok(national.real_area_properties(city, area, limit=limit))  # 逐行注释：返回当前逻辑的处理结果。
