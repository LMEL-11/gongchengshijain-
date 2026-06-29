"""API package: registers all blueprints onto the Flask app."""
from flask import Flask  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


def register_blueprints(app: Flask) -> None:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """集中注册所有 API 蓝图并挂载健康检查接口。"""
    from .cities import bp as cities_bp  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
    from .districts import bp as districts_bp  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
    from .facilities import bp as facilities_bp  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
    from .national import bp as national_bp  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
    from .properties import bp as properties_bp  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
    from .stats import bp as stats_bp  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
    from .auth import bp as auth_bp  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
    from .admin import bp as admin_bp  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

    for bp in (cities_bp, districts_bp, properties_bp, stats_bp, facilities_bp, national_bp, auth_bp, admin_bp):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        app.register_blueprint(bp)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    @app.get("/api/health")  # 把下方函数注册为路由、权限校验或框架回调入口。
    def health():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """返回后端健康检查结果。"""
        return {"code": 0, "status": "ok", "service": "housing-platform"}  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
