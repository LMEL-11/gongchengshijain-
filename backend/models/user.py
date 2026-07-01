"""用户 User model."""  # 保留字符串内容，作为说明文本或页面展示文案。
from datetime import datetime  # 从 datetime 导入 datetime，供本文件后续逻辑调用。

from werkzeug.security import check_password_hash, generate_password_hash  # 从 werkzeug.security 导入 check_password_hash, generate_password_hash，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。


class User(db.Model):  # 定义 User(db.Model 类，封装对应的数据结构或业务行为。
    """表示系统用户账号、密码哈希和角色权限。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    __tablename__ = "users"  # 设置 __tablename__ 的值，供后续业务判断、查询或响应组装使用。

    id = db.Column(db.Integer, primary_key=True)  # 设置 id 的值，供后续业务判断、查询或响应组装使用。
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)  # 设置 username 的值，供后续业务判断、查询或响应组装使用。
    password_hash = db.Column(db.String(256), nullable=False)  # 设置 password_hash 的值，供后续业务判断、查询或响应组装使用。
    role = db.Column(db.String(20), default="user")  # 设置 role 的值，供后续业务判断、查询或响应组装使用。
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 设置 created_at 的值，供后续业务判断、查询或响应组装使用。

    def set_password(self, password: str) -> None:  # 定义 set_password 函数，集中处理这一段业务逻辑。
        """为用户设置密码并保存安全哈希。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        # Use pbkdf2:sha256 for compatibility with Python 3.9 (no scrypt)
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")  # 设置 self.password_hash 的值，供后续业务判断、查询或响应组装使用。

    def check_password(self, password: str) -> bool:  # 定义 check_password 函数，集中处理这一段业务逻辑。
        """校验明文密码是否匹配当前用户的密码哈希。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return check_password_hash(self.password_hash, password)  # 返回处理后的结果给调用方继续使用。

    def to_dict(self) -> dict:  # 定义 to_dict 函数，集中处理这一段业务逻辑。
        """将当前模型实例转换为接口可返回的字典结构。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return {  # 返回处理后的结果给调用方继续使用。
            "id": self.id,  # 保留字符串内容，作为说明文本或页面展示文案。
            "username": self.username,  # 保留字符串内容，作为说明文本或页面展示文案。
            "role": self.role,  # 保留字符串内容，作为说明文本或页面展示文案。
            "created_at": self.created_at.isoformat() if self.created_at else None,  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
