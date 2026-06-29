"""Small request/response helpers shared across API blueprints."""
from flask import jsonify, request  # 逐行注释：导入本行所需的模块或对象。


def ok(data=None, message: str = "ok"):  # 逐行注释：声明函数或方法入口。
    """Wrap a successful payload in the standard response envelope."""
    return jsonify({"code": 0, "message": message, "data": data})  # 逐行注释：返回当前逻辑的处理结果。


def get_int(name: str, default=None):  # 逐行注释：声明函数或方法入口。
    """从请求参数中读取整数值，失败时返回默认值。"""
    val = request.args.get(name)  # 逐行注释：赋值或更新当前变量/字段。
    if val in (None, ""):  # 逐行注释：根据条件判断是否进入该分支。
        return default  # 逐行注释：返回当前逻辑的处理结果。
    try:  # 逐行注释：开始执行可能出现异常的逻辑。
        return int(val)  # 逐行注释：返回当前逻辑的处理结果。
    except (TypeError, ValueError):  # 逐行注释：捕获异常并执行错误处理。
        return default  # 逐行注释：返回当前逻辑的处理结果。


def get_float(name: str, default=None):  # 逐行注释：声明函数或方法入口。
    """从请求参数中读取浮点值，失败时返回默认值。"""
    val = request.args.get(name)  # 逐行注释：赋值或更新当前变量/字段。
    if val in (None, ""):  # 逐行注释：根据条件判断是否进入该分支。
        return default  # 逐行注释：返回当前逻辑的处理结果。
    try:  # 逐行注释：开始执行可能出现异常的逻辑。
        return float(val)  # 逐行注释：返回当前逻辑的处理结果。
    except (TypeError, ValueError):  # 逐行注释：捕获异常并执行错误处理。
        return default  # 逐行注释：返回当前逻辑的处理结果。
