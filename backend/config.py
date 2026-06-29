"""Application configuration.

Reads settings from environment variables (optionally loaded from a local
``.env`` file). Falls back to sensible development defaults so the project
runs out of the box.
"""
import os  # 逐行注释：导入本行所需的模块或对象。
from pathlib import Path  # 逐行注释：导入本行所需的模块或对象。

from dotenv import load_dotenv  # 逐行注释：导入本行所需的模块或对象。

BASE_DIR = Path(__file__).resolve().parent  # 逐行注释：赋值或更新当前变量/字段。

# Load .env if present (does nothing in production where real env vars are set)
load_dotenv(BASE_DIR / ".env")  # 逐行注释：执行本行代码逻辑。


def _database_url() -> str:  # 逐行注释：声明函数或方法入口。
    """Return the configured DB URL, or a SQLite fallback for zero-config runs."""
    url = os.getenv("DATABASE_URL", "").strip()  # 逐行注释：赋值或更新当前变量/字段。
    if url:  # 逐行注释：根据条件判断是否进入该分支。
        return url  # 逐行注释：返回当前逻辑的处理结果。
    # Fallback: local SQLite file so the app is runnable without a DB server.
    return f"sqlite:///{BASE_DIR / 'housing.db'}"  # 逐行注释：返回当前逻辑的处理结果。


class Config:  # 逐行注释：声明类并定义相关数据或行为。
    """集中保存 Flask、数据库、跨域和运行端口等应用配置。"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")  # 逐行注释：赋值或更新当前变量/字段。

    SQLALCHEMY_DATABASE_URI = _database_url()  # 逐行注释：赋值或更新当前变量/字段。
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 逐行注释：赋值或更新当前变量/字段。
    # Recycle connections so MySQL doesn't drop idle ones ("server has gone away").
    SQLALCHEMY_ENGINE_OPTIONS = {  # 逐行注释：赋值或更新当前变量/字段。
        "pool_pre_ping": True,  # 逐行注释：设置当前数据项或参数。
        "pool_recycle": 280,  # 逐行注释：设置当前数据项或参数。
    }  # 逐行注释：结束当前数据结构或调用块。

    # JSON: keep non-ASCII (Chinese) characters readable in responses.
    JSON_AS_ASCII = False  # 逐行注释：赋值或更新当前变量/字段。

    CORS_ORIGINS = [  # 逐行注释：赋值或更新当前变量/字段。
        o.strip()  # 逐行注释：执行本行代码逻辑。
        for o in os.getenv(  # 逐行注释：遍历集合中的每一项并执行处理。
            "CORS_ORIGINS",  # 逐行注释：设置当前数据项或参数。
            "http://localhost:5173,http://127.0.0.1:5173",  # 逐行注释：设置当前数据项或参数。
        ).split(",")  # 逐行注释：执行本行代码逻辑。
        if o.strip()  # 逐行注释：根据条件判断是否进入该分支。
    ]  # 逐行注释：结束当前数据结构或调用块。

    HOST = os.getenv("HOST", "127.0.0.1")  # 逐行注释：赋值或更新当前变量/字段。
    PORT = int(os.getenv("PORT", "5000"))  # 逐行注释：赋值或更新当前变量/字段。
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"  # 逐行注释：执行本行代码逻辑。
