"""房价走势 PriceHistory model（按区按月的均价快照）。"""
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


class PriceHistory(db.Model):  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """表示区域按月份记录的房价历史数据。"""
    __tablename__ = "price_history"  # 计算或更新__tablename__中间数据，作为后续业务判断、统计或响应组装的输入。

    id = db.Column(db.Integer, primary_key=True)  # 该字段用于存储记录主键编号，用于数据库定位和前端引用唯一数据。
    district_id = db.Column(  # 该字段用于存储所属行政区外键，用于把房源、设施或历史价格归属到区域。
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    month = db.Column(db.String(7), nullable=False)  # 'YYYY-MM'
    avg_unit_price = db.Column(db.Float)  # 当月均价（元/㎡）

    district = db.relationship("District")  # 该关系用于关联district相关业务数据，便于接口查询时联动读取。

    def to_dict(self) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
            "district_id": self.district_id,  # 把district_id字段写入响应数据，供前端页面、图表或后续接口读取。
            "month": self.month,  # 把month字段写入响应数据，供前端页面、图表或后续接口读取。
            "avg_unit_price": self.avg_unit_price,  # 把avg_unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
