"""文件功能：将旧 SQLite 数据库中的城市、区域、房源和价格历史数据迁移到当前数据库。"""

import os  # 导入本行所需的模块或对象。
from pathlib import Path  # 导入本行所需的模块或对象。

from sqlalchemy import create_engine  # 导入本行所需的模块或对象。
from sqlalchemy.orm import sessionmaker  # 导入本行所需的模块或对象。

from app import create_app  # 导入本行所需的模块或对象。
from extensions import db  # 导入本行所需的模块或对象。
from models import City, District, Property, Facility, PriceHistory  # 导入本行所需的模块或对象。

BASE_DIR = Path(__file__).resolve().parent  # 赋值或更新当前变量/字段。
SQLITE_URL = f"sqlite:///{BASE_DIR / 'housing.db'}"  # 赋值或更新当前变量/字段。

TABLES = [City, District, Property, Facility, PriceHistory]  # 赋值或更新当前变量/字段。


def copy_row(obj, model):  # 声明函数或方法入口。
    """按模型字段把旧库记录复制成新库模型实例。"""
    data = {  # 赋值或更新当前变量/字段。
        col.name: getattr(obj, col.name)  # 设置当前数据项或参数。
        for col in model.__table__.columns  # 遍历集合中的每一项并执行处理。
    }  # 结束当前数据结构或调用块。
    return model(**data)  # 返回当前逻辑的处理结果。


def main():  # 声明函数或方法入口。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    mysql_app = create_app()  # 赋值或更新当前变量/字段。

    sqlite_engine = create_engine(SQLITE_URL)  # 赋值或更新当前变量/字段。
    SQLiteSession = sessionmaker(bind=sqlite_engine)  # 赋值或更新当前变量/字段。
    sqlite_session = SQLiteSession()  # 赋值或更新当前变量/字段。

    with mysql_app.app_context():  # 进入上下文管理器并自动处理资源。
        db.create_all()  # 执行本行代码逻辑。

        # 按外键依赖顺序清空 MySQL 表
        for model in reversed(TABLES):  # 遍历集合中的每一项并执行处理。
            db.session.query(model).delete()  # 执行本行代码逻辑。
        db.session.commit()  # 提交当前数据库事务。

        # 按依赖顺序复制数据，保留原 id
        for model in TABLES:  # 遍历集合中的每一项并执行处理。
            rows = sqlite_session.query(model).all()  # 赋值或更新当前变量/字段。
            db.session.bulk_save_objects([copy_row(row, model) for row in rows])  # 执行本行代码逻辑。
            db.session.commit()  # 提交当前数据库事务。
            print(f"{model.__tablename__}: {len(rows)} rows copied")  # 设置当前数据项或参数。

    sqlite_session.close()  # 执行本行代码逻辑。
    print("migration done")  # 执行本行代码逻辑。


if __name__ == "__main__":  # 根据条件判断是否进入该分支。
    main()  # 执行本行代码逻辑。
