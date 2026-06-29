"""Application configuration.

Reads settings from environment variables (optionally loaded from a local
``.env`` file). Falls back to sensible development defaults so the project
runs out of the box.
"""
import os  # 导入本行所需的模块或对象。
from pathlib import Path  # 导入本行所需的模块或对象。

from dotenv import load_dotenv  # 导入本行所需的模块或对象。

BASE_DIR = Path(__file__).resolve().parent  # 赋值或更新当前变量/字段。

# Load .env if present (does nothing in production where real env vars are set)
load_dotenv(BASE_DIR / ".env")  # 执行本行代码逻辑。


def _database_url() -> str:  # 声明函数或方法入口。
    """Return the configured DB URL, or a SQLite fallback for zero-config runs."""
    url = os.getenv("DATABASE_URL", "").strip()  # 赋值或更新当前变量/字段。
    if url:  # 根据条件判断是否进入该分支。
        return url  # 返回当前逻辑的处理结果。
    # Fallback: local SQLite file so the app is runnable without a DB server.
    return f"sqlite:///{BASE_DIR / 'housing.db'}"  # 返回当前逻辑的处理结果。


class Config:  # 声明类并定义相关数据或行为。
    """集中保存 Flask、数据库、跨域和运行端口等应用配置。"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")  # 赋值或更新当前变量/字段。

    SQLALCHEMY_DATABASE_URI = _database_url()  # 赋值或更新当前变量/字段。
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 赋值或更新当前变量/字段。
    # Recycle connections so MySQL doesn't drop idle ones ("server has gone away").
    SQLALCHEMY_ENGINE_OPTIONS = {  # 赋值或更新当前变量/字段。
        "pool_pre_ping": True,  # 设置当前数据项或参数。
        "pool_recycle": 280,  # 设置当前数据项或参数。
    }  # 结束当前数据结构或调用块。

    # JSON: keep non-ASCII (Chinese) characters readable in responses.
    JSON_AS_ASCII = False  # 赋值或更新当前变量/字段。

    CORS_ORIGINS = [  # 赋值或更新当前变量/字段。
        o.strip()  # 执行本行代码逻辑。
        for o in os.getenv(  # 遍历集合中的每一项并执行处理。
            "CORS_ORIGINS",  # 设置当前数据项或参数。
            "http://localhost:5173,http://127.0.0.1:5173",  # 设置当前数据项或参数。
        ).split(",")  # 执行本行代码逻辑。
        if o.strip()  # 根据条件判断是否进入该分支。
    ]  # 结束当前数据结构或调用块。

    HOST = os.getenv("HOST", "127.0.0.1")  # 赋值或更新当前变量/字段。
    PORT = int(os.getenv("PORT", "5000"))  # 赋值或更新当前变量/字段。
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"  # 执行本行代码逻辑。
