"""管理后台蓝图 —— 房源 CRUD（仅管理员可访问）。"""
import math  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from flask import Blueprint, abort, jsonify, request  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import District, Property, PropertyTransaction  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from services.property_details import get_property_transaction_details  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from .decorators import admin_required  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from .utils import get_float, get_int, ok  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

bp = Blueprint("admin", __name__, url_prefix="/api/admin")  # 计算或更新bp中间数据，作为后续业务判断、统计或响应组装的输入。

# 后台表单把交易相关字段与房源主体一起提交，这里集中列出需要同步到
# PropertyTransaction 的扩展字段，避免新增/编辑接口各自维护一份字段清单。
TRANSACTION_FIELDS = (  # 计算或更新TRANSACTION_FIELDS中间数据，作为后续业务判断、统计或响应组装的输入。
    "listing_date",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "ownership_type",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "property_right",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "mortgage",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "selling_point",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "community_intro",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "layout_intro",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "transport_intro",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
)  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def _clean_text(value):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    if value is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    text = str(value).strip()  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
    return text or None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _transaction_payload(body):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从请求体中提取房源交易扩展字段并完成文本清理。"""
    return {field: _clean_text(body.get(field)) for field in TRANSACTION_FIELDS}  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _sync_transaction(prop, body):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """根据请求体同步房源的交易扩展记录，必要时创建或删除记录。"""
    if not any(field in body for field in TRANSACTION_FIELDS):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return  # 提前结束当前处理流程，避免无效数据继续向后流转。

    payload = _transaction_payload(body)  # 计算或更新请求或入库载荷，作为后续业务判断、统计或响应组装的输入。
    if not any(payload.values()):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        if prop.transaction:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            db.session.delete(prop.transaction)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
        return  # 提前结束当前处理流程，避免无效数据继续向后流转。

    if not prop.transaction:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        prop.transaction = PropertyTransaction()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    for field, value in payload.items():  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        setattr(prop.transaction, field, value)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。


def _property_dict(prop):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """组装后台房源详情字典，并附带交易扩展信息。"""
    data = prop.to_dict(detail=True)  # 计算或更新响应数据结构，作为后续业务判断、统计或响应组装的输入。
    data["transaction"] = get_property_transaction_details(prop)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return data  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/properties")  # 把下方函数注册为路由、权限校验或框架回调入口。
@admin_required  # 把下方函数注册为路由、权限校验或框架回调入口。
def list_properties():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """查询房源分页列表，支持关键词和区域筛选。"""
    # 先把分页参数限制在可控范围内，再将筛选条件叠加到同一个查询对象上，
    # 这样 total 和当前页 items 始终基于同一套过滤条件。
    page = max(get_int("page", 1), 1)  # 从请求或外部输入提取当前页码，用于后续校验、查询或写入。
    page_size = min(max(get_int("page_size", 20), 1), 100)  # 从请求或外部输入提取每页数量，用于后续校验、查询或写入。
    keyword = (request.args.get("keyword") or "").strip()  # 从请求或外部输入提取搜索关键词，用于后续校验、查询或写入。
    district_id = get_int("district_id")  # 从请求或外部输入提取行政区编号，用于后续校验、查询或写入。

    q = db.session.query(Property)  # 创建数据库查询对象的数据库查询对象，用于继续叠加过滤和聚合条件。
    if district_id:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        q = q.filter(Property.district_id == district_id)  # 计算或更新数据库查询对象，作为后续业务判断、统计或响应组装的输入。
    if keyword:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        q = q.filter(Property.title.contains(keyword))  # 计算或更新数据库查询对象，作为后续业务判断、统计或响应组装的输入。

    total = q.count()  # 计算或更新总数统计，作为后续业务判断、统计或响应组装的输入。
    pages = max(math.ceil(total / page_size), 1)  # 计算或更新pages中间数据，作为后续业务判断、统计或响应组装的输入。
    # 管理列表按 id 稳定排序，避免翻页时因为默认排序不确定导致记录跳动。
    items = (  # 计算或更新列表数据，作为后续业务判断、统计或响应组装的输入。
        q.order_by(Property.id.asc())  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .offset((page - 1) * page_size)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .limit(page_size)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    return ok(  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "items": [_property_dict(p) for p in items],  # 把items字段写入响应数据，供前端页面、图表或后续接口读取。
            "total": total,  # 把total字段写入响应数据，供前端页面、图表或后续接口读取。
            "page": page,  # 把page字段写入响应数据，供前端页面、图表或后续接口读取。
            "page_size": page_size,  # 把page_size字段写入响应数据，供前端页面、图表或后续接口读取。
            "pages": pages,  # 把pages字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


@bp.get("/properties/<int:id>")  # 把下方函数注册为路由、权限校验或框架回调入口。
@admin_required  # 把下方函数注册为路由、权限校验或框架回调入口。
def get_property(id):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """查询单个房源详情，找不到时返回 404。"""
    prop = db.session.get(Property, id)  # 计算或更新prop中间数据，作为后续业务判断、统计或响应组装的输入。
    if prop is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        abort(404)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return ok(_property_dict(prop))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.post("/properties")  # 把下方函数注册为路由、权限校验或框架回调入口。
@admin_required  # 把下方函数注册为路由、权限校验或框架回调入口。
def create_property():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """校验并创建新的房源记录，同时保存交易扩展字段。"""
    body = request.get_json(silent=True) or {}  # 从请求或外部输入提取前端提交的请求体，用于后续校验、查询或写入。

    # 标题和所属区域是人工录入房源的最小可用数据，先校验它们再写入数据库。
    title = (body.get("title") or "").strip()  # 计算或更新title中间数据，作为后续业务判断、统计或响应组装的输入。
    if not title:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return jsonify(code=1, message="房源标题不能为空"), 400  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    district_id = body.get("district_id")  # 计算或更新行政区编号，作为后续业务判断、统计或响应组装的输入。
    if not district_id or db.session.get(District, district_id) is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return jsonify(code=1, message="所属区域无效"), 400  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    # 房源主体只保存可筛选、可展示、可定位的核心字段；交易卖点等长文本由
    # _sync_transaction 写入扩展表，保持 Property 表结构清爽。
    prop = Property(  # 计算或更新prop中间数据，作为后续业务判断、统计或响应组装的输入。
        district_id=district_id,  # 计算或更新行政区编号，作为后续业务判断、统计或响应组装的输入。
        title=title,  # 计算或更新title中间数据，作为后续业务判断、统计或响应组装的输入。
        total_price=body.get("total_price"),  # 计算或更新total_price中间数据，作为后续业务判断、统计或响应组装的输入。
        unit_price=body.get("unit_price"),  # 计算或更新unit_price中间数据，作为后续业务判断、统计或响应组装的输入。
        area=body.get("area"),  # 计算或更新area中间数据，作为后续业务判断、统计或响应组装的输入。
        rooms=body.get("rooms", 0),  # 计算或更新rooms中间数据，作为后续业务判断、统计或响应组装的输入。
        halls=body.get("halls", 0),  # 计算或更新halls中间数据，作为后续业务判断、统计或响应组装的输入。
        floor=body.get("floor"),  # 计算或更新floor中间数据，作为后续业务判断、统计或响应组装的输入。
        total_floors=body.get("total_floors"),  # 计算或更新total_floors中间数据，作为后续业务判断、统计或响应组装的输入。
        build_year=body.get("build_year"),  # 计算或更新build_year中间数据，作为后续业务判断、统计或响应组装的输入。
        orientation=body.get("orientation", ""),  # 计算或更新orientation中间数据，作为后续业务判断、统计或响应组装的输入。
        decoration=body.get("decoration", ""),  # 计算或更新decoration中间数据，作为后续业务判断、统计或响应组装的输入。
        has_elevator=body.get("has_elevator", False),  # 计算或更新has_elevator中间数据，作为后续业务判断、统计或响应组装的输入。
        listing_type=body.get("listing_type", "二手房"),  # 计算或更新listing_type中间数据，作为后续业务判断、统计或响应组装的输入。
        lng=body.get("lng"),  # 计算或更新lng中间数据，作为后续业务判断、统计或响应组装的输入。
        lat=body.get("lat"),  # 计算或更新lat中间数据，作为后续业务判断、统计或响应组装的输入。
        source=body.get("source", "manual"),  # 计算或更新source中间数据，作为后续业务判断、统计或响应组装的输入。
        source_url=body.get("source_url", ""),  # 计算或更新source_url中间数据，作为后续业务判断、统计或响应组装的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    db.session.add(prop)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
    _sync_transaction(prop, body)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
    return ok(_property_dict(prop)), 201  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.put("/properties/<int:id>")  # 把下方函数注册为路由、权限校验或框架回调入口。
@admin_required  # 把下方函数注册为路由、权限校验或框架回调入口。
def update_property(id):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """校验并更新已有房源记录及其交易扩展字段。"""
    prop = db.session.get(Property, id)  # 计算或更新prop中间数据，作为后续业务判断、统计或响应组装的输入。
    if prop is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        abort(404)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    body = request.get_json(silent=True) or {}  # 从请求或外部输入提取前端提交的请求体，用于后续校验、查询或写入。

    if "title" in body:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        title = (body["title"] or "").strip()  # 计算或更新title中间数据，作为后续业务判断、统计或响应组装的输入。
        if not title:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            return jsonify(code=1, message="房源标题不能为空"), 400  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        prop.title = title  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    if "district_id" in body:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        did = body["district_id"]  # 计算或更新did中间数据，作为后续业务判断、统计或响应组装的输入。
        if db.session.get(District, did) is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            return jsonify(code=1, message="所属区域无效"), 400  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        prop.district_id = did  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    # PATCH 风格更新：请求体里出现的字段才覆盖数据库值，未提交的字段保持原样。
    for field in (  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        "total_price",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "unit_price",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "area",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "rooms",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "halls",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "floor",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "total_floors",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "build_year",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "orientation",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "decoration",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "has_elevator",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "listing_type",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "lng",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "lat",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "source",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        "source_url",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ):  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
        if field in body:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            setattr(prop, field, body[field])  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    _sync_transaction(prop, body)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
    return ok(_property_dict(prop))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.delete("/properties/<int:id>")  # 把下方函数注册为路由、权限校验或框架回调入口。
@admin_required  # 把下方函数注册为路由、权限校验或框架回调入口。
def delete_property(id):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """删除指定房源记录并提交数据库变更。"""
    prop = db.session.get(Property, id)  # 计算或更新prop中间数据，作为后续业务判断、统计或响应组装的输入。
    if prop is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        abort(404)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    db.session.delete(prop)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
    db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
    return ok(None, message="已删除")  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
