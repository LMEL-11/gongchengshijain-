"""统计 / 分析 / 预测接口 /api/stats"""  # 保留字符串内容，作为说明文本或页面展示文案。
from flask import Blueprint, request  # 从 flask 导入 Blueprint, request，供本文件后续逻辑调用。

from services import analysis, prediction  # 从 services 导入 analysis, prediction，供本文件后续逻辑调用。

from .utils import get_int, ok  # 从 .utils 导入 get_int, ok，供本文件后续逻辑调用。

bp = Blueprint("stats", __name__, url_prefix="/api/stats")  # 设置 bp 的值，供后续业务判断、查询或响应组装使用。


@bp.get("/overview")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def overview():  # 定义 overview 函数，集中处理这一段业务逻辑。
    """返回房源总量、城市数量和价格摘要等总览指标。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return ok(analysis.overview())  # 返回处理后的结果给调用方继续使用。


@bp.get("/district-ranking")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def district_ranking():  # 定义 district_ranking 函数，集中处理这一段业务逻辑。
    """按区域聚合并返回均价排行数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    city_id = get_int("city_id", 1)  # 设置 city_id 的值，供后续业务判断、查询或响应组装使用。
    return ok(analysis.district_ranking(city_id))  # 返回处理后的结果给调用方继续使用。


@bp.get("/price-distribution")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def price_distribution():  # 定义 price_distribution 函数，集中处理这一段业务逻辑。
    """按价格区间统计房源数量，生成分布图数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    city_id = get_int("city_id", 1)  # 设置 city_id 的值，供后续业务判断、查询或响应组装使用。
    return ok(analysis.price_distribution(city_id))  # 返回处理后的结果给调用方继续使用。


@bp.get("/investment")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def investment():  # 定义 investment 函数，集中处理这一段业务逻辑。
    """各区投资评分排行（价格洼地 × 涨幅 × 配套）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    city_id = get_int("city_id", 1)  # 设置 city_id 的值，供后续业务判断、查询或响应组装使用。
    return ok(analysis.investment_ranking(city_id))  # 返回处理后的结果给调用方继续使用。


@bp.get("/price-trend")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def price_trend():  # 定义 price_trend 函数，集中处理这一段业务逻辑。
    """返回区域按月份汇总的房价趋势数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    district_id = get_int("district_id")  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
    if not district_id:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return ok([])  # 返回处理后的结果给调用方继续使用。
    return ok(analysis.price_trend(district_id))  # 返回处理后的结果给调用方继续使用。


@bp.get("/listing-profile")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def listing_profile():  # 定义 listing_profile 函数，集中处理这一段业务逻辑。
    """返回区域挂牌活跃度、交易属性和价格画像数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    district_id = get_int("district_id")  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
    if not district_id:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return ok({})  # 返回处理后的结果给调用方继续使用。
    return ok(analysis.listing_profile(district_id))  # 返回处理后的结果给调用方继续使用。


@bp.post("/predict")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def predict():  # 定义 predict 函数，集中处理这一段业务逻辑。
    """根据前端输入调用预测服务并返回估价结果。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    payload = request.get_json(silent=True) or {}  # 设置 payload 的值，供后续业务判断、查询或响应组装使用。
    return ok(prediction.predict(payload))  # 返回处理后的结果给调用方继续使用。


@bp.post("/predict/retrain")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def retrain():  # 定义 retrain 函数，集中处理这一段业务逻辑。
    """Force a model re-train.

    If ``district_id`` is provided, retrain that district's model immediately.
    Without it, clear cached district models; each selected district will be
    retrained lazily on the next prediction.
    """
    payload = request.get_json(silent=True) or {}  # 设置 payload 的值，供后续业务判断、查询或响应组装使用。
    district_id = payload.get("district_id") or request.args.get("district_id", type=int)  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
    fitted = prediction.train(district_id=district_id, force=True)  # 设置 fitted 的值，供后续业务判断、查询或响应组装使用。
    if district_id:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return ok({  # 返回处理后的结果给调用方继续使用。
            "district_id": district_id,  # 保留字符串内容，作为说明文本或页面展示文案。
            "fitted": fitted,  # 保留字符串内容，作为说明文本或页面展示文案。
            "model": "district_random_forest" if fitted else "heuristic",  # 保留字符串内容，作为说明文本或页面展示文案。
        })  # 结束当前多行数据结构或函数调用。
    return ok({"fitted": False, "model": "lazy_district_models", "cache_cleared": True})  # 返回处理后的结果给调用方继续使用。
