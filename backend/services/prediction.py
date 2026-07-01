"""房价预测 Price-prediction service.

Trains one regression model per selected district and caches it in memory. The
selected administrative district / business area is the training scope, so a
prediction for 济南·省体 is trained from 省体 listings instead of the whole city
or national dataset. Degrades gracefully to a district-average heuristic if
scikit-learn is unavailable or the selected district has too little data.
"""
from datetime import datetime  # 从 datetime 导入 datetime，供本文件后续逻辑调用。
from typing import Any, Optional  # 从 typing 导入 Any, Optional，供本文件后续逻辑调用。

from sqlalchemy import func  # 从 sqlalchemy 导入 func，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import City, District, Property  # 从 models 导入 City, District, Property，供本文件后续逻辑调用。

try:  # 开始执行可能抛出异常的代码块。
    import numpy as np  # 导入 numpy as np 模块，为当前文件提供所需功能。
    from sklearn.ensemble import RandomForestRegressor  # 从 sklearn.ensemble 导入 RandomForestRegressor，供本文件后续逻辑调用。

    _SKLEARN = True  # 设置 _SKLEARN 的值，供后续业务判断、查询或响应组装使用。
except Exception:  # pragma: no cover - import guard
    _SKLEARN = False  # 设置 _SKLEARN 的值，供后续业务判断、查询或响应组装使用。

# Module-level cache: trained estimators by district + average-price lookups.
_models: dict[int, Optional[Any]] = {}  # 设置 _models: dict[int, Optional[Any 的值，供后续业务判断、查询或响应组装使用。
_model_samples: dict[int, int] = {}  # 设置 _model_samples: dict[int, int 的值，供后续业务判断、查询或响应组装使用。
_district_avg: dict[int, float] = {}  # 设置 _district_avg: dict[int, float 的值，供后续业务判断、查询或响应组装使用。
_city_avg: dict[int, float] = {}  # 设置 _city_avg: dict[int, float 的值，供后续业务判断、查询或响应组装使用。
_global_avg: float = 0.0  # 设置 _global_avg: float 的值，供后续业务判断、查询或响应组装使用。

FEATURES = ("area", "rooms", "halls", "building_age", "has_elevator", "floor_ratio", "district_avg")  # 设置 FEATURES 的值，供后续业务判断、查询或响应组装使用。


def _current_year() -> int:  # 定义 _current_year 函数，集中处理这一段业务逻辑。
    """返回当前年份，用作预测特征的兜底建成年份。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return datetime.now().year  # 返回处理后的结果给调用方继续使用。


def _row_features(p: Property, district_avg: float) -> list[float]:  # 定义 _row_features 函数，集中处理这一段业务逻辑。
    """把房源记录转换为模型训练需要的特征向量。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    # 特征尽量只使用用户预测时也能填写的字段，避免训练/预测口径不一致。
    age = max(0, _current_year() - (p.build_year or _current_year()))  # 设置 age 的值，供后续业务判断、查询或响应组装使用。
    floor_ratio = (p.floor or 1) / (p.total_floors or 1)  # 设置 floor_ratio 的值，供后续业务判断、查询或响应组装使用。
    return [  # 返回处理后的结果给调用方继续使用。
        p.area or 0,  # 执行当前代码行对应的业务处理步骤。
        p.rooms or 0,  # 执行当前代码行对应的业务处理步骤。
        p.halls or 0,  # 执行当前代码行对应的业务处理步骤。
        age,  # 执行当前代码行对应的业务处理步骤。
        1.0 if p.has_elevator else 0.0,  # 执行当前代码行对应的业务处理步骤。
        min(floor_ratio, 1.0),  # 执行当前代码行对应的业务处理步骤。
        district_avg,  # 执行当前代码行对应的业务处理步骤。
    ]  # 结束当前多行数据结构或函数调用。


def _refresh_avgs() -> None:  # 定义 _refresh_avgs 函数，集中处理这一段业务逻辑。
    """Refresh district, city, and global average unit prices."""  # 保留字符串内容，作为说明文本或页面展示文案。
    global _district_avg, _city_avg, _global_avg  # 执行当前代码行对应的业务处理步骤。

    # 均价缓存既是模型特征，也是样本不足或 sklearn 不可用时的兜底估价基准。
    _district_avg = {  # 设置 _district_avg 的值，供后续业务判断、查询或响应组装使用。
        district_id: round(avg_price)  # 执行当前代码行对应的业务处理步骤。
        for district_id, avg_price in (  # 遍历当前数据集合，逐项完成处理。
            db.session.query(District.id, func.avg(Property.unit_price))  # 构造数据库查询，用于读取、筛选或聚合业务数据。
            .join(Property, Property.district_id == District.id)  # 把关联表纳入查询，获取跨表维度的数据。
            .filter(Property.unit_price.isnot(None))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
            .group_by(District.id)  # 按指定业务维度分组，生成聚合统计结果。
            .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
        )  # 结束当前多行数据结构或函数调用。
        if avg_price  # 判断当前条件是否成立，决定是否进入对应处理分支。
    }  # 结束当前多行数据结构或函数调用。
    _city_avg = {  # 设置 _city_avg 的值，供后续业务判断、查询或响应组装使用。
        city_id: round(avg_price)  # 执行当前代码行对应的业务处理步骤。
        for city_id, avg_price in (  # 遍历当前数据集合，逐项完成处理。
            db.session.query(District.city_id, func.avg(Property.unit_price))  # 构造数据库查询，用于读取、筛选或聚合业务数据。
            .join(Property, Property.district_id == District.id)  # 把关联表纳入查询，获取跨表维度的数据。
            .filter(Property.unit_price.isnot(None))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
            .group_by(District.city_id)  # 按指定业务维度分组，生成聚合统计结果。
            .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
        )  # 结束当前多行数据结构或函数调用。
        if avg_price  # 判断当前条件是否成立，决定是否进入对应处理分支。
    }  # 结束当前多行数据结构或函数调用。
    _global_avg = round(sum(_city_avg.values()) / len(_city_avg)) if _city_avg else 0  # 设置 _global_avg 的值，供后续业务判断、查询或响应组装使用。


def train(district_id: Optional[int] = None, force: bool = False) -> bool:  # 定义 train 函数，集中处理这一段业务逻辑。
    """Train (or re-train) a district model.

    Returns True if a real random-forest model was fitted. If ``district_id`` is
    omitted, existing district-model caches are cleared and averages are
    refreshed; the next prediction lazily trains its selected district.
    """
    if force or not _district_avg:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        _refresh_avgs()  # 执行当前代码行对应的业务处理步骤。

    if district_id is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        if force:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            _models.clear()  # 执行当前代码行对应的业务处理步骤。
            _model_samples.clear()  # 执行当前代码行对应的业务处理步骤。
        return False  # 返回处理后的结果给调用方继续使用。

    if not _SKLEARN:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        _models[district_id] = None  # 设置 _models[district_id 的值，供后续业务判断、查询或响应组装使用。
        _model_samples[district_id] = 0  # 设置 _model_samples[district_id 的值，供后续业务判断、查询或响应组装使用。
        return False  # 返回处理后的结果给调用方继续使用。

    if district_id in _models and not force:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return _models[district_id] is not None  # 返回处理后的结果给调用方继续使用。

    # 每个区域单独训练，避免不同商圈价格水平混在一起削弱局部预测能力。
    props = (  # 设置 props 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(Property)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .filter(Property.district_id == district_id)  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .filter(Property.unit_price.isnot(None), Property.area.isnot(None))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    if len(props) < 30:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        _models[district_id] = None  # 设置 _models[district_id 的值，供后续业务判断、查询或响应组装使用。
        _model_samples[district_id] = len(props)  # 设置 _model_samples[district_id 的值，供后续业务判断、查询或响应组装使用。
        return False  # 返回处理后的结果给调用方继续使用。

    # X 保存可解释的结构化房源特征，y 保存目标单价。
    X, y = [], []  # 设置 X, y 的值，供后续业务判断、查询或响应组装使用。
    district_avg = _district_avg.get(district_id, _global_avg)  # 设置 district_avg 的值，供后续业务判断、查询或响应组装使用。
    for p in props:  # 遍历当前数据集合，逐项完成处理。
        X.append(_row_features(p, district_avg))  # 执行当前代码行对应的业务处理步骤。
        y.append(p.unit_price)  # 执行当前代码行对应的业务处理步骤。

    model = RandomForestRegressor(n_estimators=120, random_state=42, max_depth=12)  # 设置 model 的值，供后续业务判断、查询或响应组装使用。
    model.fit(np.array(X), np.array(y))  # 执行当前代码行对应的业务处理步骤。
    _models[district_id] = model  # 设置 _models[district_id 的值，供后续业务判断、查询或响应组装使用。
    _model_samples[district_id] = len(props)  # 设置 _model_samples[district_id 的值，供后续业务判断、查询或响应组装使用。
    return True  # 返回处理后的结果给调用方继续使用。


def predict(payload: dict) -> dict:  # 定义 predict 函数，集中处理这一段业务逻辑。
    """Predict unit & total price for a hypothetical listing.

    ``payload`` keys: city_id, district_id, area, rooms, halls, build_year,
    has_elevator, floor, total_floors.
    """
    district_id = payload.get("district_id")  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
    district = db.session.get(District, district_id) if district_id else None  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
    city_id = district.city_id if district else payload.get("city_id")  # 设置 city_id 的值，供后续业务判断、查询或响应组装使用。
    city_id = int(city_id) if city_id else None  # 设置 city_id 的值，供后续业务判断、查询或响应组装使用。
    city = db.session.get(City, city_id) if city_id else None  # 设置 city 的值，供后续业务判断、查询或响应组装使用。

    # 预测前确保均价缓存可用，再按需懒加载当前区域模型。
    if not _district_avg:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        _refresh_avgs()  # 执行当前代码行对应的业务处理步骤。
    fitted = train(district_id) if district_id else False  # 设置 fitted 的值，供后续业务判断、查询或响应组装使用。

    city_avg = _city_avg.get(city_id, _global_avg) if city_id else _global_avg  # 设置 city_avg 的值，供后续业务判断、查询或响应组装使用。
    district_avg = _district_avg.get(district_id, city_avg) or city_avg or _global_avg  # 设置 district_avg 的值，供后续业务判断、查询或响应组装使用。

    area = float(payload.get("area") or 0)  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
    age = max(0, _current_year() - int(payload.get("build_year") or _current_year()))  # 设置 age 的值，供后续业务判断、查询或响应组装使用。
    floor_ratio = min((payload.get("floor") or 1) / (payload.get("total_floors") or 1), 1.0)  # 设置 floor_ratio 的值，供后续业务判断、查询或响应组装使用。
    has_elevator = bool(payload.get("has_elevator"))  # 设置 has_elevator 的值，供后续业务判断、查询或响应组装使用。

    model = _models.get(district_id) if district_id else None  # 设置 model 的值，供后续业务判断、查询或响应组装使用。
    if fitted and model is not None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        # 模型路径使用与训练完全一致的特征顺序，避免特征错位。
        features = [[  # 设置 features 的值，供后续业务判断、查询或响应组装使用。
            area,  # 执行当前代码行对应的业务处理步骤。
            int(payload.get("rooms") or 0),  # 执行当前代码行对应的业务处理步骤。
            int(payload.get("halls") or 0),  # 执行当前代码行对应的业务处理步骤。
            age,  # 执行当前代码行对应的业务处理步骤。
            1.0 if has_elevator else 0.0,  # 执行当前代码行对应的业务处理步骤。
            floor_ratio,  # 执行当前代码行对应的业务处理步骤。
            district_avg,  # 执行当前代码行对应的业务处理步骤。
        ]]  # 结束当前多行数据结构或函数调用。
        unit_price = float(model.predict(np.array(features))[0])  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
        method = "district_random_forest"  # 设置 method 的值，供后续业务判断、查询或响应组装使用。
    else:  # 处理前面条件都未命中的兜底分支。
        # 样本不足时采用启发式：以区域均价为基准，再按电梯、楼龄和楼层做轻量修正。
        unit_price = district_avg or _global_avg  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
        unit_price *= 1 + (0.10 if has_elevator else 0)  # 设置 unit_price * 的值，供后续业务判断、查询或响应组装使用。
        unit_price *= 1 - min(age, 30) * 0.004  # 设置 unit_price * 的值，供后续业务判断、查询或响应组装使用。
        unit_price *= 0.95 + 0.10 * floor_ratio  # 设置 unit_price * 的值，供后续业务判断、查询或响应组装使用。
        method = "heuristic"  # 设置 method 的值，供后续业务判断、查询或响应组装使用。

    unit_price = max(round(unit_price), 0)  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
    total_price = round(unit_price * area / 10000, 1)  # 设置 total_price 的值，供后续业务判断、查询或响应组装使用。
    return {  # 返回处理后的结果给调用方继续使用。
        "unit_price": unit_price,  # 保留字符串内容，作为说明文本或页面展示文案。
        "total_price": total_price,  # 保留字符串内容，作为说明文本或页面展示文案。
        "area": area,  # 保留字符串内容，作为说明文本或页面展示文案。
        "city_id": city_id,  # 保留字符串内容，作为说明文本或页面展示文案。
        "city_name": city.name if city else None,  # 保留字符串内容，作为说明文本或页面展示文案。
        "district_id": district_id,  # 保留字符串内容，作为说明文本或页面展示文案。
        "district_name": district.name if district else None,  # 保留字符串内容，作为说明文本或页面展示文案。
        "method": method,  # 保留字符串内容，作为说明文本或页面展示文案。
        "training_scope": district.name if district else "区域均值兜底",  # 保留字符串内容，作为说明文本或页面展示文案。
        "training_sample_count": _model_samples.get(district_id, 0) if district_id else 0,  # 保留字符串内容，作为说明文本或页面展示文案。
        "city_avg_unit_price": round(city_avg) if city_avg else None,  # 保留字符串内容，作为说明文本或页面展示文案。
        "district_avg_unit_price": round(district_avg) if district_avg else None,  # 保留字符串内容，作为说明文本或页面展示文案。
    }  # 结束当前多行数据结构或函数调用。
