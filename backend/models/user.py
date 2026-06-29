"""用户 User model."""
from datetime import datetime  # 导入本行所需的模块或对象。

from werkzeug.security import check_password_hash, generate_password_hash  # 导入本行所需的模块或对象。

from extensions import db  # 导入本行所需的模块或对象。


class User(db.Model):  # 声明类并定义相关数据或行为。
    """表示系统用户账号、密码哈希和角色权限。"""
    __tablename__ = "users"  # 赋值或更新当前变量/字段。

    id = db.Column(db.Integer, primary_key=True)  # 赋值或更新当前变量/字段。
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)  # 赋值或更新当前变量/字段。
    password_hash = db.Column(db.String(256), nullable=False)  # 保留语法占位以便后续扩展。
    role = db.Column(db.String(20), default="user")  # "user" or "admin"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 赋值或更新当前变量/字段。

    def set_password(self, password: str) -> None:  # 声明函数或方法入口。
        """为用户设置密码并保存安全哈希。"""
        # Use pbkdf2:sha256 for compatibility with Python 3.9 (no scrypt)
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")  # 赋值或更新当前变量/字段。

    def check_password(self, password: str) -> bool:  # 声明函数或方法入口。
        """校验明文密码是否匹配当前用户的密码哈希。"""
        return check_password_hash(self.password_hash, password)  # 返回当前逻辑的处理结果。

    def to_dict(self) -> dict:  # 声明函数或方法入口。
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {  # 返回当前逻辑的处理结果。
            "id": self.id,  # 设置当前数据项或参数。
            "username": self.username,  # 设置当前数据项或参数。
            "role": self.role,  # 设置当前数据项或参数。
            "created_at": self.created_at.isoformat() if self.created_at else None,  # 设置当前数据项或参数。
        }  # 结束当前数据结构或调用块。
