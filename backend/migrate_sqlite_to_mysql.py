"""文件功能：将旧 SQLite 数据库中的城市、区域、房源和价格历史数据迁移到当前数据库。"""

import os  # 逐行注释：导入本行所需的模块或对象。
from pathlib import Path  # 逐行注释：导入本行所需的模块或对象。

from sqlalchemy import create_engine  # 逐行注释：导入本行所需的模块或对象。
from sqlalchemy.orm import sessionmaker  # 逐行注释：导入本行所需的模块或对象。

from app import create_app  # 逐行注释：导入本行所需的模块或对象。
from extensions import db  # 逐行注释：导入本行所需的模块或对象。
from models import City, District, Property, Facility, PriceHistory  # 逐行注释：导入本行所需的模块或对象。

BASE_DIR = Path(__file__).resolve().parent  # 逐行注释：赋值或更新当前变量/字段。
SQLITE_URL = f"sqlite:///{BASE_DIR / 'housing.db'}"  # 逐行注释：赋值或更新当前变量/字段。

TABLES = [City, District, Property, Facility, PriceHistory]  # 逐行注释：赋值或更新当前变量/字段。


def copy_row(obj, model):  # 逐行注释：声明函数或方法入口。
    """按模型字段把旧库记录复制成新库模型实例。"""
    data = {  # 逐行注释：赋值或更新当前变量/字段。
        col.name: getattr(obj, col.name)  # 逐行注释：设置当前数据项或参数。
        for col in model.__table__.columns  # 逐行注释：遍历集合中的每一项并执行处理。
    }  # 逐行注释：结束当前数据结构或调用块。
    return model(**data)  # 逐行注释：返回当前逻辑的处理结果。


def main():  # 逐行注释：声明函数或方法入口。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    mysql_app = create_app()  # 逐行注释：赋值或更新当前变量/字段。

    sqlite_engine = create_engine(SQLITE_URL)  # 逐行注释：赋值或更新当前变量/字段。
    SQLiteSession = sessionmaker(bind=sqlite_engine)  # 逐行注释：赋值或更新当前变量/字段。
    sqlite_session = SQLiteSession()  # 逐行注释：赋值或更新当前变量/字段。

    with mysql_app.app_context():  # 逐行注释：进入上下文管理器并自动处理资源。
        db.create_all()  # 逐行注释：执行本行代码逻辑。

        # 按外键依赖顺序清空 MySQL 表
        for model in reversed(TABLES):  # 逐行注释：遍历集合中的每一项并执行处理。
            db.session.query(model).delete()  # 逐行注释：执行本行代码逻辑。
        db.session.commit()  # 逐行注释：提交当前数据库事务。

        # 按依赖顺序复制数据，保留原 id
        for model in TABLES:  # 逐行注释：遍历集合中的每一项并执行处理。
            rows = sqlite_session.query(model).all()  # 逐行注释：赋值或更新当前变量/字段。
            db.session.bulk_save_objects([copy_row(row, model) for row in rows])  # 逐行注释：执行本行代码逻辑。
            db.session.commit()  # 逐行注释：提交当前数据库事务。
            print(f"{model.__tablename__}: {len(rows)} rows copied")  # 逐行注释：设置当前数据项或参数。

    sqlite_session.close()  # 逐行注释：执行本行代码逻辑。
    print("migration done")  # 逐行注释：执行本行代码逻辑。


if __name__ == "__main__":  # 逐行注释：根据条件判断是否进入该分支。
    main()  # 逐行注释：执行本行代码逻辑。
