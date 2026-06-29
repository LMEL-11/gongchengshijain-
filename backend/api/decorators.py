"""认证/授权装饰器。

基于 JWT Bearer Token 的 ``@login_required`` 和 ``@admin_required``。
"""
from functools import wraps
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app, g, jsonify, request

from extensions import db
from models.user import User


def _create_token(user_id: int, role: str) -> str:
    """签发 JWT 令牌，默认 24 小时过期。"""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def login_required(fn):
    """从 ``Authorization: Bearer <token>`` 头解析 JWT 并注入 ``g.current_user``。"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        """包裹被装饰的视图函数并执行权限校验。"""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify(code=401, message="未登录，请先登录"), 401

        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify(code=401, message="登录已过期，请重新登录"), 401
        except jwt.InvalidTokenError:
            return jsonify(code=401, message="无效的登录凭证，请重新登录"), 401

        user = db.session.get(User, payload["user_id"])
        if user is None:
            return jsonify(code=401, message="用户不存在"), 401

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    """先校验登录态，再校验当前用户是否拥有 ``admin`` 角色。"""

    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        """包裹被装饰的视图函数并执行权限校验。"""
        if g.current_user.role != "admin":
            return jsonify(code=403, message="需要管理员权限"), 403
        return fn(*args, **kwargs)

    return wrapper
