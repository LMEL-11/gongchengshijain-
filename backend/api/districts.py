"""行政区相关接口 /api/districts"""
from flask import Blueprint, abort  # 逐行注释：导入本行所需的模块或对象。

from extensions import db  # 逐行注释：导入本行所需的模块或对象。
from models import District, Facility  # 逐行注释：导入本行所需的模块或对象。
from services import analysis  # 逐行注释：导入本行所需的模块或对象。

from .utils import ok  # 逐行注释：导入本行所需的模块或对象。

bp = Blueprint("districts", __name__, url_prefix="/api/districts")  # 逐行注释：赋值或更新当前变量/字段。


@bp.get("/<int:district_id>")  # 逐行注释：应用装饰器配置路由、权限或命令。
def get_district(district_id: int):  # 逐行注释：声明函数或方法入口。
    """按编号查询区域详情，找不到时返回 404。"""
    district = db.session.get(District, district_id)  # 逐行注释：赋值或更新当前变量/字段。
    if not district:  # 逐行注释：根据条件判断是否进入该分支。
        abort(404)  # 逐行注释：执行本行代码逻辑。
    return ok(district.to_dict())  # 逐行注释：返回当前逻辑的处理结果。


@bp.get("/<int:district_id>/facilities")  # 逐行注释：应用装饰器配置路由、权限或命令。
def district_facilities(district_id: int):  # 逐行注释：声明函数或方法入口。
    """返回指定区域周边配套设施列表。"""
    if not db.session.get(District, district_id):  # 逐行注释：根据条件判断是否进入该分支。
        abort(404)  # 逐行注释：执行本行代码逻辑。
    rows = (  # 逐行注释：赋值或更新当前变量/字段。
        db.session.query(Facility)  # 逐行注释：执行本行代码逻辑。
        .filter(Facility.district_id == district_id)  # 逐行注释：执行本行代码逻辑。
        .all()  # 逐行注释：执行本行代码逻辑。
    )  # 逐行注释：结束当前数据结构或调用块。
    return ok([f.to_dict() for f in rows])  # 逐行注释：返回当前逻辑的处理结果。


@bp.get("/<int:district_id>/price-trend")  # 逐行注释：应用装饰器配置路由、权限或命令。
def district_price_trend(district_id: int):  # 逐行注释：声明函数或方法入口。
    """返回指定区域的房价历史趋势数据。"""
    if not db.session.get(District, district_id):  # 逐行注释：根据条件判断是否进入该分支。
        abort(404)  # 逐行注释：执行本行代码逻辑。
    return ok(analysis.price_trend(district_id))  # 逐行注释：返回当前逻辑的处理结果。
