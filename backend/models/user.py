"""用户 User model."""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model):
    """表示系统用户账号、密码哈希和角色权限。"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user")  # "user" or "admin"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """为用户设置密码并保存安全哈希。"""
        # Use pbkdf2:sha256 for compatibility with Python 3.9 (no scrypt)
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        """校验明文密码是否匹配当前用户的密码哈希。"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
