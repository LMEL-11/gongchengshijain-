"""Application configuration.

Reads settings from environment variables (optionally loaded from a local
``.env`` file). Falls back to sensible development defaults so the project
runs out of the box.
"""
import os  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from pathlib import Path  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from dotenv import load_dotenv  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

BASE_DIR = Path(__file__).resolve().parent  # 计算或更新BASE_DIR中间数据，作为后续业务判断、统计或响应组装的输入。

# Load .env if present (does nothing in production where real env vars are set)
load_dotenv(BASE_DIR / ".env")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。


def _database_url() -> str:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Return the configured DB URL, or a SQLite fallback for zero-config runs."""
    url = os.getenv("DATABASE_URL", "").strip()  # 计算或更新url中间数据，作为后续业务判断、统计或响应组装的输入。
    if url:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return url  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    # Fallback: local SQLite file so the app is runnable without a DB server.
    return f"sqlite:///{BASE_DIR / 'housing.db'}"  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


class Config:  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """集中保存 Flask、数据库、跨域和运行端口等应用配置。"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")  # 计算或更新SECRET_KEY中间数据，作为后续业务判断、统计或响应组装的输入。

    SQLALCHEMY_DATABASE_URI = _database_url()  # 计算或更新SQLALCHEMY_DATABASE_URI中间数据，作为后续业务判断、统计或响应组装的输入。
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 计算或更新SQLALCHEMY_TRACK_MODIFICATIONS中间数据，作为后续业务判断、统计或响应组装的输入。
    # Recycle connections so MySQL doesn't drop idle ones ("server has gone away").
    SQLALCHEMY_ENGINE_OPTIONS = {  # 初始化SQLALCHEMY_ENGINE_OPTIONS中间数据字典，用于承载接口返回或中间聚合结果。
        "pool_pre_ping": True,  # 把pool_pre_ping字段写入响应数据，供前端页面、图表或后续接口读取。
        "pool_recycle": 280,  # 把pool_recycle字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    # JSON: keep non-ASCII (Chinese) characters readable in responses.
    JSON_AS_ASCII = False  # 计算或更新JSON_AS_ASCII中间数据，作为后续业务判断、统计或响应组装的输入。

    CORS_ORIGINS = [  # 初始化CORS_ORIGINS中间数据列表，用于收集清洗后的多条业务数据。
        o.strip()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        for o in os.getenv(  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            "CORS_ORIGINS",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            "http://localhost:5173,http://127.0.0.1:5173",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        ).split(",")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        if o.strip()  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    HOST = os.getenv("HOST", "127.0.0.1")  # 计算或更新HOST中间数据，作为后续业务判断、统计或响应组装的输入。
    PORT = int(os.getenv("PORT", "5000"))  # 计算或更新PORT中间数据，作为后续业务判断、统计或响应组装的输入。
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"  # 计算或更新DEBUG中间数据，作为后续业务判断、统计或响应组装的输入。
