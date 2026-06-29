"""Shared Flask extensions, instantiated here to avoid circular imports."""
from flask_sqlalchemy import SQLAlchemy  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

db = SQLAlchemy()  # 计算或更新db中间数据，作为后续业务判断、统计或响应组装的输入。
