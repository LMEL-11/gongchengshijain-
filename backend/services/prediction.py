"""房价预测 Price-prediction service.

Trains one regression model per selected district and caches it in memory. The
selected administrative district / business area is the training scope, so a
prediction for 济南·省体 is trained from 省体 listings instead of the whole city
or national dataset. Degrades gracefully to a district-average heuristic if
scikit-learn is unavailable or the selected district has too little data.
"""
from datetime import datetime  # 导入本行所需的模块或对象。
from typing import Any, Optional  # 导入本行所需的模块或对象。

from sqlalchemy import func  # 导入本行所需的模块或对象。

from extensions import db  # 导入本行所需的模块或对象。
from models import City, District, Property  # 导入本行所需的模块或对象。

try:  # scikit-learn is optional at runtime
    import numpy as np  # 导入本行所需的模块或对象。
    from sklearn.ensemble import RandomForestRegressor  # 导入本行所需的模块或对象。

    _SKLEARN = True  # 赋值或更新当前变量/字段。
except Exception:  # pragma: no cover - import guard
    _SKLEARN = False  # 赋值或更新当前变量/字段。

# Module-level cache: trained estimators by district + average-price lookups.
_models: dict[int, Optional[Any]] = {}  # 赋值或更新当前变量/字段。
_model_samples: dict[int, int] = {}  # 赋值或更新当前变量/字段。
_district_avg: dict[int, float] = {}  # 赋值或更新当前变量/字段。
_city_avg: dict[int, float] = {}  # 赋值或更新当前变量/字段。
_global_avg: float = 0.0  # 赋值或更新当前变量/字段。

FEATURES = ("area", "rooms", "halls", "building_age", "has_elevator", "floor_ratio", "district_avg")  # 赋值或更新当前变量/字段。


def _current_year() -> int:  # 声明函数或方法入口。
    """返回当前年份，用作预测特征的兜底建成年份。"""
    return datetime.now().year  # 返回当前逻辑的处理结果。


def _row_features(p: Property, district_avg: float) -> list[float]:  # 声明函数或方法入口。
    """把房源记录转换为模型训练需要的特征向量。"""
    age = max(0, _current_year() - (p.build_year or _current_year()))  # 赋值或更新当前变量/字段。
    floor_ratio = (p.floor or 1) / (p.total_floors or 1)  # 赋值或更新当前变量/字段。
    return [  # 返回当前逻辑的处理结果。
        p.area or 0,  # 设置当前数据项或参数。
        p.rooms or 0,  # 设置当前数据项或参数。
        p.halls or 0,  # 设置当前数据项或参数。
        age,  # 设置当前数据项或参数。
        1.0 if p.has_elevator else 0.0,  # 设置当前数据项或参数。
        min(floor_ratio, 1.0),  # 设置当前数据项或参数。
        district_avg,  # 设置当前数据项或参数。
    ]  # 结束当前数据结构或调用块。


def _refresh_avgs() -> None:  # 声明函数或方法入口。
    """Refresh district, city, and global average unit prices."""
    global _district_avg, _city_avg, _global_avg  # 执行本行代码逻辑。

    _district_avg = {  # 赋值或更新当前变量/字段。
        district_id: round(avg_price)  # 设置当前数据项或参数。
        for district_id, avg_price in (  # 遍历集合中的每一项并执行处理。
            db.session.query(District.id, func.avg(Property.unit_price))  # 执行本行代码逻辑。
            .join(Property, Property.district_id == District.id)  # 执行本行代码逻辑。
            .filter(Property.unit_price.isnot(None))  # 执行本行代码逻辑。
            .group_by(District.id)  # 执行本行代码逻辑。
            .all()  # 执行本行代码逻辑。
        )  # 结束当前数据结构或调用块。
        if avg_price  # 根据条件判断是否进入该分支。
    }  # 结束当前数据结构或调用块。
    _city_avg = {  # 赋值或更新当前变量/字段。
        city_id: round(avg_price)  # 设置当前数据项或参数。
        for city_id, avg_price in (  # 遍历集合中的每一项并执行处理。
            db.session.query(District.city_id, func.avg(Property.unit_price))  # 执行本行代码逻辑。
            .join(Property, Property.district_id == District.id)  # 执行本行代码逻辑。
            .filter(Property.unit_price.isnot(None))  # 执行本行代码逻辑。
            .group_by(District.city_id)  # 执行本行代码逻辑。
            .all()  # 执行本行代码逻辑。
        )  # 结束当前数据结构或调用块。
        if avg_price  # 根据条件判断是否进入该分支。
    }  # 结束当前数据结构或调用块。
    _global_avg = round(sum(_city_avg.values()) / len(_city_avg)) if _city_avg else 0  # 赋值或更新当前变量/字段。


def train(district_id: Optional[int] = None, force: bool = False) -> bool:  # 声明函数或方法入口。
    """Train (or re-train) a district model.

    Returns True if a real random-forest model was fitted. If ``district_id`` is
    omitted, existing district-model caches are cleared and averages are
    refreshed; the next prediction lazily trains its selected district.
    """
    if force or not _district_avg:  # 根据条件判断是否进入该分支。
        _refresh_avgs()  # 执行本行代码逻辑。

    if district_id is None:  # 根据条件判断是否进入该分支。
        if force:  # 根据条件判断是否进入该分支。
            _models.clear()  # 执行本行代码逻辑。
            _model_samples.clear()  # 执行本行代码逻辑。
        return False  # 返回当前逻辑的处理结果。

    if not _SKLEARN:  # 根据条件判断是否进入该分支。
        _models[district_id] = None  # 赋值或更新当前变量/字段。
        _model_samples[district_id] = 0  # 赋值或更新当前变量/字段。
        return False  # 返回当前逻辑的处理结果。

    if district_id in _models and not force:  # 根据条件判断是否进入该分支。
        return _models[district_id] is not None  # 返回当前逻辑的处理结果。

    props = (  # 赋值或更新当前变量/字段。
        db.session.query(Property)  # 执行本行代码逻辑。
        .filter(Property.district_id == district_id)  # 执行本行代码逻辑。
        .filter(Property.unit_price.isnot(None), Property.area.isnot(None))  # 执行本行代码逻辑。
        .all()  # 执行本行代码逻辑。
    )  # 结束当前数据结构或调用块。
    if len(props) < 30:  # not enough signal to fit anything meaningful
        _models[district_id] = None  # 赋值或更新当前变量/字段。
        _model_samples[district_id] = len(props)  # 赋值或更新当前变量/字段。
        return False  # 返回当前逻辑的处理结果。

    X, y = [], []  # 赋值或更新当前变量/字段。
    district_avg = _district_avg.get(district_id, _global_avg)  # 赋值或更新当前变量/字段。
    for p in props:  # 遍历集合中的每一项并执行处理。
        X.append(_row_features(p, district_avg))  # 执行本行代码逻辑。
        y.append(p.unit_price)  # 执行本行代码逻辑。

    model = RandomForestRegressor(n_estimators=120, random_state=42, max_depth=12)  # 赋值或更新当前变量/字段。
    model.fit(np.array(X), np.array(y))  # 执行本行代码逻辑。
    _models[district_id] = model  # 赋值或更新当前变量/字段。
    _model_samples[district_id] = len(props)  # 赋值或更新当前变量/字段。
    return True  # 返回当前逻辑的处理结果。


def predict(payload: dict) -> dict:  # 声明函数或方法入口。
    """Predict unit & total price for a hypothetical listing.

    ``payload`` keys: city_id, district_id, area, rooms, halls, build_year,
    has_elevator, floor, total_floors.
    """
    district_id = payload.get("district_id")  # 赋值或更新当前变量/字段。
    district = db.session.get(District, district_id) if district_id else None  # 赋值或更新当前变量/字段。
    city_id = district.city_id if district else payload.get("city_id")  # 赋值或更新当前变量/字段。
    city_id = int(city_id) if city_id else None  # 赋值或更新当前变量/字段。
    city = db.session.get(City, city_id) if city_id else None  # 赋值或更新当前变量/字段。

    if not _district_avg:  # 根据条件判断是否进入该分支。
        _refresh_avgs()  # 执行本行代码逻辑。
    fitted = train(district_id) if district_id else False  # 赋值或更新当前变量/字段。

    city_avg = _city_avg.get(city_id, _global_avg) if city_id else _global_avg  # 赋值或更新当前变量/字段。
    district_avg = _district_avg.get(district_id, city_avg) or city_avg or _global_avg  # 赋值或更新当前变量/字段。

    area = float(payload.get("area") or 0)  # 赋值或更新当前变量/字段。
    age = max(0, _current_year() - int(payload.get("build_year") or _current_year()))  # 赋值或更新当前变量/字段。
    floor_ratio = min((payload.get("floor") or 1) / (payload.get("total_floors") or 1), 1.0)  # 赋值或更新当前变量/字段。
    has_elevator = bool(payload.get("has_elevator"))  # 赋值或更新当前变量/字段。

    model = _models.get(district_id) if district_id else None  # 赋值或更新当前变量/字段。
    if fitted and model is not None:  # 根据条件判断是否进入该分支。
        features = [[  # 赋值或更新当前变量/字段。
            area,  # 设置当前数据项或参数。
            int(payload.get("rooms") or 0),  # 设置当前数据项或参数。
            int(payload.get("halls") or 0),  # 设置当前数据项或参数。
            age,  # 设置当前数据项或参数。
            1.0 if has_elevator else 0.0,  # 设置当前数据项或参数。
            floor_ratio,  # 设置当前数据项或参数。
            district_avg,  # 设置当前数据项或参数。
        ]]  # 执行本行代码逻辑。
        unit_price = float(model.predict(np.array(features))[0])  # 赋值或更新当前变量/字段。
        method = "district_random_forest"  # 赋值或更新当前变量/字段。
    else:  # 处理条件不满足时的兜底分支。
        # Heuristic fallback: district average nudged by a few adjustments.
        unit_price = district_avg or _global_avg  # 赋值或更新当前变量/字段。
        unit_price *= 1 + (0.10 if has_elevator else 0)  # 赋值或更新当前变量/字段。
        unit_price *= 1 - min(age, 30) * 0.004  # older buildings discount
        unit_price *= 0.95 + 0.10 * floor_ratio  # higher floors slight premium
        method = "heuristic"  # 赋值或更新当前变量/字段。

    unit_price = max(round(unit_price), 0)  # 赋值或更新当前变量/字段。
    total_price = round(unit_price * area / 10000, 1)  # 万元
    return {  # 返回当前逻辑的处理结果。
        "unit_price": unit_price,  # 设置当前数据项或参数。
        "total_price": total_price,  # 设置当前数据项或参数。
        "area": area,  # 设置当前数据项或参数。
        "city_id": city_id,  # 设置当前数据项或参数。
        "city_name": city.name if city else None,  # 设置当前数据项或参数。
        "district_id": district_id,  # 设置当前数据项或参数。
        "district_name": district.name if district else None,  # 设置当前数据项或参数。
        "method": method,  # 设置当前数据项或参数。
        "training_scope": district.name if district else "区域均值兜底",  # 设置当前数据项或参数。
        "training_sample_count": _model_samples.get(district_id, 0) if district_id else 0,  # 设置当前数据项或参数。
        "city_avg_unit_price": round(city_avg) if city_avg else None,  # 设置当前数据项或参数。
        "district_avg_unit_price": round(district_avg) if district_avg else None,  # 设置当前数据项或参数。
    }  # 结束当前数据结构或调用块。
