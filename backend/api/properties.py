"""房源相关接口 /api/properties"""
from flask import Blueprint, abort, request  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import District, Facility, Property  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from services.property_details import get_property_transaction_details  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from .utils import get_float, get_int, ok  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

bp = Blueprint("properties", __name__, url_prefix="/api/properties")  # 计算或更新bp中间数据，作为后续业务判断、统计或响应组装的输入。

_SORTS = {  # 初始化_SORTS中间数据字典，用于承载接口返回或中间聚合结果。
    "price_asc": Property.total_price.asc(),  # 把price_asc字段写入响应数据，供前端页面、图表或后续接口读取。
    "price_desc": Property.total_price.desc(),  # 把price_desc字段写入响应数据，供前端页面、图表或后续接口读取。
    "unit_asc": Property.unit_price.asc(),  # 把unit_asc字段写入响应数据，供前端页面、图表或后续接口读取。
    "unit_desc": Property.unit_price.desc(),  # 把unit_desc字段写入响应数据，供前端页面、图表或后续接口读取。
    "area_desc": Property.area.desc(),  # 把area_desc字段写入响应数据，供前端页面、图表或后续接口读取。
    "newest": Property.created_at.desc(),  # 把newest字段写入响应数据，供前端页面、图表或后续接口读取。
}  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


@bp.get("")  # 把下方函数注册为路由、权限校验或框架回调入口。
def list_properties():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Filterable, sortable, paginated listing search."""
    query = db.session.query(Property).join(District, Property.district_id == District.id)  # 创建查询条件的数据库查询对象，用于继续叠加过滤和聚合条件。

    city_id = get_int("city_id")  # 从请求或外部输入提取城市编号，用于后续校验、查询或写入。
    district_id = get_int("district_id")  # 从请求或外部输入提取行政区编号，用于后续校验、查询或写入。
    listing_type = request.args.get("listing_type")  # 从请求或外部输入提取listing_type中间数据，用于后续校验、查询或写入。
    keyword = (request.args.get("keyword") or "").strip()  # 从请求或外部输入提取搜索关键词，用于后续校验、查询或写入。
    rooms = get_int("rooms")  # 从请求或外部输入提取rooms中间数据，用于后续校验、查询或写入。
    min_total = get_float("min_total_price")  # 从请求或外部输入提取min_total中间数据，用于后续校验、查询或写入。
    max_total = get_float("max_total_price")  # 从请求或外部输入提取max_total中间数据，用于后续校验、查询或写入。
    min_unit = get_float("min_unit_price")  # 从请求或外部输入提取min_unit中间数据，用于后续校验、查询或写入。
    max_unit = get_float("max_unit_price")  # 从请求或外部输入提取max_unit中间数据，用于后续校验、查询或写入。

    if city_id:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        query = query.filter(District.city_id == city_id)  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。
    if district_id:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        query = query.filter(Property.district_id == district_id)  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。
    if listing_type:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        query = query.filter(Property.listing_type == listing_type)  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。
    if keyword:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        query = query.filter(Property.title.like(f"%{keyword}%"))  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。
    if rooms is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        # rooms>=4 treated as "4室及以上"
        query = query.filter(Property.rooms >= 4) if rooms >= 4 else query.filter(Property.rooms == rooms)  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。
    if min_total is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        query = query.filter(Property.total_price >= min_total)  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。
    if max_total is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        query = query.filter(Property.total_price <= max_total)  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。
    if min_unit is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        query = query.filter(Property.unit_price >= min_unit)  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。
    if max_unit is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        query = query.filter(Property.unit_price <= max_unit)  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。

    query = query.order_by(_SORTS.get(request.args.get("sort", "newest"), Property.created_at.desc()))  # 从请求或外部输入提取查询条件，用于后续校验、查询或写入。

    page = max(get_int("page", 1), 1)  # 从请求或外部输入提取当前页码，用于后续校验、查询或写入。
    page_size = min(max(get_int("page_size", 12), 1), 100)  # 从请求或外部输入提取每页数量，用于后续校验、查询或写入。
    total = query.count()  # 计算或更新总数统计，作为后续业务判断、统计或响应组装的输入。
    items = query.offset((page - 1) * page_size).limit(page_size).all()  # 计算或更新列表数据，作为后续业务判断、统计或响应组装的输入。

    return ok(  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "items": [p.to_dict() for p in items],  # 把items字段写入响应数据，供前端页面、图表或后续接口读取。
            "total": total,  # 把total字段写入响应数据，供前端页面、图表或后续接口读取。
            "page": page,  # 把page字段写入响应数据，供前端页面、图表或后续接口读取。
            "page_size": page_size,  # 把page_size字段写入响应数据，供前端页面、图表或后续接口读取。
            "pages": (total + page_size - 1) // page_size,  # 把pages字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


@bp.get("/<int:property_id>")  # 把下方函数注册为路由、权限校验或框架回调入口。
def get_property(property_id: int):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """查询单个房源详情，找不到时返回 404。"""
    prop = db.session.get(Property, property_id)  # 计算或更新prop中间数据，作为后续业务判断、统计或响应组装的输入。
    if not prop:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        abort(404)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    facilities = (  # 计算或更新facilities中间数据，作为后续业务判断、统计或响应组装的输入。
        db.session.query(Facility)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .filter(Facility.district_id == prop.district_id)  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    data = prop.to_dict(detail=True)  # 计算或更新响应数据结构，作为后续业务判断、统计或响应组装的输入。
    data["facilities"] = [f.to_dict() for f in facilities]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    data["transaction"] = get_property_transaction_details(prop)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return ok(data)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
