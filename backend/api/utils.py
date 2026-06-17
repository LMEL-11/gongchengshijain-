"""Small request/response helpers shared across API blueprints."""
from flask import jsonify, request


def ok(data=None, message: str = "ok"):
    """Wrap a successful payload in the standard response envelope."""
    return jsonify({"code": 0, "message": message, "data": data})


def get_int(name: str, default=None):
    val = request.args.get(name)
    if val in (None, ""):
        return default
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def get_float(name: str, default=None):
    val = request.args.get(name)
    if val in (None, ""):
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default
