"""城市相关接口 /api/cities"""
from flask import Blueprint, abort  # 导入本行所需的模块或对象。

from extensions import db  # 导入本行所需的模块或对象。
from models import City  # 导入本行所需的模块或对象。
from services import analysis  # 导入本行所需的模块或对象。

from .utils import ok  # 导入本行所需的模块或对象。

bp = Blueprint("cities", __name__, url_prefix="/api/cities")  # 赋值或更新当前变量/字段。


@bp.get("")  # 应用装饰器配置路由、权限或命令。
def list_cities():  # 声明函数或方法入口。
    """返回城市列表，供前端选择和地图展示使用。"""
    cities = db.session.query(City).order_by(City.id).all()  # 赋值或更新当前变量/字段。
    return ok([c.to_dict() for c in cities])  # 返回当前逻辑的处理结果。


@bp.get("/<int:city_id>")  # 应用装饰器配置路由、权限或命令。
def get_city(city_id: int):  # 声明函数或方法入口。
    """按编号查询城市详情，找不到时返回 404。"""
    city = db.session.get(City, city_id)  # 赋值或更新当前变量/字段。
    if not city:  # 根据条件判断是否进入该分支。
        abort(404)  # 执行本行代码逻辑。
    return ok(city.to_dict())  # 返回当前逻辑的处理结果。


@bp.get("/<int:city_id>/districts")  # 应用装饰器配置路由、权限或命令。
def city_districts(city_id: int):  # 声明函数或方法入口。
    """Districts of a city with price stats, ranked high→low (drives 3D map)."""
    if not db.session.get(City, city_id):  # 根据条件判断是否进入该分支。
        abort(404)  # 执行本行代码逻辑。
    return ok(analysis.district_ranking(city_id))  # 返回当前逻辑的处理结果。
