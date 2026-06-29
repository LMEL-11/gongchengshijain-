"""创建默认的 admin 和 user 账户。

用法: ``flask seed-users``
"""
from flask import Flask  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models.user import User  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


def run_seed_users(app: Flask) -> None:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """创建或更新默认管理员和普通用户账号。"""
    with app.app_context():  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
        # 若已存在则跳过
        admin = db.session.query(User).filter_by(username="admin").first()  # 创建admin中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
        if admin is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            admin = User(username="admin", role="admin")  # 计算或更新admin中间数据，作为后续业务判断、统计或响应组装的输入。
            admin.set_password("admin123")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            db.session.add(admin)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            print("[seed-users] 已创建管理员账户 admin / admin123")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        else:  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
            print("[seed-users] 管理员账户已存在，跳过")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        user = db.session.query(User).filter_by(username="user").first()  # 创建user中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
        if user is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            user = User(username="user", role="user")  # 计算或更新user中间数据，作为后续业务判断、统计或响应组装的输入。
            user.set_password("user123")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            db.session.add(user)  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
            print("[seed-users] 已创建普通用户账户 user / user123")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        else:  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
            print("[seed-users] 普通用户账户已存在，跳过")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        db.session.commit()  # 把对象状态同步到数据库会话，完成新增、删除、提交或主键回填。
        print("[seed-users] ✅ 完成。请在生产环境中修改默认密码！")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
