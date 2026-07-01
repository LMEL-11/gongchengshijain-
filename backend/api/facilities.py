"""配套设施接口 /api/facilities"""  # 保留字符串内容，作为说明文本或页面展示文案。
from flask import Blueprint, request  # 从 flask 导入 Blueprint, request，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import Facility  # 从 models 导入 Facility，供本文件后续逻辑调用。
from models.facility import FACILITY_CATEGORIES  # 从 models.facility 导入 FACILITY_CATEGORIES，供本文件后续逻辑调用。

from .utils import get_int, ok  # 从 .utils 导入 get_int, ok，供本文件后续逻辑调用。

bp = Blueprint("facilities", __name__, url_prefix="/api/facilities")  # 设置 bp 的值，供后续业务判断、查询或响应组装使用。


@bp.get("")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def list_facilities():  # 定义 list_facilities 函数，集中处理这一段业务逻辑。
    """List facilities, optionally filtered by district and/or category."""  # 保留字符串内容，作为说明文本或页面展示文案。
    query = db.session.query(Facility)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    district_id = get_int("district_id")  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
    category = request.args.get("category")  # 设置 category 的值，供后续业务判断、查询或响应组装使用。
    if district_id:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        query = query.filter(Facility.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    if category:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        query = query.filter(Facility.category == category)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
    return ok([f.to_dict() for f in query.all()])  # 返回处理后的结果给调用方继续使用。


@bp.get("/categories")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def categories():  # 定义 categories 函数，集中处理这一段业务逻辑。
    """Facility category legend (key -> 中文名)."""  # 保留字符串内容，作为说明文本或页面展示文案。
    return ok([{"key": k, "label": v} for k, v in FACILITY_CATEGORIES.items()])  # 返回处理后的结果给调用方继续使用。
