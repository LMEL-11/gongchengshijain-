import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app
from extensions import db
from models import City, District, Property, Facility, PriceHistory

BASE_DIR = Path(__file__).resolve().parent
SQLITE_URL = f"sqlite:///{BASE_DIR / 'housing.db'}"

TABLES = [City, District, Property, Facility, PriceHistory]


def copy_row(obj, model):
    data = {
        col.name: getattr(obj, col.name)
        for col in model.__table__.columns
    }
    return model(**data)


def main():
    mysql_app = create_app()

    sqlite_engine = create_engine(SQLITE_URL)
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SQLiteSession()

    with mysql_app.app_context():
        db.create_all()

        # 按外键依赖顺序清空 MySQL 表
        for model in reversed(TABLES):
            db.session.query(model).delete()
        db.session.commit()

        # 按依赖顺序复制数据，保留原 id
        for model in TABLES:
            rows = sqlite_session.query(model).all()
            db.session.bulk_save_objects([copy_row(row, model) for row in rows])
            db.session.commit()
            print(f"{model.__tablename__}: {len(rows)} rows copied")

    sqlite_session.close()
    print("migration done")


if __name__ == "__main__":
    main()
