"""管理后台蓝图 —— 房源 CRUD（仅管理员可访问）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
import math  # 导入 math 模块，为当前文件提供所需功能。

from flask import Blueprint, abort, jsonify, request  # 从 flask 导入 Blueprint, abort, jsonify, request，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import District, Property, PropertyTransaction  # 从 models 导入 District, Property, PropertyTransaction，供本文件后续逻辑调用。
from services.property_details import get_property_transaction_details  # 从 services.property_details 导入 get_property_transaction_details，供本文件后续逻辑调用。
from .decorators import admin_required  # 从 .decorators 导入 admin_required，供本文件后续逻辑调用。
from .utils import get_float, get_int, ok  # 从 .utils 导入 get_float, get_int, ok，供本文件后续逻辑调用。

bp = Blueprint("admin", __name__, url_prefix="/api/admin")  # 设置 bp 的值，供后续业务判断、查询或响应组装使用。

# 后台表单把交易相关字段与房源主体一起提交，这里集中列出需要同步到
# PropertyTransaction 的扩展字段，避免新增/编辑接口各自维护一份字段清单。
TRANSACTION_FIELDS = (  # 设置 TRANSACTION_FIELDS 的值，供后续业务判断、查询或响应组装使用。
    "listing_date",  # 保留字符串内容，作为说明文本或页面展示文案。
    "ownership_type",  # 保留字符串内容，作为说明文本或页面展示文案。
    "property_right",  # 保留字符串内容，作为说明文本或页面展示文案。
    "mortgage",  # 保留字符串内容，作为说明文本或页面展示文案。
    "selling_point",  # 保留字符串内容，作为说明文本或页面展示文案。
    "community_intro",  # 保留字符串内容，作为说明文本或页面展示文案。
    "layout_intro",  # 保留字符串内容，作为说明文本或页面展示文案。
    "transport_intro",  # 保留字符串内容，作为说明文本或页面展示文案。
)  # 结束当前多行数据结构或函数调用。


def _clean_text(value):  # 定义 _clean_text 函数，集中处理这一段业务逻辑。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if value is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return None  # 返回处理后的结果给调用方继续使用。
    text = str(value).strip()  # 设置 text 的值，供后续业务判断、查询或响应组装使用。
    return text or None  # 返回处理后的结果给调用方继续使用。


def _transaction_payload(body):  # 定义 _transaction_payload 函数，集中处理这一段业务逻辑。
    """从请求体中提取房源交易扩展字段并完成文本清理。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return {field: _clean_text(body.get(field)) for field in TRANSACTION_FIELDS}  # 返回处理后的结果给调用方继续使用。


def _sync_transaction(prop, body):  # 定义 _sync_transaction 函数，集中处理这一段业务逻辑。
    """根据请求体同步房源的交易扩展记录，必要时创建或删除记录。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if not any(field in body for field in TRANSACTION_FIELDS):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return  # 结束函数并返回空结果。

    payload = _transaction_payload(body)  # 设置 payload 的值，供后续业务判断、查询或响应组装使用。
    if not any(payload.values()):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        if prop.transaction:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            db.session.delete(prop.transaction)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
        return  # 结束函数并返回空结果。

    if not prop.transaction:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        prop.transaction = PropertyTransaction()  # 设置 prop.transaction 的值，供后续业务判断、查询或响应组装使用。
    for field, value in payload.items():  # 遍历当前数据集合，逐项完成处理。
        setattr(prop.transaction, field, value)  # 执行当前代码行对应的业务处理步骤。


def _property_dict(prop):  # 定义 _property_dict 函数，集中处理这一段业务逻辑。
    """组装后台房源详情字典，并附带交易扩展信息。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    data = prop.to_dict(detail=True)  # 设置 data 的值，供后续业务判断、查询或响应组装使用。
    data["transaction"] = get_property_transaction_details(prop)  # 设置 data["transaction" 的值，供后续业务判断、查询或响应组装使用。
    return data  # 返回处理后的结果给调用方继续使用。


@bp.get("/properties")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
@admin_required  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def list_properties():  # 定义 list_properties 函数，集中处理这一段业务逻辑。
    """查询房源分页列表，支持关键词和区域筛选。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    # 先把分页参数限制在可控范围内，再将筛选条件叠加到同一个查询对象上，
    # 这样 total 和当前页 items 始终基于同一套过滤条件。
    page = max(get_int("page", 1), 1)  # 设置 page 的值，供后续业务判断、查询或响应组装使用。
    page_size = min(max(get_int("page_size", 20), 1), 100)  # 设置 page_size 的值，供后续业务判断、查询或响应组装使用。
    keyword = (request.args.get("keyword") or "").strip()  # 设置 keyword 的值，供后续业务判断、查询或响应组装使用。
    district_id = get_int("district_id")  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。

    q = db.session.query(Property)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    if district_id:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        q = q.filter(Property.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    if keyword:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        q = q.filter(Property.title.contains(keyword))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。

    total = q.count()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    pages = max(math.ceil(total / page_size), 1)  # 设置 pages 的值，供后续业务判断、查询或响应组装使用。
    # 管理列表按 id 稳定排序，避免翻页时因为默认排序不确定导致记录跳动。
    items = (  # 设置 items 的值，供后续业务判断、查询或响应组装使用。
        q.order_by(Property.id.asc())  # 按指定字段或统计值排序，保证返回顺序符合页面展示需要。
        .offset((page - 1) * page_size)  # 执行当前代码行对应的业务处理步骤。
        .limit(page_size)  # 执行当前代码行对应的业务处理步骤。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。

    return ok(  # 返回处理后的结果给调用方继续使用。
        {  # 执行当前代码行对应的业务处理步骤。
            "items": [_property_dict(p) for p in items],  # 保留字符串内容，作为说明文本或页面展示文案。
            "total": total,  # 保留字符串内容，作为说明文本或页面展示文案。
            "page": page,  # 保留字符串内容，作为说明文本或页面展示文案。
            "page_size": page_size,  # 保留字符串内容，作为说明文本或页面展示文案。
            "pages": pages,  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
    )  # 结束当前多行数据结构或函数调用。


@bp.get("/properties/<int:id>")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
@admin_required  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def get_property(id):  # 定义 get_property 函数，集中处理这一段业务逻辑。
    """查询单个房源详情，找不到时返回 404。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    prop = db.session.get(Property, id)  # 设置 prop 的值，供后续业务判断、查询或响应组装使用。
    if prop is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        abort(404)  # 执行当前代码行对应的业务处理步骤。
    return ok(_property_dict(prop))  # 返回处理后的结果给调用方继续使用。


@bp.post("/properties")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
@admin_required  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def create_property():  # 定义 create_property 函数，集中处理这一段业务逻辑。
    """校验并创建新的房源记录，同时保存交易扩展字段。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    body = request.get_json(silent=True) or {}  # 设置 body 的值，供后续业务判断、查询或响应组装使用。

    # 标题和所属区域是人工录入房源的最小可用数据，先校验它们再写入数据库。
    title = (body.get("title") or "").strip()  # 设置 title 的值，供后续业务判断、查询或响应组装使用。
    if not title:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return jsonify(code=1, message="房源标题不能为空"), 400  # 返回处理后的结果给调用方继续使用。

    district_id = body.get("district_id")  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
    if not district_id or db.session.get(District, district_id) is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return jsonify(code=1, message="所属区域无效"), 400  # 返回处理后的结果给调用方继续使用。

    # 房源主体只保存可筛选、可展示、可定位的核心字段；交易卖点等长文本由
    # _sync_transaction 写入扩展表，保持 Property 表结构清爽。
    prop = Property(  # 设置 prop 的值，供后续业务判断、查询或响应组装使用。
        district_id=district_id,  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
        title=title,  # 设置 title 的值，供后续业务判断、查询或响应组装使用。
        total_price=body.get("total_price"),  # 设置 total_price 的值，供后续业务判断、查询或响应组装使用。
        unit_price=body.get("unit_price"),  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
        area=body.get("area"),  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
        rooms=body.get("rooms", 0),  # 设置 rooms 的值，供后续业务判断、查询或响应组装使用。
        halls=body.get("halls", 0),  # 设置 halls 的值，供后续业务判断、查询或响应组装使用。
        floor=body.get("floor"),  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
        total_floors=body.get("total_floors"),  # 设置 total_floors 的值，供后续业务判断、查询或响应组装使用。
        build_year=body.get("build_year"),  # 设置 build_year 的值，供后续业务判断、查询或响应组装使用。
        orientation=body.get("orientation", ""),  # 设置 orientation 的值，供后续业务判断、查询或响应组装使用。
        decoration=body.get("decoration", ""),  # 设置 decoration 的值，供后续业务判断、查询或响应组装使用。
        has_elevator=body.get("has_elevator", False),  # 设置 has_elevator 的值，供后续业务判断、查询或响应组装使用。
        listing_type=body.get("listing_type", "二手房"),  # 设置 listing_type 的值，供后续业务判断、查询或响应组装使用。
        lng=body.get("lng"),  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
        lat=body.get("lat"),  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。
        source=body.get("source", "manual"),  # 设置 source 的值，供后续业务判断、查询或响应组装使用。
        source_url=body.get("source_url", ""),  # 设置 source_url 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。
    db.session.add(prop)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
    _sync_transaction(prop, body)  # 执行当前代码行对应的业务处理步骤。
    db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
    return ok(_property_dict(prop)), 201  # 返回处理后的结果给调用方继续使用。


@bp.put("/properties/<int:id>")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
@admin_required  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def update_property(id):  # 定义 update_property 函数，集中处理这一段业务逻辑。
    """校验并更新已有房源记录及其交易扩展字段。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    prop = db.session.get(Property, id)  # 设置 prop 的值，供后续业务判断、查询或响应组装使用。
    if prop is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        abort(404)  # 执行当前代码行对应的业务处理步骤。

    body = request.get_json(silent=True) or {}  # 设置 body 的值，供后续业务判断、查询或响应组装使用。

    if "title" in body:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        title = (body["title"] or "").strip()  # 设置 title 的值，供后续业务判断、查询或响应组装使用。
        if not title:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            return jsonify(code=1, message="房源标题不能为空"), 400  # 返回处理后的结果给调用方继续使用。
        prop.title = title  # 设置 prop.title 的值，供后续业务判断、查询或响应组装使用。

    if "district_id" in body:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        did = body["district_id"]  # 设置 did 的值，供后续业务判断、查询或响应组装使用。
        if db.session.get(District, did) is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            return jsonify(code=1, message="所属区域无效"), 400  # 返回处理后的结果给调用方继续使用。
        prop.district_id = did  # 设置 prop.district_id 的值，供后续业务判断、查询或响应组装使用。

    # PATCH 风格更新：请求体里出现的字段才覆盖数据库值，未提交的字段保持原样。
    for field in (  # 遍历当前数据集合，逐项完成处理。
        "total_price",  # 保留字符串内容，作为说明文本或页面展示文案。
        "unit_price",  # 保留字符串内容，作为说明文本或页面展示文案。
        "area",  # 保留字符串内容，作为说明文本或页面展示文案。
        "rooms",  # 保留字符串内容，作为说明文本或页面展示文案。
        "halls",  # 保留字符串内容，作为说明文本或页面展示文案。
        "floor",  # 保留字符串内容，作为说明文本或页面展示文案。
        "total_floors",  # 保留字符串内容，作为说明文本或页面展示文案。
        "build_year",  # 保留字符串内容，作为说明文本或页面展示文案。
        "orientation",  # 保留字符串内容，作为说明文本或页面展示文案。
        "decoration",  # 保留字符串内容，作为说明文本或页面展示文案。
        "has_elevator",  # 保留字符串内容，作为说明文本或页面展示文案。
        "listing_type",  # 保留字符串内容，作为说明文本或页面展示文案。
        "lng",  # 保留字符串内容，作为说明文本或页面展示文案。
        "lat",  # 保留字符串内容，作为说明文本或页面展示文案。
        "source",  # 保留字符串内容，作为说明文本或页面展示文案。
        "source_url",  # 保留字符串内容，作为说明文本或页面展示文案。
    ):  # 执行当前代码行对应的业务处理步骤。
        if field in body:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            setattr(prop, field, body[field])  # 执行当前代码行对应的业务处理步骤。

    _sync_transaction(prop, body)  # 执行当前代码行对应的业务处理步骤。
    db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
    return ok(_property_dict(prop))  # 返回处理后的结果给调用方继续使用。


@bp.delete("/properties/<int:id>")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
@admin_required  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def delete_property(id):  # 定义 delete_property 函数，集中处理这一段业务逻辑。
    """删除指定房源记录并提交数据库变更。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    prop = db.session.get(Property, id)  # 设置 prop 的值，供后续业务判断、查询或响应组装使用。
    if prop is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        abort(404)  # 执行当前代码行对应的业务处理步骤。
    db.session.delete(prop)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
    db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
    return ok(None, message="已删除")  # 返回处理后的结果给调用方继续使用。
