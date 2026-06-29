"""API package: registers all blueprints onto the Flask app."""
from flask import Flask  # 逐行注释：导入本行所需的模块或对象。


def register_blueprints(app: Flask) -> None:  # 逐行注释：声明函数或方法入口。
    """集中注册所有 API 蓝图并挂载健康检查接口。"""
    from .cities import bp as cities_bp  # 逐行注释：导入本行所需的模块或对象。
    from .districts import bp as districts_bp  # 逐行注释：导入本行所需的模块或对象。
    from .facilities import bp as facilities_bp  # 逐行注释：导入本行所需的模块或对象。
    from .national import bp as national_bp  # 逐行注释：导入本行所需的模块或对象。
    from .properties import bp as properties_bp  # 逐行注释：导入本行所需的模块或对象。
    from .stats import bp as stats_bp  # 逐行注释：导入本行所需的模块或对象。
    from .auth import bp as auth_bp  # 逐行注释：导入本行所需的模块或对象。
    from .admin import bp as admin_bp  # 逐行注释：导入本行所需的模块或对象。

    for bp in (cities_bp, districts_bp, properties_bp, stats_bp, facilities_bp, national_bp, auth_bp, admin_bp):  # 逐行注释：遍历集合中的每一项并执行处理。
        app.register_blueprint(bp)  # 逐行注释：执行本行代码逻辑。

    @app.get("/api/health")  # 逐行注释：应用装饰器配置路由、权限或命令。
    def health():  # 逐行注释：声明函数或方法入口。
        """返回后端健康检查结果。"""
        return {"code": 0, "status": "ok", "service": "housing-platform"}  # 逐行注释：返回当前逻辑的处理结果。
