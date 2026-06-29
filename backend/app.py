"""Flask application factory for the Smart Property Exploration Platform.

智慧房源探索平台 —— 后端入口（应用工厂）。
"""
from flask import Flask, jsonify  # 导入本行所需的模块或对象。
from flask_cors import CORS  # 导入本行所需的模块或对象。

from config import Config  # 导入本行所需的模块或对象。
from extensions import db  # 导入本行所需的模块或对象。


def create_app(config_object: type = Config) -> Flask:  # 声明函数或方法入口。
    """创建并配置 Flask 应用，初始化扩展、蓝图、数据表和 CLI。"""
    app = Flask(__name__)  # 赋值或更新当前变量/字段。
    app.config.from_object(config_object)  # 执行本行代码逻辑。

    # --- Extensions ---
    db.init_app(app)  # 执行本行代码逻辑。
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})  # 赋值或更新当前变量/字段。

    # --- Models must be imported before create_all so tables are registered ---
    from models import register_models  # noqa: WPS433 (local import avoids cycle)

    register_models()  # 执行本行代码逻辑。

    # --- Blueprints ---
    from api import register_blueprints  # 导入本行所需的模块或对象。

    register_blueprints(app)  # 执行本行代码逻辑。

    # --- Create tables on first run (safe: only creates what's missing) ---
    with app.app_context():  # 进入上下文管理器并自动处理资源。
        db.create_all()  # 执行本行代码逻辑。

    _register_error_handlers(app)  # 执行本行代码逻辑。
    _register_cli(app)  # 执行本行代码逻辑。
    return app  # 返回当前逻辑的处理结果。


def _register_error_handlers(app: Flask) -> None:  # 声明函数或方法入口。
    """注册统一的 400、404 和 500 错误响应处理器。"""
    @app.errorhandler(404)  # 应用装饰器配置路由、权限或命令。
    def not_found(_err):  # 声明函数或方法入口。
        """将 404 错误转换为统一 JSON 响应。"""
        return jsonify(code=404, message="资源不存在 (Not Found)"), 404  # 返回当前逻辑的处理结果。

    @app.errorhandler(400)  # 应用装饰器配置路由、权限或命令。
    def bad_request(err):  # 声明函数或方法入口。
        """将 400 错误转换为统一 JSON 响应。"""
        return jsonify(code=400, message=str(getattr(err, "description", "Bad Request"))), 400  # 返回当前逻辑的处理结果。

    @app.errorhandler(500)  # 应用装饰器配置路由、权限或命令。
    def server_error(_err):  # 声明函数或方法入口。
        """将 500 错误转换为统一 JSON 响应。"""
        return jsonify(code=500, message="服务器内部错误 (Internal Server Error)"), 500  # 返回当前逻辑的处理结果。


def _register_cli(app: Flask) -> None:  # 声明函数或方法入口。
    """Register `flask seed` so sample data can be loaded from the CLI."""

    @app.cli.command("seed")  # 应用装饰器配置路由、权限或命令。
    def seed_command():  # pragma: no cover - thin CLI wrapper
        """Populate the database with realistic sample housing data."""
        from seed import run_seed  # 导入本行所需的模块或对象。

        run_seed(app)  # 执行本行代码逻辑。

    @app.cli.command("seed-users")  # 应用装饰器配置路由、权限或命令。
    def seed_users_command():  # 声明函数或方法入口。
        """Create default admin/user accounts."""
        from seed_users import run_seed_users  # 导入本行所需的模块或对象。

        run_seed_users(app)  # 执行本行代码逻辑。


# Allow `flask --app app run` and `python run.py`
app = create_app()  # 赋值或更新当前变量/字段。


if __name__ == "__main__":  # 根据条件判断是否进入该分支。
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])  # 赋值或更新当前变量/字段。
