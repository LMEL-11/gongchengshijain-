"""管理员录入的房源交易属性扩展信息。"""
from extensions import db  # 导入本行所需的模块或对象。


class PropertyTransaction(db.Model):  # 声明类并定义相关数据或行为。
    """表示房源交易扩展信息，如挂牌日期、产权和卖点说明。"""
    __tablename__ = "property_transactions"  # 赋值或更新当前变量/字段。

    id = db.Column(db.Integer, primary_key=True)  # 赋值或更新当前变量/字段。
    property_id = db.Column(  # 赋值或更新当前变量/字段。
        db.Integer,  # 设置当前数据项或参数。
        db.ForeignKey("properties.id", ondelete="CASCADE"),  # 赋值或更新当前变量/字段。
        nullable=False,  # 赋值或更新当前变量/字段。
        unique=True,  # 赋值或更新当前变量/字段。
        index=True,  # 赋值或更新当前变量/字段。
    )  # 结束当前数据结构或调用块。
    listing_date = db.Column(db.String(30))  # 赋值或更新当前变量/字段。
    ownership_type = db.Column(db.String(50))  # 赋值或更新当前变量/字段。
    property_right = db.Column(db.String(50))  # 赋值或更新当前变量/字段。
    mortgage = db.Column(db.String(100))  # 赋值或更新当前变量/字段。
    selling_point = db.Column(db.Text)  # 赋值或更新当前变量/字段。
    community_intro = db.Column(db.Text)  # 赋值或更新当前变量/字段。
    layout_intro = db.Column(db.Text)  # 赋值或更新当前变量/字段。
    transport_intro = db.Column(db.Text)  # 赋值或更新当前变量/字段。

    property = db.relationship("Property", back_populates="transaction")  # 赋值或更新当前变量/字段。

    def to_dict(self) -> dict:  # 声明函数或方法入口。
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {  # 返回当前逻辑的处理结果。
            "listing_date": self.listing_date,  # 设置当前数据项或参数。
            "ownership_type": self.ownership_type,  # 设置当前数据项或参数。
            "property_right": self.property_right,  # 设置当前数据项或参数。
            "mortgage": self.mortgage,  # 设置当前数据项或参数。
            "selling_point": self.selling_point,  # 设置当前数据项或参数。
            "community_intro": self.community_intro,  # 设置当前数据项或参数。
            "layout_intro": self.layout_intro,  # 设置当前数据项或参数。
            "transport_intro": self.transport_intro,  # 设置当前数据项或参数。
        }  # 结束当前数据结构或调用块。
