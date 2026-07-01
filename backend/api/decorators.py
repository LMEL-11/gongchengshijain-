"""认证/授权装饰器。

基于 JWT Bearer Token 的 ``@login_required`` 和 ``@admin_required``。
"""
from functools import wraps  # 从 functools 导入 wraps，供本文件后续逻辑调用。
from datetime import datetime, timedelta, timezone  # 从 datetime 导入 datetime, timedelta, timezone，供本文件后续逻辑调用。

import jwt  # 导入 jwt 模块，为当前文件提供所需功能。
from flask import current_app, g, jsonify, request  # 从 flask 导入 current_app, g, jsonify, request，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models.user import User  # 从 models.user 导入 User，供本文件后续逻辑调用。


def _create_token(user_id: int, role: str) -> str:  # 定义 _create_token 函数，集中处理这一段业务逻辑。
    """签发 JWT 令牌，默认 24 小时过期。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    payload = {  # 设置 payload 的值，供后续业务判断、查询或响应组装使用。
        "user_id": user_id,  # 保留字符串内容，作为说明文本或页面展示文案。
        "role": role,  # 保留字符串内容，作为说明文本或页面展示文案。
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),  # 设置 "exp": datetime.now(timezone.utc) + timedelta(hours 的值，供后续业务判断、查询或响应组装使用。
    }  # 结束当前多行数据结构或函数调用。
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")  # 返回处理后的结果给调用方继续使用。


def login_required(fn):  # 定义 login_required 函数，集中处理这一段业务逻辑。
    """从 ``Authorization: Bearer <token>`` 头解析 JWT 并注入 ``g.current_user``。"""  # 保留字符串内容，作为说明文本或页面展示文案。

    @wraps(fn)  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    def wrapper(*args, **kwargs):  # 定义 wrapper 函数，集中处理这一段业务逻辑。
        """包裹被装饰的视图函数并执行权限校验。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        auth_header = request.headers.get("Authorization", "")  # 设置 auth_header 的值，供后续业务判断、查询或响应组装使用。
        if not auth_header.startswith("Bearer "):  # 判断当前条件是否成立，决定是否进入对应处理分支。
            return jsonify(code=401, message="未登录，请先登录"), 401  # 返回处理后的结果给调用方继续使用。

        token = auth_header[7:]  # 设置 token 的值，供后续业务判断、查询或响应组装使用。
        try:  # 开始执行可能抛出异常的代码块。
            payload = jwt.decode(  # 设置 payload 的值，供后续业务判断、查询或响应组装使用。
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]  # 设置 token, current_app.config["SECRET_KEY"], algorithms 的值，供后续业务判断、查询或响应组装使用。
            )  # 结束当前多行数据结构或函数调用。
        except jwt.ExpiredSignatureError:  # 捕获指定异常，并转入可控的错误处理流程。
            return jsonify(code=401, message="登录已过期，请重新登录"), 401  # 返回处理后的结果给调用方继续使用。
        except jwt.InvalidTokenError:  # 捕获指定异常，并转入可控的错误处理流程。
            return jsonify(code=401, message="无效的登录凭证，请重新登录"), 401  # 返回处理后的结果给调用方继续使用。

        user = db.session.get(User, payload["user_id"])  # 设置 user 的值，供后续业务判断、查询或响应组装使用。
        if user is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            return jsonify(code=401, message="用户不存在"), 401  # 返回处理后的结果给调用方继续使用。

        g.current_user = user  # 设置 g.current_user 的值，供后续业务判断、查询或响应组装使用。
        return fn(*args, **kwargs)  # 返回处理后的结果给调用方继续使用。

    return wrapper  # 返回处理后的结果给调用方继续使用。


def admin_required(fn):  # 定义 admin_required 函数，集中处理这一段业务逻辑。
    """先校验登录态，再校验当前用户是否拥有 ``admin`` 角色。"""  # 保留字符串内容，作为说明文本或页面展示文案。

    @wraps(fn)  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    @login_required  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    def wrapper(*args, **kwargs):  # 定义 wrapper 函数，集中处理这一段业务逻辑。
        """包裹被装饰的视图函数并执行权限校验。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        if g.current_user.role != "admin":  # 判断当前条件是否成立，决定是否进入对应处理分支。
            return jsonify(code=403, message="需要管理员权限"), 403  # 返回处理后的结果给调用方继续使用。
        return fn(*args, **kwargs)  # 返回处理后的结果给调用方继续使用。

    return wrapper  # 返回处理后的结果给调用方继续使用。
