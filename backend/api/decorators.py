"""认证/授权装饰器。

基于 JWT Bearer Token 的 ``@login_required`` 和 ``@admin_required``。
"""
from functools import wraps  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from datetime import datetime, timedelta, timezone  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

import jwt  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from flask import current_app, g, jsonify, request  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models.user import User  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


def _create_token(user_id: int, role: str) -> str:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """签发 JWT 令牌，默认 24 小时过期。"""
    payload = {  # 初始化请求或入库载荷字典，用于承载接口返回或中间聚合结果。
        "user_id": user_id,  # 把user_id字段写入响应数据，供前端页面、图表或后续接口读取。
        "role": role,  # 把role字段写入响应数据，供前端页面、图表或后续接口读取。
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),  # 把exp字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def login_required(fn):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从 ``Authorization: Bearer <token>`` 头解析 JWT 并注入 ``g.current_user``。"""

    @wraps(fn)  # 把下方函数注册为路由、权限校验或框架回调入口。
    def wrapper(*args, **kwargs):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """包裹被装饰的视图函数并执行权限校验。"""
        auth_header = request.headers.get("Authorization", "")  # 从请求或外部输入提取auth_header中间数据，用于后续校验、查询或写入。
        if not auth_header.startswith("Bearer "):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            return jsonify(code=401, message="未登录，请先登录"), 401  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

        token = auth_header[7:]  # 计算或更新token中间数据，作为后续业务判断、统计或响应组装的输入。
        try:  # 开始执行可能失败的外部访问、数据转换或数据库操作。
            payload = jwt.decode(  # 计算或更新请求或入库载荷，作为后续业务判断、统计或响应组装的输入。
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        except jwt.ExpiredSignatureError:  # 捕获异常并转换为可控的错误处理或提示信息。
            return jsonify(code=401, message="登录已过期，请重新登录"), 401  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        except jwt.InvalidTokenError:  # 捕获异常并转换为可控的错误处理或提示信息。
            return jsonify(code=401, message="无效的登录凭证，请重新登录"), 401  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

        user = db.session.get(User, payload["user_id"])  # 计算或更新user中间数据，作为后续业务判断、统计或响应组装的输入。
        if user is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            return jsonify(code=401, message="用户不存在"), 401  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

        g.current_user = user  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return fn(*args, **kwargs)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    return wrapper  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def admin_required(fn):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """先校验登录态，再校验当前用户是否拥有 ``admin`` 角色。"""

    @wraps(fn)  # 把下方函数注册为路由、权限校验或框架回调入口。
    @login_required  # 把下方函数注册为路由、权限校验或框架回调入口。
    def wrapper(*args, **kwargs):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """包裹被装饰的视图函数并执行权限校验。"""
        if g.current_user.role != "admin":  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            return jsonify(code=403, message="需要管理员权限"), 403  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        return fn(*args, **kwargs)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    return wrapper  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
