"""全国二手房数据接口 /api/national（供大屏使用）。"""
from flask import Blueprint, request  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from services import national  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from .utils import get_int, ok  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

bp = Blueprint("national", __name__, url_prefix="/api/national")  # 计算或更新bp中间数据，作为后续业务判断、统计或响应组装的输入。


@bp.get("/summary")  # 把下方函数注册为路由、权限校验或框架回调入口。
def summary():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """返回全国或真实数据模式的总览统计信息。"""
    return ok(national.summary())  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/provinces")  # 把下方函数注册为路由、权限校验或框架回调入口。
def provinces():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """各省二手房聚合（用于全国地图着色 + 省份排行）。"""
    return ok(national.provinces())  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/cities")  # 把下方函数注册为路由、权限校验或框架回调入口。
def cities():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """某省下属城市二手房（用于省级地图着色 + 城市排行）。"""
    province = request.args.get("province", "")  # 从请求或外部输入提取province中间数据，用于后续校验、查询或写入。
    return ok(national.cities(province))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


# ===== 真实采集房源（Property 表）驱动的大屏数据 =====
@bp.get("/real/summary")  # 把下方函数注册为路由、权限校验或框架回调入口。
def real_summary():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """真实房源总量 / 覆盖省市商圈 / 均价 / 城市 TOP / 户型分布。"""
    return ok(national.real_summary())  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/real/provinces")  # 把下方函数注册为路由、权限校验或框架回调入口。
def real_provinces():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """各省真实房源数（全国地图着色 + 省份排行）。"""
    return ok(national.real_provinces())  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/real/cities")  # 把下方函数注册为路由、权限校验或框架回调入口。
def real_cities():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """某省真实房源数（省级地图着色 + 城市排行）。"""
    return ok(national.real_cities(request.args.get("province", "")))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/real/districts")  # 把下方函数注册为路由、权限校验或框架回调入口。
def real_districts():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """某城市各商圈真实房源数（市级下钻侧栏排行）。"""
    return ok(national.real_districts(request.args.get("city", "")))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/real/area-properties")  # 把下方函数注册为路由、权限校验或框架回调入口。
def real_area_properties():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """某城市行政区内可定位房源点（用于大屏内嵌百度地图）。"""
    city = request.args.get("city", "")  # 从请求或外部输入提取city中间数据，用于后续校验、查询或写入。
    area = request.args.get("area", "")  # 从请求或外部输入提取area中间数据，用于后续校验、查询或写入。
    limit = get_int("limit", 800)  # 从请求或外部输入提取limit中间数据，用于后续校验、查询或写入。
    return ok(national.real_area_properties(city, area, limit=limit))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
