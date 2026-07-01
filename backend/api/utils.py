"""Small request/response helpers shared across API blueprints."""  # 保留字符串内容，作为说明文本或页面展示文案。
from flask import jsonify, request  # 从 flask 导入 jsonify, request，供本文件后续逻辑调用。


def ok(data=None, message: str = "ok"):  # 定义 ok 函数，集中处理这一段业务逻辑。
    """Wrap a successful payload in the standard response envelope."""  # 保留字符串内容，作为说明文本或页面展示文案。
    return jsonify({"code": 0, "message": message, "data": data})  # 返回处理后的结果给调用方继续使用。


def get_int(name: str, default=None):  # 定义 get_int 函数，集中处理这一段业务逻辑。
    """从请求参数中读取整数值，失败时返回默认值。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    val = request.args.get(name)  # 设置 val 的值，供后续业务判断、查询或响应组装使用。
    if val in (None, ""):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return default  # 返回处理后的结果给调用方继续使用。
    try:  # 开始执行可能抛出异常的代码块。
        return int(val)  # 返回处理后的结果给调用方继续使用。
    except (TypeError, ValueError):  # 捕获指定异常，并转入可控的错误处理流程。
        return default  # 返回处理后的结果给调用方继续使用。


def get_float(name: str, default=None):  # 定义 get_float 函数，集中处理这一段业务逻辑。
    """从请求参数中读取浮点值，失败时返回默认值。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    val = request.args.get(name)  # 设置 val 的值，供后续业务判断、查询或响应组装使用。
    if val in (None, ""):  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return default  # 返回处理后的结果给调用方继续使用。
    try:  # 开始执行可能抛出异常的代码块。
        return float(val)  # 返回处理后的结果给调用方继续使用。
    except (TypeError, ValueError):  # 捕获指定异常，并转入可控的错误处理流程。
        return default  # 返回处理后的结果给调用方继续使用。
