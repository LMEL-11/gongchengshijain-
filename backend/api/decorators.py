"""认证/授权装饰器。

基于 JWT Bearer Token 的 ``@login_required`` 和 ``@admin_required``。
"""
from functools import wraps  # 逐行注释：导入本行所需的模块或对象。
from datetime import datetime, timedelta, timezone  # 逐行注释：导入本行所需的模块或对象。

import jwt  # 逐行注释：导入本行所需的模块或对象。
from flask import current_app, g, jsonify, request  # 逐行注释：导入本行所需的模块或对象。

from extensions import db  # 逐行注释：导入本行所需的模块或对象。
from models.user import User  # 逐行注释：导入本行所需的模块或对象。


def _create_token(user_id: int, role: str) -> str:  # 逐行注释：声明函数或方法入口。
    """签发 JWT 令牌，默认 24 小时过期。"""
    payload = {  # 逐行注释：赋值或更新当前变量/字段。
        "user_id": user_id,  # 逐行注释：设置当前数据项或参数。
        "role": role,  # 逐行注释：设置当前数据项或参数。
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),  # 逐行注释：赋值或更新当前变量/字段。
    }  # 逐行注释：结束当前数据结构或调用块。
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")  # 逐行注释：返回当前逻辑的处理结果。


def login_required(fn):  # 逐行注释：声明函数或方法入口。
    """从 ``Authorization: Bearer <token>`` 头解析 JWT 并注入 ``g.current_user``。"""

    @wraps(fn)  # 逐行注释：应用装饰器配置路由、权限或命令。
    def wrapper(*args, **kwargs):  # 逐行注释：声明函数或方法入口。
        """包裹被装饰的视图函数并执行权限校验。"""
        auth_header = request.headers.get("Authorization", "")  # 逐行注释：赋值或更新当前变量/字段。
        if not auth_header.startswith("Bearer "):  # 逐行注释：根据条件判断是否进入该分支。
            return jsonify(code=401, message="未登录，请先登录"), 401  # 逐行注释：返回当前逻辑的处理结果。

        token = auth_header[7:]  # 逐行注释：赋值或更新当前变量/字段。
        try:  # 逐行注释：开始执行可能出现异常的逻辑。
            payload = jwt.decode(  # 逐行注释：赋值或更新当前变量/字段。
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]  # 逐行注释：赋值或更新当前变量/字段。
            )  # 逐行注释：结束当前数据结构或调用块。
        except jwt.ExpiredSignatureError:  # 逐行注释：捕获异常并执行错误处理。
            return jsonify(code=401, message="登录已过期，请重新登录"), 401  # 逐行注释：返回当前逻辑的处理结果。
        except jwt.InvalidTokenError:  # 逐行注释：捕获异常并执行错误处理。
            return jsonify(code=401, message="无效的登录凭证，请重新登录"), 401  # 逐行注释：返回当前逻辑的处理结果。

        user = db.session.get(User, payload["user_id"])  # 逐行注释：赋值或更新当前变量/字段。
        if user is None:  # 逐行注释：根据条件判断是否进入该分支。
            return jsonify(code=401, message="用户不存在"), 401  # 逐行注释：返回当前逻辑的处理结果。

        g.current_user = user  # 逐行注释：赋值或更新当前变量/字段。
        return fn(*args, **kwargs)  # 逐行注释：返回当前逻辑的处理结果。

    return wrapper  # 逐行注释：返回当前逻辑的处理结果。


def admin_required(fn):  # 逐行注释：声明函数或方法入口。
    """先校验登录态，再校验当前用户是否拥有 ``admin`` 角色。"""

    @wraps(fn)  # 逐行注释：应用装饰器配置路由、权限或命令。
    @login_required  # 逐行注释：应用装饰器配置路由、权限或命令。
    def wrapper(*args, **kwargs):  # 逐行注释：声明函数或方法入口。
        """包裹被装饰的视图函数并执行权限校验。"""
        if g.current_user.role != "admin":  # 逐行注释：根据条件判断是否进入该分支。
            return jsonify(code=403, message="需要管理员权限"), 403  # 逐行注释：返回当前逻辑的处理结果。
        return fn(*args, **kwargs)  # 逐行注释：返回当前逻辑的处理结果。

    return wrapper  # 逐行注释：返回当前逻辑的处理结果。
