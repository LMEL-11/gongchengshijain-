"""Flask application factory for the Smart Property Exploration Platform.

智慧房源探索平台 —— 后端入口（应用工厂）。
"""
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    # --- Extensions ---
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # --- Models must be imported before create_all so tables are registered ---
    from models import register_models  # noqa: WPS433 (local import avoids cycle)

    register_models()

    # --- Blueprints ---
    from api import register_blueprints

    register_blueprints(app)

    # --- Create tables on first run (safe: only creates what's missing) ---
    with app.app_context():
        db.create_all()

    _register_error_handlers(app)
    _register_cli(app)
    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_err):
        return jsonify(code=404, message="资源不存在 (Not Found)"), 404

    @app.errorhandler(400)
    def bad_request(err):
        return jsonify(code=400, message=str(getattr(err, "description", "Bad Request"))), 400

    @app.errorhandler(500)
    def server_error(_err):
        return jsonify(code=500, message="服务器内部错误 (Internal Server Error)"), 500


def _register_cli(app: Flask) -> None:
    """Register `flask seed` so sample data can be loaded from the CLI."""

    @app.cli.command("seed")
    def seed_command():  # pragma: no cover - thin CLI wrapper
        """Populate the database with realistic sample housing data."""
        from seed import run_seed

        run_seed(app)

    @app.cli.command("seed-users")
    def seed_users_command():
        """Create default admin/user accounts."""
        from seed_users import run_seed_users

        run_seed_users(app)


# Allow `flask --app app run` and `python run.py`
app = create_app()


if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
