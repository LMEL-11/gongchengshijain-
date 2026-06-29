"""认证蓝图 —— 登录 / 获取当前用户 / 退出。"""
from flask import Blueprint, g, jsonify, request

from models.user import User
from extensions import db
from .decorators import _create_token, login_required
from .utils import ok

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login():
    """处理登录请求，校验账号密码并返回登录令牌。"""
    body = request.get_json(silent=True) or {}
    username = (body.get("username") or "").strip()
    password = body.get("password") or ""

    if not username or not password:
        return jsonify(code=1, message="用户名和密码不能为空"), 400

    user = db.session.query(User).filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify(code=1, message="用户名或密码错误"), 401

    token = _create_token(user.id, user.role)
    return ok({"token": token, "user": user.to_dict()})


@bp.get("/me")
@login_required
def me():
    """返回当前登录用户的信息。"""
    return ok(g.current_user.to_dict())


@bp.post("/logout")
@login_required
def logout():
    """JWT 为无状态令牌；客户端丢弃 token 即完成退出。"""
    return ok(None, message="已退出登录")
