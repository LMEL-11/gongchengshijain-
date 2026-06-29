"""Application configuration.

Reads settings from environment variables (optionally loaded from a local
``.env`` file). Falls back to sensible development defaults so the project
runs out of the box.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load .env if present (does nothing in production where real env vars are set)
load_dotenv(BASE_DIR / ".env")


def _database_url() -> str:
    """Return the configured DB URL, or a SQLite fallback for zero-config runs."""
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return url
    # Fallback: local SQLite file so the app is runnable without a DB server.
    return f"sqlite:///{BASE_DIR / 'housing.db'}"


class Config:
    """集中保存 Flask、数据库、跨域和运行端口等应用配置。"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Recycle connections so MySQL doesn't drop idle ones ("server has gone away").
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # JSON: keep non-ASCII (Chinese) characters readable in responses.
    JSON_AS_ASCII = False

    CORS_ORIGINS = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if o.strip()
    ]

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
