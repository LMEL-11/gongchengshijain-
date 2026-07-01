"""Application configuration.

Reads settings from environment variables (optionally loaded from a local
``.env`` file). Falls back to sensible development defaults so the project
runs out of the box.
"""
import os  # 导入 os 模块，为当前文件提供所需功能。
from pathlib import Path  # 从 pathlib 导入 Path，供本文件后续逻辑调用。

from dotenv import load_dotenv  # 从 dotenv 导入 load_dotenv，供本文件后续逻辑调用。

BASE_DIR = Path(__file__).resolve().parent  # 设置 BASE_DIR 的值，供后续业务判断、查询或响应组装使用。

# Load .env if present (does nothing in production where real env vars are set)
load_dotenv(BASE_DIR / ".env")  # 执行当前代码行对应的业务处理步骤。


def _database_url() -> str:  # 定义 _database_url 函数，集中处理这一段业务逻辑。
    """Return the configured DB URL, or a SQLite fallback for zero-config runs."""  # 保留字符串内容，作为说明文本或页面展示文案。
    url = os.getenv("DATABASE_URL", "").strip()  # 设置 url 的值，供后续业务判断、查询或响应组装使用。
    if url:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return url  # 返回处理后的结果给调用方继续使用。
    # Fallback: local SQLite file so the app is runnable without a DB server.
    return f"sqlite:///{BASE_DIR / 'housing.db'}"  # 返回处理后的结果给调用方继续使用。


class Config:  # 定义 Config 类，封装对应的数据结构或业务行为。
    """集中保存 Flask、数据库、跨域和运行端口等应用配置。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")  # 设置 SECRET_KEY 的值，供后续业务判断、查询或响应组装使用。

    SQLALCHEMY_DATABASE_URI = _database_url()  # 设置 SQLALCHEMY_DATABASE_URI 的值，供后续业务判断、查询或响应组装使用。
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 设置 SQLALCHEMY_TRACK_MODIFICATIONS 的值，供后续业务判断、查询或响应组装使用。
    # Recycle connections so MySQL doesn't drop idle ones ("server has gone away").
    SQLALCHEMY_ENGINE_OPTIONS = {  # 设置 SQLALCHEMY_ENGINE_OPTIONS 的值，供后续业务判断、查询或响应组装使用。
        "pool_pre_ping": True,  # 保留字符串内容，作为说明文本或页面展示文案。
        "pool_recycle": 280,  # 保留字符串内容，作为说明文本或页面展示文案。
    }  # 结束当前多行数据结构或函数调用。

    # JSON: keep non-ASCII (Chinese) characters readable in responses.
    JSON_AS_ASCII = False  # 设置 JSON_AS_ASCII 的值，供后续业务判断、查询或响应组装使用。

    CORS_ORIGINS = [  # 设置 CORS_ORIGINS 的值，供后续业务判断、查询或响应组装使用。
        o.strip()  # 执行当前代码行对应的业务处理步骤。
        for o in os.getenv(  # 遍历当前数据集合，逐项完成处理。
            "CORS_ORIGINS",  # 保留字符串内容，作为说明文本或页面展示文案。
            "http://localhost:5173,http://127.0.0.1:5173",  # 保留字符串内容，作为说明文本或页面展示文案。
        ).split(",")  # 执行当前代码行对应的业务处理步骤。
        if o.strip()  # 判断当前条件是否成立，决定是否进入对应处理分支。
    ]  # 结束当前多行数据结构或函数调用。

    HOST = os.getenv("HOST", "127.0.0.1")  # 设置 HOST 的值，供后续业务判断、查询或响应组装使用。
    PORT = int(os.getenv("PORT", "5000"))  # 设置 PORT 的值，供后续业务判断、查询或响应组装使用。
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"  # 执行当前代码行对应的业务处理步骤。
