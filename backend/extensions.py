"""Shared Flask extensions, instantiated here to avoid circular imports."""
from flask_sqlalchemy import SQLAlchemy  # 导入本行所需的模块或对象。

db = SQLAlchemy()  # 赋值或更新当前变量/字段。
