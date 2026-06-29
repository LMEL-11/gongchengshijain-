"""认证蓝图 —— 登录 / 获取当前用户 / 退出。"""
from flask import Blueprint, g, jsonify, request  # 导入本行所需的模块或对象。

from models.user import User  # 导入本行所需的模块或对象。
from extensions import db  # 导入本行所需的模块或对象。
from .decorators import _create_token, login_required  # 导入本行所需的模块或对象。
from .utils import ok  # 导入本行所需的模块或对象。

bp = Blueprint("auth", __name__, url_prefix="/api/auth")  # 赋值或更新当前变量/字段。


@bp.post("/login")  # 应用装饰器配置路由、权限或命令。
def login():  # 声明函数或方法入口。
    """处理登录请求，校验账号密码并返回登录令牌。"""
    body = request.get_json(silent=True) or {}  # 赋值或更新当前变量/字段。
    username = (body.get("username") or "").strip()  # 赋值或更新当前变量/字段。
    password = body.get("password") or ""  # 保留语法占位以便后续扩展。

    if not username or not password:  # 根据条件判断是否进入该分支。
        return jsonify(code=1, message="用户名和密码不能为空"), 400  # 返回当前逻辑的处理结果。

    user = db.session.query(User).filter_by(username=username).first()  # 赋值或更新当前变量/字段。
    if user is None or not user.check_password(password):  # 根据条件判断是否进入该分支。
        return jsonify(code=1, message="用户名或密码错误"), 401  # 返回当前逻辑的处理结果。

    token = _create_token(user.id, user.role)  # 赋值或更新当前变量/字段。
    return ok({"token": token, "user": user.to_dict()})  # 返回当前逻辑的处理结果。


@bp.get("/me")  # 应用装饰器配置路由、权限或命令。
@login_required  # 应用装饰器配置路由、权限或命令。
def me():  # 声明函数或方法入口。
    """返回当前登录用户的信息。"""
    return ok(g.current_user.to_dict())  # 返回当前逻辑的处理结果。


@bp.post("/logout")  # 应用装饰器配置路由、权限或命令。
@login_required  # 应用装饰器配置路由、权限或命令。
def logout():  # 声明函数或方法入口。
    """JWT 为无状态令牌；客户端丢弃 token 即完成退出。"""
    return ok(None, message="已退出登录")  # 返回当前逻辑的处理结果。
