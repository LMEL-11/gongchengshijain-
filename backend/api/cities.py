"""城市相关接口 /api/cities"""  # 保留字符串内容，作为说明文本或页面展示文案。
from flask import Blueprint, abort  # 从 flask 导入 Blueprint, abort，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import City  # 从 models 导入 City，供本文件后续逻辑调用。
from services import analysis  # 从 services 导入 analysis，供本文件后续逻辑调用。

from .utils import ok  # 从 .utils 导入 ok，供本文件后续逻辑调用。

bp = Blueprint("cities", __name__, url_prefix="/api/cities")  # 设置 bp 的值，供后续业务判断、查询或响应组装使用。


@bp.get("")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def list_cities():  # 定义 list_cities 函数，集中处理这一段业务逻辑。
    """返回城市列表，供前端选择和地图展示使用。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    cities = db.session.query(City).order_by(City.id).all()  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    return ok([c.to_dict() for c in cities])  # 返回处理后的结果给调用方继续使用。


@bp.get("/<int:city_id>")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def get_city(city_id: int):  # 定义 get_city 函数，集中处理这一段业务逻辑。
    """按编号查询城市详情，找不到时返回 404。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    city = db.session.get(City, city_id)  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
    if not city:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        abort(404)  # 执行当前代码行对应的业务处理步骤。
    return ok(city.to_dict())  # 返回处理后的结果给调用方继续使用。


@bp.get("/<int:city_id>/districts")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def city_districts(city_id: int):  # 定义 city_districts 函数，集中处理这一段业务逻辑。
    """Districts of a city with price stats, ranked high→low (drives 3D map)."""  # 保留字符串内容，作为说明文本或页面展示文案。
    if not db.session.get(City, city_id):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        abort(404)  # 执行当前代码行对应的业务处理步骤。
    return ok(analysis.district_ranking(city_id))  # 返回处理后的结果给调用方继续使用。
