"""文件功能：将旧 SQLite 数据库中的城市、区域、房源和价格历史数据迁移到当前数据库。"""

import os  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from pathlib import Path  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from sqlalchemy import create_engine  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from sqlalchemy.orm import sessionmaker  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from app import create_app  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import City, District, Property, Facility, PriceHistory  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

BASE_DIR = Path(__file__).resolve().parent  # 计算或更新BASE_DIR中间数据，作为后续业务判断、统计或响应组装的输入。
SQLITE_URL = f"sqlite:///{BASE_DIR / 'housing.db'}"  # 计算或更新SQLITE_URL中间数据，作为后续业务判断、统计或响应组装的输入。

TABLES = [City, District, Property, Facility, PriceHistory]  # 初始化TABLES中间数据列表，用于收集清洗后的多条业务数据。


def copy_row(obj, model):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """按模型字段把旧库记录复制成新库模型实例。"""
    data = {  # 初始化响应数据结构字典，用于承载接口返回或中间聚合结果。
        col.name: getattr(obj, col.name)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        for col in model.__table__.columns  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return model(**data)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def main():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    mysql_app = create_app()  # 计算或更新mysql_app中间数据，作为后续业务判断、统计或响应组装的输入。

    sqlite_engine = create_engine(SQLITE_URL)  # 计算或更新sqlite_engine中间数据，作为后续业务判断、统计或响应组装的输入。
    SQLiteSession = sessionmaker(bind=sqlite_engine)  # 计算或更新SQLiteSession中间数据，作为后续业务判断、统计或响应组装的输入。
    sqlite_session = SQLiteSession()  # 计算或更新sqlite_session中间数据，作为后续业务判断、统计或响应组装的输入。

    with mysql_app.app_context():  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
        db.create_all()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        # 按外键依赖顺序清空 MySQL 表
        for model in reversed(TABLES):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            db.session.query(model).delete()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。

        # 按依赖顺序复制数据，保留原 id
        for model in TABLES:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            rows = sqlite_session.query(model).all()  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
            db.session.bulk_save_objects([copy_row(row, model) for row in rows])  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            print(f"{model.__tablename__}: {len(rows)} rows copied")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    sqlite_session.close()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    print("migration done")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。


if __name__ == "__main__":  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    main()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
