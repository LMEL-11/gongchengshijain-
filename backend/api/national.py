"""全国二手房数据接口 /api/national（供大屏使用）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
from flask import Blueprint, request  # 从 flask 导入 Blueprint, request，供本文件后续逻辑调用。

from services import national  # 从 services 导入 national，供本文件后续逻辑调用。

from .utils import get_int, ok  # 从 .utils 导入 get_int, ok，供本文件后续逻辑调用。

bp = Blueprint("national", __name__, url_prefix="/api/national")  # 设置 bp 的值，供后续业务判断、查询或响应组装使用。


@bp.get("/summary")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def summary():  # 定义 summary 函数，集中处理这一段业务逻辑。
    """返回全国或真实数据模式的总览统计信息。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return ok(national.summary())  # 返回处理后的结果给调用方继续使用。


@bp.get("/provinces")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def provinces():  # 定义 provinces 函数，集中处理这一段业务逻辑。
    """各省二手房聚合（用于全国地图着色 + 省份排行）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return ok(national.provinces())  # 返回处理后的结果给调用方继续使用。


@bp.get("/cities")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def cities():  # 定义 cities 函数，集中处理这一段业务逻辑。
    """某省下属城市二手房（用于省级地图着色 + 城市排行）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    province = request.args.get("province", "")  # 设置 province 的值，供后续业务判断、查询或响应组装使用。
    return ok(national.cities(province))  # 返回处理后的结果给调用方继续使用。


# ===== 真实采集房源（Property 表）驱动的大屏数据 =====
@bp.get("/real/summary")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def real_summary():  # 定义 real_summary 函数，集中处理这一段业务逻辑。
    """真实房源总量 / 覆盖省市商圈 / 均价 / 城市 TOP / 户型分布。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return ok(national.real_summary())  # 返回处理后的结果给调用方继续使用。


@bp.get("/real/provinces")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def real_provinces():  # 定义 real_provinces 函数，集中处理这一段业务逻辑。
    """各省真实房源数（全国地图着色 + 省份排行）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return ok(national.real_provinces())  # 返回处理后的结果给调用方继续使用。


@bp.get("/real/cities")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def real_cities():  # 定义 real_cities 函数，集中处理这一段业务逻辑。
    """某省真实房源数（省级地图着色 + 城市排行）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return ok(national.real_cities(request.args.get("province", "")))  # 返回处理后的结果给调用方继续使用。


@bp.get("/real/districts")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def real_districts():  # 定义 real_districts 函数，集中处理这一段业务逻辑。
    """某城市各商圈真实房源数（市级下钻侧栏排行）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return ok(national.real_districts(request.args.get("city", "")))  # 返回处理后的结果给调用方继续使用。


@bp.get("/real/area-properties")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def real_area_properties():  # 定义 real_area_properties 函数，集中处理这一段业务逻辑。
    """某城市行政区内可定位房源点（用于大屏内嵌百度地图）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    city = request.args.get("city", "")  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
    area = request.args.get("area", "")  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
    limit = get_int("limit", 800)  # 设置 limit 的值，供后续业务判断、查询或响应组装使用。
    return ok(national.real_area_properties(city, area, limit=limit))  # 返回处理后的结果给调用方继续使用。
