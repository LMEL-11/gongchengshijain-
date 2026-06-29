"""房源相关接口 /api/properties"""
from flask import Blueprint, abort, request  # 导入本行所需的模块或对象。

from extensions import db  # 导入本行所需的模块或对象。
from models import District, Facility, Property  # 导入本行所需的模块或对象。
from services.property_details import get_property_transaction_details  # 导入本行所需的模块或对象。

from .utils import get_float, get_int, ok  # 导入本行所需的模块或对象。

bp = Blueprint("properties", __name__, url_prefix="/api/properties")  # 赋值或更新当前变量/字段。

_SORTS = {  # 赋值或更新当前变量/字段。
    "price_asc": Property.total_price.asc(),  # 设置当前数据项或参数。
    "price_desc": Property.total_price.desc(),  # 设置当前数据项或参数。
    "unit_asc": Property.unit_price.asc(),  # 设置当前数据项或参数。
    "unit_desc": Property.unit_price.desc(),  # 设置当前数据项或参数。
    "area_desc": Property.area.desc(),  # 设置当前数据项或参数。
    "newest": Property.created_at.desc(),  # 设置当前数据项或参数。
}  # 结束当前数据结构或调用块。


@bp.get("")  # 应用装饰器配置路由、权限或命令。
def list_properties():  # 声明函数或方法入口。
    """Filterable, sortable, paginated listing search."""
    query = db.session.query(Property).join(District, Property.district_id == District.id)  # 执行本行代码逻辑。

    city_id = get_int("city_id")  # 赋值或更新当前变量/字段。
    district_id = get_int("district_id")  # 赋值或更新当前变量/字段。
    listing_type = request.args.get("listing_type")  # 赋值或更新当前变量/字段。
    keyword = (request.args.get("keyword") or "").strip()  # 赋值或更新当前变量/字段。
    rooms = get_int("rooms")  # 赋值或更新当前变量/字段。
    min_total = get_float("min_total_price")  # 赋值或更新当前变量/字段。
    max_total = get_float("max_total_price")  # 赋值或更新当前变量/字段。
    min_unit = get_float("min_unit_price")  # 赋值或更新当前变量/字段。
    max_unit = get_float("max_unit_price")  # 赋值或更新当前变量/字段。

    if city_id:  # 根据条件判断是否进入该分支。
        query = query.filter(District.city_id == city_id)  # 执行本行代码逻辑。
    if district_id:  # 根据条件判断是否进入该分支。
        query = query.filter(Property.district_id == district_id)  # 执行本行代码逻辑。
    if listing_type:  # 根据条件判断是否进入该分支。
        query = query.filter(Property.listing_type == listing_type)  # 执行本行代码逻辑。
    if keyword:  # 根据条件判断是否进入该分支。
        query = query.filter(Property.title.like(f"%{keyword}%"))  # 赋值或更新当前变量/字段。
    if rooms is not None:  # 根据条件判断是否进入该分支。
        # rooms>=4 treated as "4室及以上"
        query = query.filter(Property.rooms >= 4) if rooms >= 4 else query.filter(Property.rooms == rooms)  # 执行本行代码逻辑。
    if min_total is not None:  # 根据条件判断是否进入该分支。
        query = query.filter(Property.total_price >= min_total)  # 执行本行代码逻辑。
    if max_total is not None:  # 根据条件判断是否进入该分支。
        query = query.filter(Property.total_price <= max_total)  # 执行本行代码逻辑。
    if min_unit is not None:  # 根据条件判断是否进入该分支。
        query = query.filter(Property.unit_price >= min_unit)  # 执行本行代码逻辑。
    if max_unit is not None:  # 根据条件判断是否进入该分支。
        query = query.filter(Property.unit_price <= max_unit)  # 执行本行代码逻辑。

    query = query.order_by(_SORTS.get(request.args.get("sort", "newest"), Property.created_at.desc()))  # 赋值或更新当前变量/字段。

    page = max(get_int("page", 1), 1)  # 赋值或更新当前变量/字段。
    page_size = min(max(get_int("page_size", 12), 1), 100)  # 赋值或更新当前变量/字段。
    total = query.count()  # 赋值或更新当前变量/字段。
    items = query.offset((page - 1) * page_size).limit(page_size).all()  # 赋值或更新当前变量/字段。

    return ok(  # 返回当前逻辑的处理结果。
        {  # 执行本行代码逻辑。
            "items": [p.to_dict() for p in items],  # 设置当前数据项或参数。
            "total": total,  # 设置当前数据项或参数。
            "page": page,  # 设置当前数据项或参数。
            "page_size": page_size,  # 设置当前数据项或参数。
            "pages": (total + page_size - 1) // page_size,  # 设置当前数据项或参数。
        }  # 结束当前数据结构或调用块。
    )  # 结束当前数据结构或调用块。


@bp.get("/<int:property_id>")  # 应用装饰器配置路由、权限或命令。
def get_property(property_id: int):  # 声明函数或方法入口。
    """查询单个房源详情，找不到时返回 404。"""
    prop = db.session.get(Property, property_id)  # 赋值或更新当前变量/字段。
    if not prop:  # 根据条件判断是否进入该分支。
        abort(404)  # 执行本行代码逻辑。
    facilities = (  # 赋值或更新当前变量/字段。
        db.session.query(Facility)  # 执行本行代码逻辑。
        .filter(Facility.district_id == prop.district_id)  # 执行本行代码逻辑。
        .all()  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    data = prop.to_dict(detail=True)  # 赋值或更新当前变量/字段。
    data["facilities"] = [f.to_dict() for f in facilities]  # 赋值或更新当前变量/字段。
    data["transaction"] = get_property_transaction_details(prop)  # 赋值或更新当前变量/字段。
    return ok(data)  # 返回当前逻辑的处理结果。
