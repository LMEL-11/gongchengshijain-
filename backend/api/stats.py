"""统计 / 分析 / 预测接口 /api/stats"""
from flask import Blueprint, request  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from services import analysis, prediction  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from .utils import get_int, ok  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

bp = Blueprint("stats", __name__, url_prefix="/api/stats")  # 计算或更新bp中间数据，作为后续业务判断、统计或响应组装的输入。


@bp.get("/overview")  # 把下方函数注册为路由、权限校验或框架回调入口。
def overview():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """返回房源总量、城市数量和价格摘要等总览指标。"""
    return ok(analysis.overview())  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/district-ranking")  # 把下方函数注册为路由、权限校验或框架回调入口。
def district_ranking():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """按区域聚合并返回均价排行数据。"""
    city_id = get_int("city_id", 1)  # 从请求或外部输入提取城市编号，用于后续校验、查询或写入。
    return ok(analysis.district_ranking(city_id))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/price-distribution")  # 把下方函数注册为路由、权限校验或框架回调入口。
def price_distribution():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """按价格区间统计房源数量，生成分布图数据。"""
    city_id = get_int("city_id", 1)  # 从请求或外部输入提取城市编号，用于后续校验、查询或写入。
    return ok(analysis.price_distribution(city_id))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/investment")  # 把下方函数注册为路由、权限校验或框架回调入口。
def investment():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """各区投资评分排行（价格洼地 × 涨幅 × 配套）。"""
    city_id = get_int("city_id", 1)  # 从请求或外部输入提取城市编号，用于后续校验、查询或写入。
    return ok(analysis.investment_ranking(city_id))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/price-trend")  # 把下方函数注册为路由、权限校验或框架回调入口。
def price_trend():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """返回区域按月份汇总的房价趋势数据。"""
    district_id = get_int("district_id")  # 从请求或外部输入提取行政区编号，用于后续校验、查询或写入。
    if not district_id:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return ok([])  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return ok(analysis.price_trend(district_id))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/listing-profile")  # 把下方函数注册为路由、权限校验或框架回调入口。
def listing_profile():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """返回区域挂牌活跃度、交易属性和价格画像数据。"""
    district_id = get_int("district_id")  # 从请求或外部输入提取行政区编号，用于后续校验、查询或写入。
    if not district_id:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return ok({})  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return ok(analysis.listing_profile(district_id))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.post("/predict")  # 把下方函数注册为路由、权限校验或框架回调入口。
def predict():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """根据前端输入调用预测服务并返回估价结果。"""
    payload = request.get_json(silent=True) or {}  # 从请求或外部输入提取请求或入库载荷，用于后续校验、查询或写入。
    return ok(prediction.predict(payload))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.post("/predict/retrain")  # 把下方函数注册为路由、权限校验或框架回调入口。
def retrain():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Force a model re-train.

    If ``district_id`` is provided, retrain that district's model immediately.
    Without it, clear cached district models; each selected district will be
    retrained lazily on the next prediction.
    """
    payload = request.get_json(silent=True) or {}  # 从请求或外部输入提取请求或入库载荷，用于后续校验、查询或写入。
    district_id = payload.get("district_id") or request.args.get("district_id", type=int)  # 从请求或外部输入提取行政区编号，用于后续校验、查询或写入。
    fitted = prediction.train(district_id=district_id, force=True)  # 计算或更新fitted中间数据，作为后续业务判断、统计或响应组装的输入。
    if district_id:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return ok({  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
            "district_id": district_id,  # 把district_id字段写入响应数据，供前端页面、图表或后续接口读取。
            "fitted": fitted,  # 把fitted字段写入响应数据，供前端页面、图表或后续接口读取。
            "model": "district_random_forest" if fitted else "heuristic",  # 把model字段写入响应数据，供前端页面、图表或后续接口读取。
        })  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return ok({"fitted": False, "model": "lazy_district_models", "cache_cleared": True})  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
