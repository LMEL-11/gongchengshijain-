"""Flask application factory for the Smart Property Exploration Platform.

智慧房源探索平台 —— 后端入口（应用工厂）。
"""
from flask import Flask, jsonify  # 从 flask 导入 Flask, jsonify，供本文件后续逻辑调用。
from flask_cors import CORS  # 从 flask_cors 导入 CORS，供本文件后续逻辑调用。

from config import Config  # 从 config 导入 Config，供本文件后续逻辑调用。
from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。


def create_app(config_object: type = Config) -> Flask:  # 定义 create_app 函数，集中处理这一段业务逻辑。
    """创建并配置 Flask 应用，初始化扩展、蓝图、数据表和 CLI。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    app = Flask(__name__)  # 设置 app 的值，供后续业务判断、查询或响应组装使用。
    app.config.from_object(config_object)  # 执行当前代码行对应的业务处理步骤。

    # --- Extensions ---
    db.init_app(app)  # 执行当前代码行对应的业务处理步骤。
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})  # 设置 CORS(app, resources 的值，供后续业务判断、查询或响应组装使用。

    # --- Models must be imported before create_all so tables are registered ---
    from models import register_models  # noqa: WPS433 (local import avoids cycle)

    register_models()  # 执行当前代码行对应的业务处理步骤。

    # --- Blueprints ---
    from api import register_blueprints  # 从 api 导入 register_blueprints，供本文件后续逻辑调用。

    register_blueprints(app)  # 执行当前代码行对应的业务处理步骤。

    # --- Create tables on first run (safe: only creates what's missing) ---
    with app.app_context():  # 进入上下文管理流程，自动处理资源打开和释放。
        db.create_all()  # 执行当前代码行对应的业务处理步骤。

    _register_error_handlers(app)  # 执行当前代码行对应的业务处理步骤。
    _register_cli(app)  # 执行当前代码行对应的业务处理步骤。
    return app  # 返回处理后的结果给调用方继续使用。


def _register_error_handlers(app: Flask) -> None:  # 定义 _register_error_handlers 函数，集中处理这一段业务逻辑。
    """注册统一的 400、404 和 500 错误响应处理器。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    @app.errorhandler(404)  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    def not_found(_err):  # 定义 not_found 函数，集中处理这一段业务逻辑。
        """将 404 错误转换为统一 JSON 响应。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return jsonify(code=404, message="资源不存在 (Not Found)"), 404  # 返回处理后的结果给调用方继续使用。

    @app.errorhandler(400)  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    def bad_request(err):  # 定义 bad_request 函数，集中处理这一段业务逻辑。
        """将 400 错误转换为统一 JSON 响应。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return jsonify(code=400, message=str(getattr(err, "description", "Bad Request"))), 400  # 返回处理后的结果给调用方继续使用。

    @app.errorhandler(500)  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    def server_error(_err):  # 定义 server_error 函数，集中处理这一段业务逻辑。
        """将 500 错误转换为统一 JSON 响应。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return jsonify(code=500, message="服务器内部错误 (Internal Server Error)"), 500  # 返回处理后的结果给调用方继续使用。


def _register_cli(app: Flask) -> None:  # 定义 _register_cli 函数，集中处理这一段业务逻辑。
    """Register `flask seed` so sample data can be loaded from the CLI."""  # 保留字符串内容，作为说明文本或页面展示文案。

    @app.cli.command("seed")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    def seed_command():  # pragma: no cover - thin CLI wrapper
        """Populate the database with realistic sample housing data."""  # 保留字符串内容，作为说明文本或页面展示文案。
        from seed import run_seed  # 从 seed 导入 run_seed，供本文件后续逻辑调用。

        run_seed(app)  # 执行当前代码行对应的业务处理步骤。

    @app.cli.command("seed-users")  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    def seed_users_command():  # 定义 seed_users_command 函数，集中处理这一段业务逻辑。
        """Create default admin/user accounts."""  # 保留字符串内容，作为说明文本或页面展示文案。
        from seed_users import run_seed_users  # 从 seed_users 导入 run_seed_users，供本文件后续逻辑调用。

        run_seed_users(app)  # 执行当前代码行对应的业务处理步骤。


# Allow `flask --app app run` and `python run.py`
app = create_app()  # 设置 app 的值，供后续业务判断、查询或响应组装使用。


if __name__ == "__main__":  # 判断当前条件是否成立，决定是否进入对应处理分支。
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])  # 设置 app.run(host 的值，供后续业务判断、查询或响应组装使用。
