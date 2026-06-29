"""Development entry point: `python run.py` (equivalent to `flask --app app run`)."""
from app import app  # 导入本行所需的模块或对象。

if __name__ == "__main__":  # 根据条件判断是否进入该分支。
    app.run(  # 执行本行代码逻辑。
        host=app.config["HOST"],  # 赋值或更新当前变量/字段。
        port=app.config["PORT"],  # 赋值或更新当前变量/字段。
        debug=app.config["DEBUG"],  # 赋值或更新当前变量/字段。
    )  # 结束当前数据结构或调用块。
