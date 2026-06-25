"""API package: registers all blueprints onto the Flask app."""
from flask import Flask


def register_blueprints(app: Flask) -> None:
    from .cities import bp as cities_bp
    from .districts import bp as districts_bp
    from .facilities import bp as facilities_bp
    from .national import bp as national_bp
    from .properties import bp as properties_bp
    from .stats import bp as stats_bp
    from .auth import bp as auth_bp
    from .admin import bp as admin_bp

    for bp in (cities_bp, districts_bp, properties_bp, stats_bp, facilities_bp, national_bp, auth_bp, admin_bp):
        app.register_blueprint(bp)

    @app.get("/api/health")
    def health():
        return {"code": 0, "status": "ok", "service": "housing-platform"}
