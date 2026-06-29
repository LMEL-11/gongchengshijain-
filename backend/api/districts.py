"""行政区相关接口 /api/districts"""
from flask import Blueprint, abort  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import District, Facility  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from services import analysis  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from .utils import ok  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

bp = Blueprint("districts", __name__, url_prefix="/api/districts")  # 计算或更新bp中间数据，作为后续业务判断、统计或响应组装的输入。


@bp.get("/<int:district_id>")  # 把下方函数注册为路由、权限校验或框架回调入口。
def get_district(district_id: int):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """按编号查询区域详情，找不到时返回 404。"""
    district = db.session.get(District, district_id)  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
    if not district:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        abort(404)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return ok(district.to_dict())  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/<int:district_id>/facilities")  # 把下方函数注册为路由、权限校验或框架回调入口。
def district_facilities(district_id: int):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """返回指定区域周边配套设施列表。"""
    if not db.session.get(District, district_id):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        abort(404)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    rows = (  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
        db.session.query(Facility)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .filter(Facility.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return ok([f.to_dict() for f in rows])  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/<int:district_id>/price-trend")  # 把下方函数注册为路由、权限校验或框架回调入口。
def district_price_trend(district_id: int):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """返回指定区域的房价历史趋势数据。"""
    if not db.session.get(District, district_id):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        abort(404)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return ok(analysis.price_trend(district_id))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
