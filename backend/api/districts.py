"""行政区相关接口 /api/districts"""  # 保留字符串内容，作为说明文本或页面展示文案。
from flask import Blueprint, abort  # 从 flask 导入 Blueprint, abort，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import District, Facility  # 从 models 导入 District, Facility，供本文件后续逻辑调用。
from services import analysis  # 从 services 导入 analysis，供本文件后续逻辑调用。

from .utils import ok  # 从 .utils 导入 ok，供本文件后续逻辑调用。

bp = Blueprint("districts", __name__, url_prefix="/api/districts")  # 设置 bp 的值，供后续业务判断、查询或响应组装使用。


@bp.get("/<int:district_id>")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def get_district(district_id: int):  # 定义 get_district 函数，集中处理这一段业务逻辑。
    """按编号查询区域详情，找不到时返回 404。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    district = db.session.get(District, district_id)  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
    if not district:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        abort(404)  # 执行当前代码行对应的业务处理步骤。
    return ok(district.to_dict())  # 返回处理后的结果给调用方继续使用。


@bp.get("/<int:district_id>/facilities")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def district_facilities(district_id: int):  # 定义 district_facilities 函数，集中处理这一段业务逻辑。
    """返回指定区域周边配套设施列表。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if not db.session.get(District, district_id):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        abort(404)  # 执行当前代码行对应的业务处理步骤。
    rows = (  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(Facility)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .filter(Facility.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    return ok([f.to_dict() for f in rows])  # 返回处理后的结果给调用方继续使用。


@bp.get("/<int:district_id>/price-trend")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def district_price_trend(district_id: int):  # 定义 district_price_trend 函数，集中处理这一段业务逻辑。
    """返回指定区域的房价历史趋势数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if not db.session.get(District, district_id):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        abort(404)  # 执行当前代码行对应的业务处理步骤。
    return ok(analysis.price_trend(district_id))  # 返回处理后的结果给调用方继续使用。
