"""认证蓝图 —— 登录 / 获取当前用户 / 退出。"""  # 保留字符串内容，作为说明文本或页面展示文案。
from flask import Blueprint, g, jsonify, request  # 从 flask 导入 Blueprint, g, jsonify, request，供本文件后续逻辑调用。

from models.user import User  # 从 models.user 导入 User，供本文件后续逻辑调用。
from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from .decorators import _create_token, login_required  # 从 .decorators 导入 _create_token, login_required，供本文件后续逻辑调用。
from .utils import ok  # 从 .utils 导入 ok，供本文件后续逻辑调用。

bp = Blueprint("auth", __name__, url_prefix="/api/auth")  # 设置 bp 的值，供后续业务判断、查询或响应组装使用。


@bp.post("/login")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def login():  # 定义 login 函数，集中处理这一段业务逻辑。
    """处理登录请求，校验账号密码并返回登录令牌。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    body = request.get_json(silent=True) or {}  # 设置 body 的值，供后续业务判断、查询或响应组装使用。
    username = (body.get("username") or "").strip()  # 设置 username 的值，供后续业务判断、查询或响应组装使用。
    password = body.get("password") or ""  # 设置 password 的值，供后续业务判断、查询或响应组装使用。

    if not username or not password:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return jsonify(code=1, message="用户名和密码不能为空"), 400  # 返回处理后的结果给调用方继续使用。

    user = db.session.query(User).filter_by(username=username).first()  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    if user is None or not user.check_password(password):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return jsonify(code=1, message="用户名或密码错误"), 401  # 返回处理后的结果给调用方继续使用。

    token = _create_token(user.id, user.role)  # 设置 token 的值，供后续业务判断、查询或响应组装使用。
    return ok({"token": token, "user": user.to_dict()})  # 返回处理后的结果给调用方继续使用。


@bp.get("/me")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
@login_required  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def me():  # 定义 me 函数，集中处理这一段业务逻辑。
    """返回当前登录用户的信息。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return ok(g.current_user.to_dict())  # 返回处理后的结果给调用方继续使用。


@bp.post("/logout")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
@login_required  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def logout():  # 定义 logout 函数，集中处理这一段业务逻辑。
    """JWT 为无状态令牌；客户端丢弃 token 即完成退出。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return ok(None, message="已退出登录")  # 返回处理后的结果给调用方继续使用。
