"""Shared Flask extensions, instantiated here to avoid circular imports."""  # 保留字符串内容，作为说明文本或页面展示文案。
from flask_sqlalchemy import SQLAlchemy  # 从 flask_sqlalchemy 导入 SQLAlchemy，供本文件后续逻辑调用。

db = SQLAlchemy()  # 设置 db 的值，供后续业务判断、查询或响应组装使用。
