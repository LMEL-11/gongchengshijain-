"""API package: registers all blueprints onto the Flask app."""  # 保留字符串内容，作为说明文本或页面展示文案。
from flask import Flask  # 从 flask 导入 Flask，供本文件后续逻辑调用。


def register_blueprints(app: Flask) -> None:  # 定义 register_blueprints 函数，集中处理这一段业务逻辑。
    """集中注册所有 API 蓝图并挂载健康检查接口。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    from .cities import bp as cities_bp  # 从 .cities 导入 bp as cities_bp，供本文件后续逻辑调用。
    from .districts import bp as districts_bp  # 从 .districts 导入 bp as districts_bp，供本文件后续逻辑调用。
    from .facilities import bp as facilities_bp  # 从 .facilities 导入 bp as facilities_bp，供本文件后续逻辑调用。
    from .national import bp as national_bp  # 从 .national 导入 bp as national_bp，供本文件后续逻辑调用。
    from .properties import bp as properties_bp  # 从 .properties 导入 bp as properties_bp，供本文件后续逻辑调用。
    from .stats import bp as stats_bp  # 从 .stats 导入 bp as stats_bp，供本文件后续逻辑调用。
    from .auth import bp as auth_bp  # 从 .auth 导入 bp as auth_bp，供本文件后续逻辑调用。
    from .admin import bp as admin_bp  # 从 .admin 导入 bp as admin_bp，供本文件后续逻辑调用。

    for bp in (cities_bp, districts_bp, properties_bp, stats_bp, facilities_bp, national_bp, auth_bp, admin_bp):  # 遍历当前数据集合，逐项完成处理。
        app.register_blueprint(bp)  # 执行当前代码行对应的业务处理步骤。

    @app.get("/api/health")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    def health():  # 定义 health 函数，集中处理这一段业务逻辑。
        """返回后端健康检查结果。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return {"code": 0, "status": "ok", "service": "housing-platform"}  # 返回处理后的结果给调用方继续使用。
