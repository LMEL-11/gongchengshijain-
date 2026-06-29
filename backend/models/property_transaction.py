"""管理员录入的房源交易属性扩展信息。"""
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


class PropertyTransaction(db.Model):  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """表示房源交易扩展信息，如挂牌日期、产权和卖点说明。"""
    __tablename__ = "property_transactions"  # 计算或更新__tablename__中间数据，作为后续业务判断、统计或响应组装的输入。

    id = db.Column(db.Integer, primary_key=True)  # 该字段用于存储记录主键编号，用于数据库定位和前端引用唯一数据。
    property_id = db.Column(  # 该字段用于存储所属房源外键，用于把交易扩展信息绑定到具体房源。
        db.Integer,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        db.ForeignKey("properties.id", ondelete="CASCADE"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        nullable=False,  # 计算或更新nullable中间数据，作为后续业务判断、统计或响应组装的输入。
        unique=True,  # 计算或更新unique中间数据，作为后续业务判断、统计或响应组装的输入。
        index=True,  # 计算或更新index中间数据，作为后续业务判断、统计或响应组装的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    listing_date = db.Column(db.String(30))  # 该字段用于存储挂牌时间，用于统计挂牌趋势和房源新鲜度。
    ownership_type = db.Column(db.String(50))  # 该字段用于存储房屋用途或权属类型，用于交易属性画像统计。
    property_right = db.Column(db.String(50))  # 该字段用于存储产权年限或产权类型，用于交易属性画像统计。
    mortgage = db.Column(db.String(100))  # 该字段用于存储抵押状态，用于交易风险和房源画像展示。
    selling_point = db.Column(db.Text)  # 该字段用于存储核心卖点文本，用于详情页展示和标签提取。
    community_intro = db.Column(db.Text)  # 该字段用于存储小区介绍文本，用于补充房源周边和社区信息。
    layout_intro = db.Column(db.Text)  # 该字段用于存储户型介绍文本，用于补充房源结构信息。
    transport_intro = db.Column(db.Text)  # 该字段用于存储交通介绍文本，用于补充通勤和区位信息。

    property = db.relationship("Property", back_populates="transaction")  # 该关系用于关联property相关业务数据，便于接口查询时联动读取。

    def to_dict(self) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
            "listing_date": self.listing_date,  # 把listing_date字段写入响应数据，供前端页面、图表或后续接口读取。
            "ownership_type": self.ownership_type,  # 把ownership_type字段写入响应数据，供前端页面、图表或后续接口读取。
            "property_right": self.property_right,  # 把property_right字段写入响应数据，供前端页面、图表或后续接口读取。
            "mortgage": self.mortgage,  # 把mortgage字段写入响应数据，供前端页面、图表或后续接口读取。
            "selling_point": self.selling_point,  # 把selling_point字段写入响应数据，供前端页面、图表或后续接口读取。
            "community_intro": self.community_intro,  # 把community_intro字段写入响应数据，供前端页面、图表或后续接口读取。
            "layout_intro": self.layout_intro,  # 把layout_intro字段写入响应数据，供前端页面、图表或后续接口读取。
            "transport_intro": self.transport_intro,  # 把transport_intro字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
