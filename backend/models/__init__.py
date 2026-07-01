"""SQLAlchemy models for the housing platform.

Import order matters only in that every model module must be imported before
``db.create_all()`` runs — :func:`register_models` guarantees that.
"""
from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。

from .city import City  # 从 .city 导入 City，供本文件后续逻辑调用。
from .district import District  # 从 .district 导入 District，供本文件后续逻辑调用。
from .facility import Facility  # 从 .facility 导入 Facility，供本文件后续逻辑调用。
from .price_history import PriceHistory  # 从 .price_history 导入 PriceHistory，供本文件后续逻辑调用。
from .property import Property  # 从 .property 导入 Property，供本文件后续逻辑调用。
from .property_transaction import PropertyTransaction  # 从 .property_transaction 导入 PropertyTransaction，供本文件后续逻辑调用。
from .user import User  # 从 .user 导入 User，供本文件后续逻辑调用。

__all__ = [  # 设置 __all__ 的值，供后续业务判断、查询或响应组装使用。
    "db",  # 保留字符串内容，作为说明文本或页面展示文案。
    "City",  # 保留字符串内容，作为说明文本或页面展示文案。
    "District",  # 保留字符串内容，作为说明文本或页面展示文案。
    "Property",  # 保留字符串内容，作为说明文本或页面展示文案。
    "PropertyTransaction",  # 保留字符串内容，作为说明文本或页面展示文案。
    "User",  # 保留字符串内容，作为说明文本或页面展示文案。
    "Facility",  # 保留字符串内容，作为说明文本或页面展示文案。
    "PriceHistory",  # 保留字符串内容，作为说明文本或页面展示文案。
    "register_models",  # 保留字符串内容，作为说明文本或页面展示文案。
]  # 结束当前多行数据结构或函数调用。


def register_models() -> None:  # 定义 register_models 函数，集中处理这一段业务逻辑。
    """No-op hook: importing this package already registered every table.

    Kept as an explicit call site in the app factory for readability.
    """
    return None  # 返回处理后的结果给调用方继续使用。
