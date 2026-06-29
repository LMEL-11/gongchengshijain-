"""认证蓝图 —— 登录 / 获取当前用户 / 退出。"""
from flask import Blueprint, g, jsonify, request  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from models.user import User  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from .decorators import _create_token, login_required  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from .utils import ok  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

bp = Blueprint("auth", __name__, url_prefix="/api/auth")  # 计算或更新bp中间数据，作为后续业务判断、统计或响应组装的输入。


@bp.post("/login")  # 把下方函数注册为路由、权限校验或框架回调入口。
def login():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """处理登录请求，校验账号密码并返回登录令牌。"""
    body = request.get_json(silent=True) or {}  # 从请求或外部输入提取前端提交的请求体，用于后续校验、查询或写入。
    username = (body.get("username") or "").strip()  # 计算或更新username中间数据，作为后续业务判断、统计或响应组装的输入。
    password = body.get("password") or ""  # 计算或更新password中间数据，作为后续业务判断、统计或响应组装的输入。

    if not username or not password:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return jsonify(code=1, message="用户名和密码不能为空"), 400  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    user = db.session.query(User).filter_by(username=username).first()  # 创建user中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
    if user is None or not user.check_password(password):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return jsonify(code=1, message="用户名或密码错误"), 401  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    token = _create_token(user.id, user.role)  # 计算或更新token中间数据，作为后续业务判断、统计或响应组装的输入。
    return ok({"token": token, "user": user.to_dict()})  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.get("/me")  # 把下方函数注册为路由、权限校验或框架回调入口。
@login_required  # 把下方函数注册为路由、权限校验或框架回调入口。
def me():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """返回当前登录用户的信息。"""
    return ok(g.current_user.to_dict())  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@bp.post("/logout")  # 把下方函数注册为路由、权限校验或框架回调入口。
@login_required  # 把下方函数注册为路由、权限校验或框架回调入口。
def logout():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """JWT 为无状态令牌；客户端丢弃 token 即完成退出。"""
    return ok(None, message="已退出登录")  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
