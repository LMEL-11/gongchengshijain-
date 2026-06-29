"""管理后台蓝图 —— 房源 CRUD（仅管理员可访问）。"""
import math  # 导入本行所需的模块或对象。

from flask import Blueprint, abort, jsonify, request  # 导入本行所需的模块或对象。

from extensions import db  # 导入本行所需的模块或对象。
from models import District, Property, PropertyTransaction  # 导入本行所需的模块或对象。
from services.property_details import get_property_transaction_details  # 导入本行所需的模块或对象。
from .decorators import admin_required  # 导入本行所需的模块或对象。
from .utils import get_float, get_int, ok  # 导入本行所需的模块或对象。

bp = Blueprint("admin", __name__, url_prefix="/api/admin")  # 赋值或更新当前变量/字段。

TRANSACTION_FIELDS = (  # 赋值或更新当前变量/字段。
    "listing_date",  # 设置当前数据项或参数。
    "ownership_type",  # 设置当前数据项或参数。
    "property_right",  # 设置当前数据项或参数。
    "mortgage",  # 设置当前数据项或参数。
    "selling_point",  # 设置当前数据项或参数。
    "community_intro",  # 设置当前数据项或参数。
    "layout_intro",  # 设置当前数据项或参数。
    "transport_intro",  # 设置当前数据项或参数。
)  # 结束当前数据结构或调用块。


def _clean_text(value):  # 声明函数或方法入口。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    if value is None:  # 根据条件判断是否进入该分支。
        return None  # 返回当前逻辑的处理结果。
    text = str(value).strip()  # 赋值或更新当前变量/字段。
    return text or None  # 返回当前逻辑的处理结果。


def _transaction_payload(body):  # 声明函数或方法入口。
    """从请求体中提取房源交易扩展字段并完成文本清理。"""
    return {field: _clean_text(body.get(field)) for field in TRANSACTION_FIELDS}  # 返回当前逻辑的处理结果。


def _sync_transaction(prop, body):  # 声明函数或方法入口。
    """根据请求体同步房源的交易扩展记录，必要时创建或删除记录。"""
    if not any(field in body for field in TRANSACTION_FIELDS):  # 根据条件判断是否进入该分支。
        return  # 返回当前逻辑的处理结果。

    payload = _transaction_payload(body)  # 赋值或更新当前变量/字段。
    if not any(payload.values()):  # 根据条件判断是否进入该分支。
        if prop.transaction:  # 根据条件判断是否进入该分支。
            db.session.delete(prop.transaction)  # 把对象标记为删除等待提交。
        return  # 返回当前逻辑的处理结果。

    if not prop.transaction:  # 根据条件判断是否进入该分支。
        prop.transaction = PropertyTransaction()  # 赋值或更新当前变量/字段。
    for field, value in payload.items():  # 遍历集合中的每一项并执行处理。
        setattr(prop.transaction, field, value)  # 执行本行代码逻辑。


def _property_dict(prop):  # 声明函数或方法入口。
    """组装后台房源详情字典，并附带交易扩展信息。"""
    data = prop.to_dict(detail=True)  # 赋值或更新当前变量/字段。
    data["transaction"] = get_property_transaction_details(prop)  # 赋值或更新当前变量/字段。
    return data  # 返回当前逻辑的处理结果。


@bp.get("/properties")  # 应用装饰器配置路由、权限或命令。
@admin_required  # 应用装饰器配置路由、权限或命令。
def list_properties():  # 声明函数或方法入口。
    """查询房源分页列表，支持关键词和区域筛选。"""
    page = max(get_int("page", 1), 1)  # 赋值或更新当前变量/字段。
    page_size = min(max(get_int("page_size", 20), 1), 100)  # 赋值或更新当前变量/字段。
    keyword = (request.args.get("keyword") or "").strip()  # 赋值或更新当前变量/字段。
    district_id = get_int("district_id")  # 赋值或更新当前变量/字段。

    q = db.session.query(Property)  # 赋值或更新当前变量/字段。
    if district_id:  # 根据条件判断是否进入该分支。
        q = q.filter(Property.district_id == district_id)  # 执行本行代码逻辑。
    if keyword:  # 根据条件判断是否进入该分支。
        q = q.filter(Property.title.contains(keyword))  # 赋值或更新当前变量/字段。

    total = q.count()  # 赋值或更新当前变量/字段。
    pages = max(math.ceil(total / page_size), 1)  # 赋值或更新当前变量/字段。
    items = (  # 赋值或更新当前变量/字段。
        q.order_by(Property.id.asc())  # 执行本行代码逻辑。
        .offset((page - 1) * page_size)  # 执行本行代码逻辑。
        .limit(page_size)  # 执行本行代码逻辑。
        .all()  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。

    return ok(  # 返回当前逻辑的处理结果。
        {  # 执行本行代码逻辑。
            "items": [_property_dict(p) for p in items],  # 设置当前数据项或参数。
            "total": total,  # 设置当前数据项或参数。
            "page": page,  # 设置当前数据项或参数。
            "page_size": page_size,  # 设置当前数据项或参数。
            "pages": pages,  # 设置当前数据项或参数。
        }  # 结束当前数据结构或调用块。
    )  # 结束当前数据结构或调用块。


@bp.get("/properties/<int:id>")  # 应用装饰器配置路由、权限或命令。
@admin_required  # 应用装饰器配置路由、权限或命令。
def get_property(id):  # 声明函数或方法入口。
    """查询单个房源详情，找不到时返回 404。"""
    prop = db.session.get(Property, id)  # 赋值或更新当前变量/字段。
    if prop is None:  # 根据条件判断是否进入该分支。
        abort(404)  # 执行本行代码逻辑。
    return ok(_property_dict(prop))  # 返回当前逻辑的处理结果。


@bp.post("/properties")  # 应用装饰器配置路由、权限或命令。
@admin_required  # 应用装饰器配置路由、权限或命令。
def create_property():  # 声明函数或方法入口。
    """校验并创建新的房源记录，同时保存交易扩展字段。"""
    body = request.get_json(silent=True) or {}  # 赋值或更新当前变量/字段。

    title = (body.get("title") or "").strip()  # 赋值或更新当前变量/字段。
    if not title:  # 根据条件判断是否进入该分支。
        return jsonify(code=1, message="房源标题不能为空"), 400  # 返回当前逻辑的处理结果。

    district_id = body.get("district_id")  # 赋值或更新当前变量/字段。
    if not district_id or db.session.get(District, district_id) is None:  # 根据条件判断是否进入该分支。
        return jsonify(code=1, message="所属区域无效"), 400  # 返回当前逻辑的处理结果。

    prop = Property(  # 赋值或更新当前变量/字段。
        district_id=district_id,  # 赋值或更新当前变量/字段。
        title=title,  # 赋值或更新当前变量/字段。
        total_price=body.get("total_price"),  # 赋值或更新当前变量/字段。
        unit_price=body.get("unit_price"),  # 赋值或更新当前变量/字段。
        area=body.get("area"),  # 赋值或更新当前变量/字段。
        rooms=body.get("rooms", 0),  # 赋值或更新当前变量/字段。
        halls=body.get("halls", 0),  # 赋值或更新当前变量/字段。
        floor=body.get("floor"),  # 赋值或更新当前变量/字段。
        total_floors=body.get("total_floors"),  # 赋值或更新当前变量/字段。
        build_year=body.get("build_year"),  # 赋值或更新当前变量/字段。
        orientation=body.get("orientation", ""),  # 赋值或更新当前变量/字段。
        decoration=body.get("decoration", ""),  # 赋值或更新当前变量/字段。
        has_elevator=body.get("has_elevator", False),  # 赋值或更新当前变量/字段。
        listing_type=body.get("listing_type", "二手房"),  # 赋值或更新当前变量/字段。
        lng=body.get("lng"),  # 赋值或更新当前变量/字段。
        lat=body.get("lat"),  # 赋值或更新当前变量/字段。
        source=body.get("source", "manual"),  # 赋值或更新当前变量/字段。
        source_url=body.get("source_url", ""),  # 赋值或更新当前变量/字段。
    )  # 结束当前数据结构或调用块。
    db.session.add(prop)  # 把对象加入数据库会话等待提交。
    _sync_transaction(prop, body)  # 执行本行代码逻辑。
    db.session.commit()  # 提交当前数据库事务。
    return ok(_property_dict(prop)), 201  # 返回当前逻辑的处理结果。


@bp.put("/properties/<int:id>")  # 应用装饰器配置路由、权限或命令。
@admin_required  # 应用装饰器配置路由、权限或命令。
def update_property(id):  # 声明函数或方法入口。
    """校验并更新已有房源记录及其交易扩展字段。"""
    prop = db.session.get(Property, id)  # 赋值或更新当前变量/字段。
    if prop is None:  # 根据条件判断是否进入该分支。
        abort(404)  # 执行本行代码逻辑。

    body = request.get_json(silent=True) or {}  # 赋值或更新当前变量/字段。

    if "title" in body:  # 根据条件判断是否进入该分支。
        title = (body["title"] or "").strip()  # 赋值或更新当前变量/字段。
        if not title:  # 根据条件判断是否进入该分支。
            return jsonify(code=1, message="房源标题不能为空"), 400  # 返回当前逻辑的处理结果。
        prop.title = title  # 赋值或更新当前变量/字段。

    if "district_id" in body:  # 根据条件判断是否进入该分支。
        did = body["district_id"]  # 赋值或更新当前变量/字段。
        if db.session.get(District, did) is None:  # 根据条件判断是否进入该分支。
            return jsonify(code=1, message="所属区域无效"), 400  # 返回当前逻辑的处理结果。
        prop.district_id = did  # 赋值或更新当前变量/字段。

    # Numeric / string / bool fields — only update when present
    for field in (  # 遍历集合中的每一项并执行处理。
        "total_price",  # 设置当前数据项或参数。
        "unit_price",  # 设置当前数据项或参数。
        "area",  # 设置当前数据项或参数。
        "rooms",  # 设置当前数据项或参数。
        "halls",  # 设置当前数据项或参数。
        "floor",  # 设置当前数据项或参数。
        "total_floors",  # 设置当前数据项或参数。
        "build_year",  # 设置当前数据项或参数。
        "orientation",  # 设置当前数据项或参数。
        "decoration",  # 设置当前数据项或参数。
        "has_elevator",  # 设置当前数据项或参数。
        "listing_type",  # 设置当前数据项或参数。
        "lng",  # 设置当前数据项或参数。
        "lat",  # 设置当前数据项或参数。
        "source",  # 设置当前数据项或参数。
        "source_url",  # 设置当前数据项或参数。
    ):  # 开始一个新的缩进代码块。
        if field in body:  # 根据条件判断是否进入该分支。
            setattr(prop, field, body[field])  # 执行本行代码逻辑。

    _sync_transaction(prop, body)  # 执行本行代码逻辑。
    db.session.commit()  # 提交当前数据库事务。
    return ok(_property_dict(prop))  # 返回当前逻辑的处理结果。


@bp.delete("/properties/<int:id>")  # 应用装饰器配置路由、权限或命令。
@admin_required  # 应用装饰器配置路由、权限或命令。
def delete_property(id):  # 声明函数或方法入口。
    """删除指定房源记录并提交数据库变更。"""
    prop = db.session.get(Property, id)  # 赋值或更新当前变量/字段。
    if prop is None:  # 根据条件判断是否进入该分支。
        abort(404)  # 执行本行代码逻辑。
    db.session.delete(prop)  # 把对象标记为删除等待提交。
    db.session.commit()  # 提交当前数据库事务。
    return ok(None, message="已删除")  # 返回当前逻辑的处理结果。
