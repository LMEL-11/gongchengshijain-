"""创建默认的 admin 和 user 账户。

用法: ``flask seed-users``
"""
from flask import Flask  # 逐行注释：导入本行所需的模块或对象。

from extensions import db  # 逐行注释：导入本行所需的模块或对象。
from models.user import User  # 逐行注释：导入本行所需的模块或对象。


def run_seed_users(app: Flask) -> None:  # 逐行注释：声明函数或方法入口。
    """创建或更新默认管理员和普通用户账号。"""
    with app.app_context():  # 逐行注释：进入上下文管理器并自动处理资源。
        # 若已存在则跳过
        admin = db.session.query(User).filter_by(username="admin").first()  # 逐行注释：赋值或更新当前变量/字段。
        if admin is None:  # 逐行注释：根据条件判断是否进入该分支。
            admin = User(username="admin", role="admin")  # 逐行注释：赋值或更新当前变量/字段。
            admin.set_password("admin123")  # 逐行注释：执行本行代码逻辑。
            db.session.add(admin)  # 逐行注释：把对象加入数据库会话等待提交。
            print("[seed-users] 已创建管理员账户 admin / admin123")  # 逐行注释：执行本行代码逻辑。
        else:  # 逐行注释：处理条件不满足时的兜底分支。
            print("[seed-users] 管理员账户已存在，跳过")  # 逐行注释：执行本行代码逻辑。

        user = db.session.query(User).filter_by(username="user").first()  # 逐行注释：赋值或更新当前变量/字段。
        if user is None:  # 逐行注释：根据条件判断是否进入该分支。
            user = User(username="user", role="user")  # 逐行注释：赋值或更新当前变量/字段。
            user.set_password("user123")  # 逐行注释：执行本行代码逻辑。
            db.session.add(user)  # 逐行注释：把对象加入数据库会话等待提交。
            print("[seed-users] 已创建普通用户账户 user / user123")  # 逐行注释：执行本行代码逻辑。
        else:  # 逐行注释：处理条件不满足时的兜底分支。
            print("[seed-users] 普通用户账户已存在，跳过")  # 逐行注释：执行本行代码逻辑。

        db.session.commit()  # 逐行注释：提交当前数据库事务。
        print("[seed-users] ✅ 完成。请在生产环境中修改默认密码！")  # 逐行注释：执行本行代码逻辑。
