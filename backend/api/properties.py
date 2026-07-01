"""房源相关接口 /api/properties"""  # 保留字符串内容，作为说明文本或页面展示文案。
from flask import Blueprint, abort, request  # 从 flask 导入 Blueprint, abort, request，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import District, Facility, Property  # 从 models 导入 District, Facility, Property，供本文件后续逻辑调用。
from services.property_details import get_property_transaction_details  # 从 services.property_details 导入 get_property_transaction_details，供本文件后续逻辑调用。

from .utils import get_float, get_int, ok  # 从 .utils 导入 get_float, get_int, ok，供本文件后续逻辑调用。

bp = Blueprint("properties", __name__, url_prefix="/api/properties")  # 设置 bp 的值，供后续业务判断、查询或响应组装使用。

_SORTS = {  # 设置 _SORTS 的值，供后续业务判断、查询或响应组装使用。
    "price_asc": Property.total_price.asc(),  # 保留字符串内容，作为说明文本或页面展示文案。
    "price_desc": Property.total_price.desc(),  # 保留字符串内容，作为说明文本或页面展示文案。
    "unit_asc": Property.unit_price.asc(),  # 保留字符串内容，作为说明文本或页面展示文案。
    "unit_desc": Property.unit_price.desc(),  # 保留字符串内容，作为说明文本或页面展示文案。
    "area_desc": Property.area.desc(),  # 保留字符串内容，作为说明文本或页面展示文案。
    "newest": Property.created_at.desc(),  # 保留字符串内容，作为说明文本或页面展示文案。
}  # 结束当前多行数据结构或函数调用。


@bp.get("")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def list_properties():  # 定义 list_properties 函数，集中处理这一段业务逻辑。
    """Filterable, sortable, paginated listing search."""  # 保留字符串内容，作为说明文本或页面展示文案。
    query = db.session.query(Property).join(District, Property.district_id == District.id)  # 构造数据库查询，用于读取、筛选或聚合业务数据。

    city_id = get_int("city_id")  # 设置 city_id 的值，供后续业务判断、查询或响应组装使用。
    district_id = get_int("district_id")  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
    listing_type = request.args.get("listing_type")  # 设置 listing_type 的值，供后续业务判断、查询或响应组装使用。
    keyword = (request.args.get("keyword") or "").strip()  # 设置 keyword 的值，供后续业务判断、查询或响应组装使用。
    rooms = get_int("rooms")  # 设置 rooms 的值，供后续业务判断、查询或响应组装使用。
    min_total = get_float("min_total_price")  # 设置 min_total 的值，供后续业务判断、查询或响应组装使用。
    max_total = get_float("max_total_price")  # 设置 max_total 的值，供后续业务判断、查询或响应组装使用。
    min_unit = get_float("min_unit_price")  # 设置 min_unit 的值，供后续业务判断、查询或响应组装使用。
    max_unit = get_float("max_unit_price")  # 设置 max_unit 的值，供后续业务判断、查询或响应组装使用。

    if city_id:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        query = query.filter(District.city_id == city_id)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    if district_id:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        query = query.filter(Property.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    if listing_type:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        query = query.filter(Property.listing_type == listing_type)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    if keyword:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        query = query.filter(Property.title.like(f"%{keyword}%"))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    if rooms is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        # rooms>=4 treated as "4室及以上"
        query = query.filter(Property.rooms >= 4) if rooms >= 4 else query.filter(Property.rooms == rooms)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    if min_total is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        query = query.filter(Property.total_price >= min_total)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    if max_total is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        query = query.filter(Property.total_price <= max_total)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    if min_unit is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        query = query.filter(Property.unit_price >= min_unit)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    if max_unit is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        query = query.filter(Property.unit_price <= max_unit)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。

    query = query.order_by(_SORTS.get(request.args.get("sort", "newest"), Property.created_at.desc()))  # 按指定字段或统计值排序，保证返回顺序符合页面展示需要。

    page = max(get_int("page", 1), 1)  # 设置 page 的值，供后续业务判断、查询或响应组装使用。
    page_size = min(max(get_int("page_size", 12), 1), 100)  # 设置 page_size 的值，供后续业务判断、查询或响应组装使用。
    total = query.count()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    items = query.offset((page - 1) * page_size).limit(page_size).all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。

    return ok(  # 返回处理后的结果给调用方继续使用。
        {  # 执行当前代码行对应的业务处理步骤。
            "items": [p.to_dict() for p in items],  # 保留字符串内容，作为说明文本或页面展示文案。
            "total": total,  # 保留字符串内容，作为说明文本或页面展示文案。
            "page": page,  # 保留字符串内容，作为说明文本或页面展示文案。
            "page_size": page_size,  # 保留字符串内容，作为说明文本或页面展示文案。
            "pages": (total + page_size - 1) // page_size,  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
    )  # 结束当前多行数据结构或函数调用。


@bp.get("/<int:property_id>")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def get_property(property_id: int):  # 定义 get_property 函数，集中处理这一段业务逻辑。
    """查询单个房源详情，找不到时返回 404。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    prop = db.session.get(Property, property_id)  # 设置 prop 的值，供后续业务判断、查询或响应组装使用。
    if not prop:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        abort(404)  # 执行当前代码行对应的业务处理步骤。
    facilities = (  # 设置 facilities 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(Facility)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .filter(Facility.district_id == prop.district_id)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    data = prop.to_dict(detail=True)  # 设置 data 的值，供后续业务判断、查询或响应组装使用。
    data["facilities"] = [f.to_dict() for f in facilities]  # 设置 data["facilities" 的值，供后续业务判断、查询或响应组装使用。
    data["transaction"] = get_property_transaction_details(prop)  # 设置 data["transaction" 的值，供后续业务判断、查询或响应组装使用。
    return ok(data)  # 返回处理后的结果给调用方继续使用。
