"""管理员录入的房源交易属性扩展信息。"""  # 保留字符串内容，作为说明文本或页面展示文案。
from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。


class PropertyTransaction(db.Model):  # 定义 PropertyTransaction(db.Model 类，封装对应的数据结构或业务行为。
    """表示房源交易扩展信息，如挂牌日期、产权和卖点说明。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    __tablename__ = "property_transactions"  # 设置 __tablename__ 的值，供后续业务判断、查询或响应组装使用。

    id = db.Column(db.Integer, primary_key=True)  # 设置 id 的值，供后续业务判断、查询或响应组装使用。
    property_id = db.Column(  # 设置 property_id 的值，供后续业务判断、查询或响应组装使用。
        db.Integer,  # 执行当前代码行对应的业务处理步骤。
        db.ForeignKey("properties.id", ondelete="CASCADE"),  # 设置 db.ForeignKey("properties.id", ondelete 的值，供后续业务判断、查询或响应组装使用。
        nullable=False,  # 设置 nullable 的值，供后续业务判断、查询或响应组装使用。
        unique=True,  # 设置 unique 的值，供后续业务判断、查询或响应组装使用。
        index=True,  # 设置 index 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。
    listing_date = db.Column(db.String(30))  # 设置 listing_date 的值，供后续业务判断、查询或响应组装使用。
    ownership_type = db.Column(db.String(50))  # 设置 ownership_type 的值，供后续业务判断、查询或响应组装使用。
    property_right = db.Column(db.String(50))  # 设置 property_right 的值，供后续业务判断、查询或响应组装使用。
    mortgage = db.Column(db.String(100))  # 设置 mortgage 的值，供后续业务判断、查询或响应组装使用。
    selling_point = db.Column(db.Text)  # 设置 selling_point 的值，供后续业务判断、查询或响应组装使用。
    community_intro = db.Column(db.Text)  # 设置 community_intro 的值，供后续业务判断、查询或响应组装使用。
    layout_intro = db.Column(db.Text)  # 设置 layout_intro 的值，供后续业务判断、查询或响应组装使用。
    transport_intro = db.Column(db.Text)  # 设置 transport_intro 的值，供后续业务判断、查询或响应组装使用。

    property = db.relationship("Property", back_populates="transaction")  # 设置 property 的值，供后续业务判断、查询或响应组装使用。

    def to_dict(self) -> dict:  # 定义 to_dict 函数，集中处理这一段业务逻辑。
        """将当前模型实例转换为接口可返回的字典结构。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return {  # 返回处理后的结果给调用方继续使用。
            "listing_date": self.listing_date,  # 保留字符串内容，作为说明文本或页面展示文案。
            "ownership_type": self.ownership_type,  # 保留字符串内容，作为说明文本或页面展示文案。
            "property_right": self.property_right,  # 保留字符串内容，作为说明文本或页面展示文案。
            "mortgage": self.mortgage,  # 保留字符串内容，作为说明文本或页面展示文案。
            "selling_point": self.selling_point,  # 保留字符串内容，作为说明文本或页面展示文案。
            "community_intro": self.community_intro,  # 保留字符串内容，作为说明文本或页面展示文案。
            "layout_intro": self.layout_intro,  # 保留字符串内容，作为说明文本或页面展示文案。
            "transport_intro": self.transport_intro,  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
