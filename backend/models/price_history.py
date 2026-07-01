"""房价走势 PriceHistory model（按区按月的均价快照）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。


class PriceHistory(db.Model):  # 定义 PriceHistory(db.Model 类，封装对应的数据结构或业务行为。
    """表示区域按月份记录的房价历史数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    __tablename__ = "price_history"  # 设置 __tablename__ 的值，供后续业务判断、查询或响应组装使用。

    id = db.Column(db.Integer, primary_key=True)  # 设置 id 的值，供后续业务判断、查询或响应组装使用。
    district_id = db.Column(  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True  # 设置 db.Integer, db.ForeignKey("districts.id"), nullable 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。
    month = db.Column(db.String(7), nullable=False)  # 设置 month 的值，供后续业务判断、查询或响应组装使用。
    avg_unit_price = db.Column(db.Float)  # 设置 avg_unit_price 的值，供后续业务判断、查询或响应组装使用。

    district = db.relationship("District")  # 设置 district 的值，供后续业务判断、查询或响应组装使用。

    def to_dict(self) -> dict:  # 定义 to_dict 函数，集中处理这一段业务逻辑。
        """将当前模型实例转换为接口可返回的字典结构。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return {  # 返回处理后的结果给调用方继续使用。
            "district_id": self.district_id,  # 保留字符串内容，作为说明文本或页面展示文案。
            "month": self.month,  # 保留字符串内容，作为说明文本或页面展示文案。
            "avg_unit_price": self.avg_unit_price,  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
