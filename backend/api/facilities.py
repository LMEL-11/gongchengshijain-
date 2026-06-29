"""配套设施接口 /api/facilities"""
from flask import Blueprint, request  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import Facility  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models.facility import FACILITY_CATEGORIES  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from .utils import get_int, ok  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

bp = Blueprint("facilities", __name__, url_prefix="/api/facilities")  # 计算或更新bp中间数据，作为后续业务判断、统计或响应组装的输入。


@bp.get("")  # 把下方函数注册为路由、权限校验或框架回调入口。
def list_facilities():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """List facilities, optionally filtered by district and/or category."""
    query = db.session.query(Facility)  # 创建查询条件的数据库查询对象，用于继续叠加过滤和聚合条件。
    district_id = get_int("district_id")  # 从请求或外部输入提取行政区编号，用于后续校验、查询或写入。
    category = request.args.get("category")  # 从请求或外部输入提取category中间数据，用于后续校验、查询或写入。
    if district_id:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        query = query.filter(Facility.district_id == district_id)  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。
    if category:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        query = query.filter(Facility.category == category)  # 计算或更新查询条件，作为后续业务判断、统计或响应组装的输入。
    return ok([f.to_dict() for f in query.all()])  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/categories")  # 把下方函数注册为路由、权限校验或框架回调入口。
def categories():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Facility category legend (key -> 中文名)."""
    return ok([{"key": k, "label": v} for k, v in FACILITY_CATEGORIES.items()])  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
