"""SQLAlchemy models for the housing platform.

Import order matters only in that every model module must be imported before
``db.create_all()`` runs — :func:`register_models` guarantees that.
"""
from extensions import db  # 导入本行所需的模块或对象。

from .city import City  # 导入本行所需的模块或对象。
from .district import District  # 导入本行所需的模块或对象。
from .facility import Facility  # 导入本行所需的模块或对象。
from .price_history import PriceHistory  # 导入本行所需的模块或对象。
from .property import Property  # 导入本行所需的模块或对象。
from .property_transaction import PropertyTransaction  # 导入本行所需的模块或对象。
from .user import User  # 导入本行所需的模块或对象。

__all__ = [  # 赋值或更新当前变量/字段。
    "db",  # 设置当前数据项或参数。
    "City",  # 设置当前数据项或参数。
    "District",  # 设置当前数据项或参数。
    "Property",  # 设置当前数据项或参数。
    "PropertyTransaction",  # 设置当前数据项或参数。
    "User",  # 设置当前数据项或参数。
    "Facility",  # 设置当前数据项或参数。
    "PriceHistory",  # 设置当前数据项或参数。
    "register_models",  # 设置当前数据项或参数。
]  # 结束当前数据结构或调用块。


def register_models() -> None:  # 声明函数或方法入口。
    """No-op hook: importing this package already registered every table.

    Kept as an explicit call site in the app factory for readability.
    """
    return None  # 返回当前逻辑的处理结果。
