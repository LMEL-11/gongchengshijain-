"""认证/授权装饰器。

基于 JWT Bearer Token 的 ``@login_required`` 和 ``@admin_required``。
"""
from functools import wraps  # 导入本行所需的模块或对象。
from datetime import datetime, timedelta, timezone  # 导入本行所需的模块或对象。

import jwt  # 导入本行所需的模块或对象。
from flask import current_app, g, jsonify, request  # 导入本行所需的模块或对象。

from extensions import db  # 导入本行所需的模块或对象。
from models.user import User  # 导入本行所需的模块或对象。


def _create_token(user_id: int, role: str) -> str:  # 声明函数或方法入口。
    """签发 JWT 令牌，默认 24 小时过期。"""
    payload = {  # 赋值或更新当前变量/字段。
        "user_id": user_id,  # 设置当前数据项或参数。
        "role": role,  # 设置当前数据项或参数。
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),  # 赋值或更新当前变量/字段。
    }  # 结束当前数据结构或调用块。
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")  # 返回当前逻辑的处理结果。


def login_required(fn):  # 声明函数或方法入口。
    """从 ``Authorization: Bearer <token>`` 头解析 JWT 并注入 ``g.current_user``。"""

    @wraps(fn)  # 应用装饰器配置路由、权限或命令。
    def wrapper(*args, **kwargs):  # 声明函数或方法入口。
        """包裹被装饰的视图函数并执行权限校验。"""
        auth_header = request.headers.get("Authorization", "")  # 赋值或更新当前变量/字段。
        if not auth_header.startswith("Bearer "):  # 根据条件判断是否进入该分支。
            return jsonify(code=401, message="未登录，请先登录"), 401  # 返回当前逻辑的处理结果。

        token = auth_header[7:]  # 赋值或更新当前变量/字段。
        try:  # 开始执行可能出现异常的逻辑。
            payload = jwt.decode(  # 赋值或更新当前变量/字段。
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]  # 赋值或更新当前变量/字段。
            )  # 结束当前数据结构或调用块。
        except jwt.ExpiredSignatureError:  # 捕获异常并执行错误处理。
            return jsonify(code=401, message="登录已过期，请重新登录"), 401  # 返回当前逻辑的处理结果。
        except jwt.InvalidTokenError:  # 捕获异常并执行错误处理。
            return jsonify(code=401, message="无效的登录凭证，请重新登录"), 401  # 返回当前逻辑的处理结果。

        user = db.session.get(User, payload["user_id"])  # 赋值或更新当前变量/字段。
        if user is None:  # 根据条件判断是否进入该分支。
            return jsonify(code=401, message="用户不存在"), 401  # 返回当前逻辑的处理结果。

        g.current_user = user  # 赋值或更新当前变量/字段。
        return fn(*args, **kwargs)  # 返回当前逻辑的处理结果。

    return wrapper  # 返回当前逻辑的处理结果。


def admin_required(fn):  # 声明函数或方法入口。
    """先校验登录态，再校验当前用户是否拥有 ``admin`` 角色。"""

    @wraps(fn)  # 应用装饰器配置路由、权限或命令。
    @login_required  # 应用装饰器配置路由、权限或命令。
    def wrapper(*args, **kwargs):  # 声明函数或方法入口。
        """包裹被装饰的视图函数并执行权限校验。"""
        if g.current_user.role != "admin":  # 根据条件判断是否进入该分支。
            return jsonify(code=403, message="需要管理员权限"), 403  # 返回当前逻辑的处理结果。
        return fn(*args, **kwargs)  # 返回当前逻辑的处理结果。

    return wrapper  # 返回当前逻辑的处理结果。
