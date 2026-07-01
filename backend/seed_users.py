"""创建默认的 admin 和 user 账户。

用法: ``flask seed-users``
"""
from flask import Flask  # 从 flask 导入 Flask，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models.user import User  # 从 models.user 导入 User，供本文件后续逻辑调用。


def run_seed_users(app: Flask) -> None:  # 定义 run_seed_users 函数，集中处理这一段业务逻辑。
    """创建或更新默认管理员和普通用户账号。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    with app.app_context():  # 进入上下文管理流程，自动处理资源打开和释放。
        # 若已存在则跳过
        admin = db.session.query(User).filter_by(username="admin").first()  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        if admin is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            admin = User(username="admin", role="admin")  # 设置 admin 的值，供后续业务判断、查询或响应组装使用。
            admin.set_password("admin123")  # 执行当前代码行对应的业务处理步骤。
            db.session.add(admin)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            print("[seed-users] 已创建管理员账户 admin / admin123")  # 输出当前处理结果或运行状态，方便调试和观察流程。
        else:  # 处理前面条件都未命中的兜底分支。
            print("[seed-users] 管理员账户已存在，跳过")  # 输出当前处理结果或运行状态，方便调试和观察流程。

        user = db.session.query(User).filter_by(username="user").first()  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        if user is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            user = User(username="user", role="user")  # 设置 user 的值，供后续业务判断、查询或响应组装使用。
            user.set_password("user123")  # 执行当前代码行对应的业务处理步骤。
            db.session.add(user)  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
            print("[seed-users] 已创建普通用户账户 user / user123")  # 输出当前处理结果或运行状态，方便调试和观察流程。
        else:  # 处理前面条件都未命中的兜底分支。
            print("[seed-users] 普通用户账户已存在，跳过")  # 输出当前处理结果或运行状态，方便调试和观察流程。

        db.session.commit()  # 同步数据库会话状态，完成新增、删除、提交或主键回填。
        print("[seed-users] ✅ 完成。请在生产环境中修改默认密码！")  # 输出当前处理结果或运行状态，方便调试和观察流程。
