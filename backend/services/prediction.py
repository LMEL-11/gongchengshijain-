"""房价预测 Price-prediction service.

Trains one regression model per selected district and caches it in memory. The
selected administrative district / business area is the training scope, so a
prediction for 济南·省体 is trained from 省体 listings instead of the whole city
or national dataset. Degrades gracefully to a district-average heuristic if
scikit-learn is unavailable or the selected district has too little data.
"""
from datetime import datetime  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from typing import Any, Optional  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from sqlalchemy import func  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import City, District, Property  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

try:  # scikit-learn is optional at runtime
    import numpy as np  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
    from sklearn.ensemble import RandomForestRegressor  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

    _SKLEARN = True  # 计算或更新_SKLEARN中间数据，作为后续业务判断、统计或响应组装的输入。
except Exception:  # pragma: no cover - import guard
    _SKLEARN = False  # 计算或更新_SKLEARN中间数据，作为后续业务判断、统计或响应组装的输入。

# Module-level cache: trained estimators by district + average-price lookups.
_models: dict[int, Optional[Any]] = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
_model_samples: dict[int, int] = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
_district_avg: dict[int, float] = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
_city_avg: dict[int, float] = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
_global_avg: float = 0.0  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

FEATURES = ("area", "rooms", "halls", "building_age", "has_elevator", "floor_ratio", "district_avg")  # 计算或更新FEATURES中间数据，作为后续业务判断、统计或响应组装的输入。


def _current_year() -> int:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """返回当前年份，用作预测特征的兜底建成年份。"""
    return datetime.now().year  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _row_features(p: Property, district_avg: float) -> list[float]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """把房源记录转换为模型训练需要的特征向量。"""
    # 特征尽量只使用用户预测时也能填写的字段，避免训练/预测口径不一致。
    age = max(0, _current_year() - (p.build_year or _current_year()))  # 计算或更新age中间数据，作为后续业务判断、统计或响应组装的输入。
    floor_ratio = (p.floor or 1) / (p.total_floors or 1)  # 计算或更新floor_ratio中间数据，作为后续业务判断、统计或响应组装的输入。
    return [  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        p.area or 0,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        p.rooms or 0,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        p.halls or 0,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        age,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        1.0 if p.has_elevator else 0.0,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        min(floor_ratio, 1.0),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        district_avg,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def _refresh_avgs() -> None:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Refresh district, city, and global average unit prices."""
    global _district_avg, _city_avg, _global_avg  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    # 均价缓存既是模型特征，也是样本不足或 sklearn 不可用时的兜底估价基准。
    _district_avg = {  # 初始化_district_avg中间数据字典，用于承载接口返回或中间聚合结果。
        district_id: round(avg_price)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        for district_id, avg_price in (  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            db.session.query(District.id, func.avg(Property.unit_price))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            .join(Property, Property.district_id == District.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
            .filter(Property.unit_price.isnot(None))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
            .group_by(District.id)  # 按业务维度分组聚合，生成排行榜或统计指标。
            .all()  # 执行查询并取回结果，作为后续数据转换的输入。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        if avg_price  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    _city_avg = {  # 初始化_city_avg中间数据字典，用于承载接口返回或中间聚合结果。
        city_id: round(avg_price)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        for city_id, avg_price in (  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            db.session.query(District.city_id, func.avg(Property.unit_price))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            .join(Property, Property.district_id == District.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
            .filter(Property.unit_price.isnot(None))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
            .group_by(District.city_id)  # 按业务维度分组聚合，生成排行榜或统计指标。
            .all()  # 执行查询并取回结果，作为后续数据转换的输入。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        if avg_price  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    _global_avg = round(sum(_city_avg.values()) / len(_city_avg)) if _city_avg else 0  # 计算或更新_global_avg中间数据，作为后续业务判断、统计或响应组装的输入。


def train(district_id: Optional[int] = None, force: bool = False) -> bool:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Train (or re-train) a district model.

    Returns True if a real random-forest model was fitted. If ``district_id`` is
    omitted, existing district-model caches are cleared and averages are
    refreshed; the next prediction lazily trains its selected district.
    """
    if force or not _district_avg:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        _refresh_avgs()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    if district_id is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        if force:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            _models.clear()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            _model_samples.clear()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return False  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    if not _SKLEARN:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        _models[district_id] = None  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        _model_samples[district_id] = 0  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return False  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    if district_id in _models and not force:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return _models[district_id] is not None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    # 每个区域单独训练，避免不同商圈价格水平混在一起削弱局部预测能力。
    props = (  # 计算或更新props中间数据，作为后续业务判断、统计或响应组装的输入。
        db.session.query(Property)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .filter(Property.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .filter(Property.unit_price.isnot(None), Property.area.isnot(None))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    if len(props) < 30:  # not enough signal to fit anything meaningful
        _models[district_id] = None  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        _model_samples[district_id] = len(props)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return False  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    # X 保存可解释的结构化房源特征，y 保存目标单价。
    X, y = [], []  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    district_avg = _district_avg.get(district_id, _global_avg)  # 计算或更新district_avg中间数据，作为后续业务判断、统计或响应组装的输入。
    for p in props:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        X.append(_row_features(p, district_avg))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        y.append(p.unit_price)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    model = RandomForestRegressor(n_estimators=120, random_state=42, max_depth=12)  # 计算或更新model中间数据，作为后续业务判断、统计或响应组装的输入。
    model.fit(np.array(X), np.array(y))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    _models[district_id] = model  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    _model_samples[district_id] = len(props)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return True  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def predict(payload: dict) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Predict unit & total price for a hypothetical listing.

    ``payload`` keys: city_id, district_id, area, rooms, halls, build_year,
    has_elevator, floor, total_floors.
    """
    district_id = payload.get("district_id")  # 计算或更新行政区编号，作为后续业务判断、统计或响应组装的输入。
    district = db.session.get(District, district_id) if district_id else None  # 计算或更新district中间数据，作为后续业务判断、统计或响应组装的输入。
    city_id = district.city_id if district else payload.get("city_id")  # 计算或更新城市编号，作为后续业务判断、统计或响应组装的输入。
    city_id = int(city_id) if city_id else None  # 计算或更新城市编号，作为后续业务判断、统计或响应组装的输入。
    city = db.session.get(City, city_id) if city_id else None  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。

    # 预测前确保均价缓存可用，再按需懒加载当前区域模型。
    if not _district_avg:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        _refresh_avgs()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    fitted = train(district_id) if district_id else False  # 计算或更新fitted中间数据，作为后续业务判断、统计或响应组装的输入。

    city_avg = _city_avg.get(city_id, _global_avg) if city_id else _global_avg  # 计算或更新city_avg中间数据，作为后续业务判断、统计或响应组装的输入。
    district_avg = _district_avg.get(district_id, city_avg) or city_avg or _global_avg  # 计算或更新district_avg中间数据，作为后续业务判断、统计或响应组装的输入。

    area = float(payload.get("area") or 0)  # 计算或更新area中间数据，作为后续业务判断、统计或响应组装的输入。
    age = max(0, _current_year() - int(payload.get("build_year") or _current_year()))  # 计算或更新age中间数据，作为后续业务判断、统计或响应组装的输入。
    floor_ratio = min((payload.get("floor") or 1) / (payload.get("total_floors") or 1), 1.0)  # 计算或更新floor_ratio中间数据，作为后续业务判断、统计或响应组装的输入。
    has_elevator = bool(payload.get("has_elevator"))  # 计算或更新has_elevator中间数据，作为后续业务判断、统计或响应组装的输入。

    model = _models.get(district_id) if district_id else None  # 计算或更新model中间数据，作为后续业务判断、统计或响应组装的输入。
    if fitted and model is not None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        # 模型路径使用与训练完全一致的特征顺序，避免特征错位。
        features = [[  # 初始化features中间数据列表，用于收集清洗后的多条业务数据。
            area,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            int(payload.get("rooms") or 0),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            int(payload.get("halls") or 0),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            age,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            1.0 if has_elevator else 0.0,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            floor_ratio,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            district_avg,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        ]]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        unit_price = float(model.predict(np.array(features))[0])  # 计算或更新unit_price中间数据，作为后续业务判断、统计或响应组装的输入。
        method = "district_random_forest"  # 计算或更新method中间数据，作为后续业务判断、统计或响应组装的输入。
    else:  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
        # 样本不足时采用启发式：以区域均价为基准，再按电梯、楼龄和楼层做轻量修正。
        unit_price = district_avg or _global_avg  # 计算或更新unit_price中间数据，作为后续业务判断、统计或响应组装的输入。
        unit_price *= 1 + (0.10 if has_elevator else 0)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        unit_price *= 1 - min(age, 30) * 0.004  # older buildings discount
        unit_price *= 0.95 + 0.10 * floor_ratio  # higher floors slight premium
        method = "heuristic"  # 计算或更新method中间数据，作为后续业务判断、统计或响应组装的输入。

    unit_price = max(round(unit_price), 0)  # 计算或更新unit_price中间数据，作为后续业务判断、统计或响应组装的输入。
    total_price = round(unit_price * area / 10000, 1)  # 万元
    return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        "unit_price": unit_price,  # 把unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "total_price": total_price,  # 把total_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "area": area,  # 把area字段写入响应数据，供前端页面、图表或后续接口读取。
        "city_id": city_id,  # 把city_id字段写入响应数据，供前端页面、图表或后续接口读取。
        "city_name": city.name if city else None,  # 把city_name字段写入响应数据，供前端页面、图表或后续接口读取。
        "district_id": district_id,  # 把district_id字段写入响应数据，供前端页面、图表或后续接口读取。
        "district_name": district.name if district else None,  # 把district_name字段写入响应数据，供前端页面、图表或后续接口读取。
        "method": method,  # 把method字段写入响应数据，供前端页面、图表或后续接口读取。
        "training_scope": district.name if district else "区域均值兜底",  # 把training_scope字段写入响应数据，供前端页面、图表或后续接口读取。
        "training_sample_count": _model_samples.get(district_id, 0) if district_id else 0,  # 把training_sample_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "city_avg_unit_price": round(city_avg) if city_avg else None,  # 把city_avg_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "district_avg_unit_price": round(district_avg) if district_avg else None,  # 把district_avg_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
