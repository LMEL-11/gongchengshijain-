"""创建默认的 admin 和 user 账户。

用法: ``flask seed-users``
"""
from flask import Flask

from extensions import db
from models.user import User


def run_seed_users(app: Flask) -> None:
    with app.app_context():
        # 若已存在则跳过
        admin = db.session.query(User).filter_by(username="admin").first()
        if admin is None:
            admin = User(username="admin", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            print("[seed-users] 已创建管理员账户 admin / admin123")
        else:
            print("[seed-users] 管理员账户已存在，跳过")

        user = db.session.query(User).filter_by(username="user").first()
        if user is None:
            user = User(username="user", role="user")
            user.set_password("user123")
            db.session.add(user)
            print("[seed-users] 已创建普通用户账户 user / user123")
        else:
            print("[seed-users] 普通用户账户已存在，跳过")

        db.session.commit()
        print("[seed-users] ✅ 完成。请在生产环境中修改默认密码！")
