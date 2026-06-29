"""Small request/response helpers shared across API blueprints."""
from flask import jsonify, request  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


def ok(data=None, message: str = "ok"):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Wrap a successful payload in the standard response envelope."""
    return jsonify({"code": 0, "message": message, "data": data})  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def get_int(name: str, default=None):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从请求参数中读取整数值，失败时返回默认值。"""
    val = request.args.get(name)  # 从请求或外部输入提取val中间数据，用于后续校验、查询或写入。
    if val in (None, ""):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return default  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    try:  # 开始执行可能失败的外部访问、数据转换或数据库操作。
        return int(val)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    except (TypeError, ValueError):  # 捕获异常并转换为可控的错误处理或提示信息。
        return default  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def get_float(name: str, default=None):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从请求参数中读取浮点值，失败时返回默认值。"""
    val = request.args.get(name)  # 从请求或外部输入提取val中间数据，用于后续校验、查询或写入。
    if val in (None, ""):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return default  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    try:  # 开始执行可能失败的外部访问、数据转换或数据库操作。
        return float(val)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    except (TypeError, ValueError):  # 捕获异常并转换为可控的错误处理或提示信息。
        return default  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
