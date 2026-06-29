"""配套设施接口 /api/facilities"""
from flask import Blueprint, request  # 导入本行所需的模块或对象。

from extensions import db  # 导入本行所需的模块或对象。
from models import Facility  # 导入本行所需的模块或对象。
from models.facility import FACILITY_CATEGORIES  # 导入本行所需的模块或对象。

from .utils import get_int, ok  # 导入本行所需的模块或对象。

bp = Blueprint("facilities", __name__, url_prefix="/api/facilities")  # 赋值或更新当前变量/字段。


@bp.get("")  # 应用装饰器配置路由、权限或命令。
def list_facilities():  # 声明函数或方法入口。
    """List facilities, optionally filtered by district and/or category."""
    query = db.session.query(Facility)  # 赋值或更新当前变量/字段。
    district_id = get_int("district_id")  # 赋值或更新当前变量/字段。
    category = request.args.get("category")  # 赋值或更新当前变量/字段。
    if district_id:  # 根据条件判断是否进入该分支。
        query = query.filter(Facility.district_id == district_id)  # 执行本行代码逻辑。
    if category:  # 根据条件判断是否进入该分支。
        query = query.filter(Facility.category == category)  # 执行本行代码逻辑。
    return ok([f.to_dict() for f in query.all()])  # 返回当前逻辑的处理结果。


@bp.get("/categories")  # 应用装饰器配置路由、权限或命令。
def categories():  # 声明函数或方法入口。
    """Facility category legend (key -> 中文名)."""
    return ok([{"key": k, "label": v} for k, v in FACILITY_CATEGORIES.items()])  # 返回当前逻辑的处理结果。
