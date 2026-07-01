"""文件功能：将旧 SQLite 数据库中的城市、区域、房源和价格历史数据迁移到当前数据库。"""  # 保留字符串内容，作为说明文本或页面展示文案。

import os  # 导入 os 模块，为当前文件提供所需功能。
from pathlib import Path  # 从 pathlib 导入 Path，供本文件后续逻辑调用。

from sqlalchemy import create_engine  # 从 sqlalchemy 导入 create_engine，供本文件后续逻辑调用。
from sqlalchemy.orm import sessionmaker  # 从 sqlalchemy.orm 导入 sessionmaker，供本文件后续逻辑调用。

from app import create_app  # 从 app 导入 create_app，供本文件后续逻辑调用。
from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import City, District, Property, Facility, PriceHistory  # 从 models 导入 City, District, Property, Facility, PriceHistory，供本文件后续逻辑调用。

BASE_DIR = Path(__file__).resolve().parent  # 设置 BASE_DIR 的值，供后续业务判断、查询或响应组装使用。
SQLITE_URL = f"sqlite:///{BASE_DIR / 'housing.db'}"  # 设置 SQLITE_URL 的值，供后续业务判断、查询或响应组装使用。

TABLES = [City, District, Property, Facility, PriceHistory]  # 设置 TABLES 的值，供后续业务判断、查询或响应组装使用。


def copy_row(obj, model):  # 定义 copy_row 函数，集中处理这一段业务逻辑。
    """按模型字段把旧库记录复制成新库模型实例。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    data = {  # 设置 data 的值，供后续业务判断、查询或响应组装使用。
        col.name: getattr(obj, col.name)  # 执行当前代码行对应的业务处理步骤。
        for col in model.__table__.columns  # 遍历当前数据集合，逐项完成处理。
    }  # 结束当前多行数据结构或函数调用。
    return model(**data)  # 返回处理后的结果给调用方继续使用。


def main():  # 定义 main 函数，集中处理这一段业务逻辑。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    mysql_app = create_app()  # 设置 mysql_app 的值，供后续业务判断、查询或响应组装使用。

    sqlite_engine = create_engine(SQLITE_URL)  # 设置 sqlite_engine 的值，供后续业务判断、查询或响应组装使用。
    SQLiteSession = sessionmaker(bind=sqlite_engine)  # 设置 SQLiteSession 的值，供后续业务判断、查询或响应组装使用。
    sqlite_session = SQLiteSession()  # 设置 sqlite_session 的值，供后续业务判断、查询或响应组装使用。

    with mysql_app.app_context():  # 进入上下文管理流程，自动处理资源打开和释放。
        db.create_all()  # 执行当前代码行对应的业务处理步骤。

        # 按外键依赖顺序清空 MySQL 表
        for model in reversed(TABLES):  # 遍历当前数据集合，逐项完成处理。
            db.session.query(model).delete()  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。

        # 按依赖顺序复制数据，保留原 id
        for model in TABLES:  # 遍历当前数据集合，逐项完成处理。
            rows = sqlite_session.query(model).all()  # 构造数据库查询，用于读取、筛选或聚合业务数据。
            db.session.bulk_save_objects([copy_row(row, model) for row in rows])  # 执行当前代码行对应的业务处理步骤。
            db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            print(f"{model.__tablename__}: {len(rows)} rows copied")  # 输出当前处理结果或运行状态，方便调试和观察流程。

    sqlite_session.close()  # 执行当前代码行对应的业务处理步骤。
    print("migration done")  # 输出当前处理结果或运行状态，方便调试和观察流程。


if __name__ == "__main__":  # 判断当前条件是否成立，决定是否进入对应处理分支。
    main()  # 执行当前代码行对应的业务处理步骤。
