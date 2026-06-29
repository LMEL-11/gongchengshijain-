"""用户 User model."""
from datetime import datetime  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from werkzeug.security import check_password_hash, generate_password_hash  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


class User(db.Model):  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """表示系统用户账号、密码哈希和角色权限。"""
    __tablename__ = "users"  # 计算或更新__tablename__中间数据，作为后续业务判断、统计或响应组装的输入。

    id = db.Column(db.Integer, primary_key=True)  # 该字段用于存储记录主键编号，用于数据库定位和前端引用唯一数据。
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)  # 该字段用于存储登录用户名，用于账号识别和权限校验。
    password_hash = db.Column(db.String(256), nullable=False)  # 该字段用于存储加密后的密码摘要，用于登录时进行安全比对。
    role = db.Column(db.String(20), default="user")  # "user" or "admin"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 该字段用于存储记录创建时间，用于追踪数据写入时间和排序。

    def set_password(self, password: str) -> None:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """为用户设置密码并保存安全哈希。"""
        # Use pbkdf2:sha256 for compatibility with Python 3.9 (no scrypt)
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    def check_password(self, password: str) -> bool:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """校验明文密码是否匹配当前用户的密码哈希。"""
        return check_password_hash(self.password_hash, password)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    def to_dict(self) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
            "id": self.id,  # 把id字段写入响应数据，供前端页面、图表或后续接口读取。
            "username": self.username,  # 把username字段写入响应数据，供前端页面、图表或后续接口读取。
            "role": self.role,  # 把role字段写入响应数据，供前端页面、图表或后续接口读取。
            "created_at": self.created_at.isoformat() if self.created_at else None,  # 把created_at字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
