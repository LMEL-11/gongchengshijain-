"""城市相关接口 /api/cities"""
from flask import Blueprint, abort  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import City  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from services import analysis  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from .utils import ok  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

bp = Blueprint("cities", __name__, url_prefix="/api/cities")  # 计算或更新bp中间数据，作为后续业务判断、统计或响应组装的输入。


@bp.get("")  # 把下方函数注册为路由、权限校验或框架回调入口。
def list_cities():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """返回城市列表，供前端选择和地图展示使用。"""
    cities = db.session.query(City).order_by(City.id).all()  # 创建城市集合的数据库查询对象，用于继续叠加过滤和聚合条件。
    return ok([c.to_dict() for c in cities])  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/<int:city_id>")  # 把下方函数注册为路由、权限校验或框架回调入口。
def get_city(city_id: int):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """按编号查询城市详情，找不到时返回 404。"""
    city = db.session.get(City, city_id)  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
    if not city:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        abort(404)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return ok(city.to_dict())  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/<int:city_id>/districts")  # 把下方函数注册为路由、权限校验或框架回调入口。
def city_districts(city_id: int):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Districts of a city with price stats, ranked high→low (drives 3D map)."""
    if not db.session.get(City, city_id):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        abort(404)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return ok(analysis.district_ranking(city_id))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
