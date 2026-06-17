"""房价预测 Price-prediction service.

Trains one regression model per selected district and caches it in memory. The
selected administrative district / business area is the training scope, so a
prediction for 济南·省体 is trained from 省体 listings instead of the whole city
or national dataset. Degrades gracefully to a district-average heuristic if
scikit-learn is unavailable or the selected district has too little data.
"""
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import func

from extensions import db
from models import City, District, Property

try:  # scikit-learn is optional at runtime
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor

    _SKLEARN = True
except Exception:  # pragma: no cover - import guard
    _SKLEARN = False

# Module-level cache: trained estimators by district + average-price lookups.
_models: dict[int, Optional[Any]] = {}
_model_samples: dict[int, int] = {}
_district_avg: dict[int, float] = {}
_city_avg: dict[int, float] = {}
_global_avg: float = 0.0

FEATURES = ("area", "rooms", "halls", "building_age", "has_elevator", "floor_ratio", "district_avg")


def _current_year() -> int:
    return datetime.now().year


def _row_features(p: Property, district_avg: float) -> list[float]:
    age = max(0, _current_year() - (p.build_year or _current_year()))
    floor_ratio = (p.floor or 1) / (p.total_floors or 1)
    return [
        p.area or 0,
        p.rooms or 0,
        p.halls or 0,
        age,
        1.0 if p.has_elevator else 0.0,
        min(floor_ratio, 1.0),
        district_avg,
    ]


def _refresh_avgs() -> None:
    """Refresh district, city, and global average unit prices."""
    global _district_avg, _city_avg, _global_avg

    _district_avg = {
        district_id: round(avg_price)
        for district_id, avg_price in (
            db.session.query(District.id, func.avg(Property.unit_price))
            .join(Property, Property.district_id == District.id)
            .filter(Property.unit_price.isnot(None))
            .group_by(District.id)
            .all()
        )
        if avg_price
    }
    _city_avg = {
        city_id: round(avg_price)
        for city_id, avg_price in (
            db.session.query(District.city_id, func.avg(Property.unit_price))
            .join(Property, Property.district_id == District.id)
            .filter(Property.unit_price.isnot(None))
            .group_by(District.city_id)
            .all()
        )
        if avg_price
    }
    _global_avg = round(sum(_city_avg.values()) / len(_city_avg)) if _city_avg else 0


def train(district_id: Optional[int] = None, force: bool = False) -> bool:
    """Train (or re-train) a district model.

    Returns True if a real random-forest model was fitted. If ``district_id`` is
    omitted, existing district-model caches are cleared and averages are
    refreshed; the next prediction lazily trains its selected district.
    """
    if force or not _district_avg:
        _refresh_avgs()

    if district_id is None:
        if force:
            _models.clear()
            _model_samples.clear()
        return False

    if not _SKLEARN:
        _models[district_id] = None
        _model_samples[district_id] = 0
        return False

    if district_id in _models and not force:
        return _models[district_id] is not None

    props = (
        db.session.query(Property)
        .filter(Property.district_id == district_id)
        .filter(Property.unit_price.isnot(None), Property.area.isnot(None))
        .all()
    )
    if len(props) < 30:  # not enough signal to fit anything meaningful
        _models[district_id] = None
        _model_samples[district_id] = len(props)
        return False

    X, y = [], []
    district_avg = _district_avg.get(district_id, _global_avg)
    for p in props:
        X.append(_row_features(p, district_avg))
        y.append(p.unit_price)

    model = RandomForestRegressor(n_estimators=120, random_state=42, max_depth=12)
    model.fit(np.array(X), np.array(y))
    _models[district_id] = model
    _model_samples[district_id] = len(props)
    return True


def predict(payload: dict) -> dict:
    """Predict unit & total price for a hypothetical listing.

    ``payload`` keys: city_id, district_id, area, rooms, halls, build_year,
    has_elevator, floor, total_floors.
    """
    district_id = payload.get("district_id")
    district = db.session.get(District, district_id) if district_id else None
    city_id = district.city_id if district else payload.get("city_id")
    city_id = int(city_id) if city_id else None
    city = db.session.get(City, city_id) if city_id else None

    if not _district_avg:
        _refresh_avgs()
    fitted = train(district_id) if district_id else False

    city_avg = _city_avg.get(city_id, _global_avg) if city_id else _global_avg
    district_avg = _district_avg.get(district_id, city_avg) or city_avg or _global_avg

    area = float(payload.get("area") or 0)
    age = max(0, _current_year() - int(payload.get("build_year") or _current_year()))
    floor_ratio = min((payload.get("floor") or 1) / (payload.get("total_floors") or 1), 1.0)
    has_elevator = bool(payload.get("has_elevator"))

    model = _models.get(district_id) if district_id else None
    if fitted and model is not None:
        features = [[
            area,
            int(payload.get("rooms") or 0),
            int(payload.get("halls") or 0),
            age,
            1.0 if has_elevator else 0.0,
            floor_ratio,
            district_avg,
        ]]
        unit_price = float(model.predict(np.array(features))[0])
        method = "district_random_forest"
    else:
        # Heuristic fallback: district average nudged by a few adjustments.
        unit_price = district_avg or _global_avg
        unit_price *= 1 + (0.10 if has_elevator else 0)
        unit_price *= 1 - min(age, 30) * 0.004  # older buildings discount
        unit_price *= 0.95 + 0.10 * floor_ratio  # higher floors slight premium
        method = "heuristic"

    unit_price = max(round(unit_price), 0)
    total_price = round(unit_price * area / 10000, 1)  # 万元
    return {
        "unit_price": unit_price,
        "total_price": total_price,
        "area": area,
        "city_id": city_id,
        "city_name": city.name if city else None,
        "district_id": district_id,
        "district_name": district.name if district else None,
        "method": method,
        "training_scope": district.name if district else "区域均值兜底",
        "training_sample_count": _model_samples.get(district_id, 0) if district_id else 0,
        "city_avg_unit_price": round(city_avg) if city_avg else None,
        "district_avg_unit_price": round(district_avg) if district_avg else None,
    }
