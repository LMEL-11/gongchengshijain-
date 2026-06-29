"""Flask application factory for the Smart Property Exploration Platform.

智慧房源探索平台 —— 后端入口（应用工厂）。
"""
from flask import Flask, jsonify  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from flask_cors import CORS  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from config import Config  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


def create_app(config_object: type = Config) -> Flask:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """创建并配置 Flask 应用，初始化扩展、蓝图、数据表和 CLI。"""
    app = Flask(__name__)  # 计算或更新app中间数据，作为后续业务判断、统计或响应组装的输入。
    app.config.from_object(config_object)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    # --- Extensions ---
    db.init_app(app)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    # --- Models must be imported before create_all so tables are registered ---
    from models import register_models  # noqa: WPS433 (local import avoids cycle)

    register_models()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    # --- Blueprints ---
    from api import register_blueprints  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

    register_blueprints(app)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    # --- Create tables on first run (safe: only creates what's missing) ---
    with app.app_context():  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
        db.create_all()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    _register_error_handlers(app)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    _register_cli(app)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return app  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _register_error_handlers(app: Flask) -> None:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """注册统一的 400、404 和 500 错误响应处理器。"""
    @app.errorhandler(404)  # 把下方函数注册为路由、权限校验或框架回调入口。
    def not_found(_err):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将 404 错误转换为统一 JSON 响应。"""
        return jsonify(code=404, message="资源不存在 (Not Found)"), 404  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    @app.errorhandler(400)  # 把下方函数注册为路由、权限校验或框架回调入口。
    def bad_request(err):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将 400 错误转换为统一 JSON 响应。"""
        return jsonify(code=400, message=str(getattr(err, "description", "Bad Request"))), 400  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    @app.errorhandler(500)  # 把下方函数注册为路由、权限校验或框架回调入口。
    def server_error(_err):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将 500 错误转换为统一 JSON 响应。"""
        return jsonify(code=500, message="服务器内部错误 (Internal Server Error)"), 500  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _register_cli(app: Flask) -> None:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Register `flask seed` so sample data can be loaded from the CLI."""

    @app.cli.command("seed")  # 把下方函数注册为路由、权限校验或框架回调入口。
    def seed_command():  # pragma: no cover - thin CLI wrapper
        """Populate the database with realistic sample housing data."""
        from seed import run_seed  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

        run_seed(app)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    @app.cli.command("seed-users")  # 把下方函数注册为路由、权限校验或框架回调入口。
    def seed_users_command():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """Create default admin/user accounts."""
        from seed_users import run_seed_users  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

        run_seed_users(app)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。


# Allow `flask --app app run` and `python run.py`
app = create_app()  # 计算或更新app中间数据，作为后续业务判断、统计或响应组装的输入。


if __name__ == "__main__":  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
