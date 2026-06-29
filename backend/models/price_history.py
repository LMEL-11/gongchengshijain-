"""房价走势 PriceHistory model（按区按月的均价快照）。"""
from extensions import db  # 导入本行所需的模块或对象。


class PriceHistory(db.Model):  # 声明类并定义相关数据或行为。
    """表示区域按月份记录的房价历史数据。"""
    __tablename__ = "price_history"  # 赋值或更新当前变量/字段。

    id = db.Column(db.Integer, primary_key=True)  # 赋值或更新当前变量/字段。
    district_id = db.Column(  # 赋值或更新当前变量/字段。
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True  # 赋值或更新当前变量/字段。
    )  # 结束当前数据结构或调用块。
    month = db.Column(db.String(7), nullable=False)  # 'YYYY-MM'
    avg_unit_price = db.Column(db.Float)  # 当月均价（元/㎡）

    district = db.relationship("District")  # 赋值或更新当前变量/字段。

    def to_dict(self) -> dict:  # 声明函数或方法入口。
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {  # 返回当前逻辑的处理结果。
            "district_id": self.district_id,  # 设置当前数据项或参数。
            "month": self.month,  # 设置当前数据项或参数。
            "avg_unit_price": self.avg_unit_price,  # 设置当前数据项或参数。
        }  # 结束当前数据结构或调用块。
