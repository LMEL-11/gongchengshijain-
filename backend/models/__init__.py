"""SQLAlchemy models for the housing platform.

Import order matters only in that every model module must be imported before
``db.create_all()`` runs — :func:`register_models` guarantees that.
"""
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from .city import City  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from .district import District  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from .facility import Facility  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from .price_history import PriceHistory  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from .property import Property  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from .property_transaction import PropertyTransaction  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from .user import User  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

__all__ = [  # 初始化__all__中间数据列表，用于收集清洗后的多条业务数据。
    "db",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "City",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "District",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "Property",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "PropertyTransaction",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "User",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "Facility",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "PriceHistory",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "register_models",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def register_models() -> None:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """No-op hook: importing this package already registered every table.

    Kept as an explicit call site in the app factory for readability.
    """
    return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
