"""统计 / 分析 / 预测接口 /api/stats"""
from flask import Blueprint, request  # 导入本行所需的模块或对象。

from services import analysis, prediction  # 导入本行所需的模块或对象。

from .utils import get_int, ok  # 导入本行所需的模块或对象。

bp = Blueprint("stats", __name__, url_prefix="/api/stats")  # 赋值或更新当前变量/字段。


@bp.get("/overview")  # 应用装饰器配置路由、权限或命令。
def overview():  # 声明函数或方法入口。
    """返回房源总量、城市数量和价格摘要等总览指标。"""
    return ok(analysis.overview())  # 返回当前逻辑的处理结果。


@bp.get("/district-ranking")  # 应用装饰器配置路由、权限或命令。
def district_ranking():  # 声明函数或方法入口。
    """按区域聚合并返回均价排行数据。"""
    city_id = get_int("city_id", 1)  # 赋值或更新当前变量/字段。
    return ok(analysis.district_ranking(city_id))  # 返回当前逻辑的处理结果。


@bp.get("/price-distribution")  # 应用装饰器配置路由、权限或命令。
def price_distribution():  # 声明函数或方法入口。
    """按价格区间统计房源数量，生成分布图数据。"""
    city_id = get_int("city_id", 1)  # 赋值或更新当前变量/字段。
    return ok(analysis.price_distribution(city_id))  # 返回当前逻辑的处理结果。


@bp.get("/investment")  # 应用装饰器配置路由、权限或命令。
def investment():  # 声明函数或方法入口。
    """各区投资评分排行（价格洼地 × 涨幅 × 配套）。"""
    city_id = get_int("city_id", 1)  # 赋值或更新当前变量/字段。
    return ok(analysis.investment_ranking(city_id))  # 返回当前逻辑的处理结果。


@bp.get("/price-trend")  # 应用装饰器配置路由、权限或命令。
def price_trend():  # 声明函数或方法入口。
    """返回区域按月份汇总的房价趋势数据。"""
    district_id = get_int("district_id")  # 赋值或更新当前变量/字段。
    if not district_id:  # 根据条件判断是否进入该分支。
        return ok([])  # 返回当前逻辑的处理结果。
    return ok(analysis.price_trend(district_id))  # 返回当前逻辑的处理结果。


@bp.get("/listing-profile")  # 应用装饰器配置路由、权限或命令。
def listing_profile():  # 声明函数或方法入口。
    """返回区域挂牌活跃度、交易属性和价格画像数据。"""
    district_id = get_int("district_id")  # 赋值或更新当前变量/字段。
    if not district_id:  # 根据条件判断是否进入该分支。
        return ok({})  # 返回当前逻辑的处理结果。
    return ok(analysis.listing_profile(district_id))  # 返回当前逻辑的处理结果。


@bp.post("/predict")  # 应用装饰器配置路由、权限或命令。
def predict():  # 声明函数或方法入口。
    """根据前端输入调用预测服务并返回估价结果。"""
    payload = request.get_json(silent=True) or {}  # 赋值或更新当前变量/字段。
    return ok(prediction.predict(payload))  # 返回当前逻辑的处理结果。


@bp.post("/predict/retrain")  # 应用装饰器配置路由、权限或命令。
def retrain():  # 声明函数或方法入口。
    """Force a model re-train.

    If ``district_id`` is provided, retrain that district's model immediately.
    Without it, clear cached district models; each selected district will be
    retrained lazily on the next prediction.
    """
    payload = request.get_json(silent=True) or {}  # 赋值或更新当前变量/字段。
    district_id = payload.get("district_id") or request.args.get("district_id", type=int)  # 赋值或更新当前变量/字段。
    fitted = prediction.train(district_id=district_id, force=True)  # 赋值或更新当前变量/字段。
    if district_id:  # 根据条件判断是否进入该分支。
        return ok({  # 返回当前逻辑的处理结果。
            "district_id": district_id,  # 设置当前数据项或参数。
            "fitted": fitted,  # 设置当前数据项或参数。
            "model": "district_random_forest" if fitted else "heuristic",  # 设置当前数据项或参数。
        })  # 执行本行代码逻辑。
    return ok({"fitted": False, "model": "lazy_district_models", "cache_cleared": True})  # 返回当前逻辑的处理结果。
