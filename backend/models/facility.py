"""周边配套设施 Facility model（学校、医院、地铁等）。"""
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

# 设施类别 -> 中文名（前端图例使用）
FACILITY_CATEGORIES = {  # 初始化FACILITY_CATEGORIES中间数据字典，用于承载接口返回或中间聚合结果。
    "school": "学校",  # 把school字段写入响应数据，供前端页面、图表或后续接口读取。
    "hospital": "医院",  # 把hospital字段写入响应数据，供前端页面、图表或后续接口读取。
    "subway": "地铁",  # 把subway字段写入响应数据，供前端页面、图表或后续接口读取。
    "transport": "交通",  # 把transport字段写入响应数据，供前端页面、图表或后续接口读取。
    "mall": "商场",  # 把mall字段写入响应数据，供前端页面、图表或后续接口读取。
    "park": "公园",  # 把park字段写入响应数据，供前端页面、图表或后续接口读取。
}  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


class Facility(db.Model):  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """表示区域周边配套设施及其类型、位置和评分信息。"""
    __tablename__ = "facilities"  # 计算或更新__tablename__中间数据，作为后续业务判断、统计或响应组装的输入。

    id = db.Column(db.Integer, primary_key=True)  # 该字段用于存储记录主键编号，用于数据库定位和前端引用唯一数据。
    district_id = db.Column(  # 该字段用于存储所属行政区外键，用于把房源、设施或历史价格归属到区域。
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    name = db.Column(db.String(100), nullable=False)  # 该字段用于存储业务名称，用于页面展示、筛选和数据映射。
    category = db.Column(db.String(20), nullable=False)  # school/hospital/subway/...
    lng = db.Column(db.Float)  # 该字段用于存储经度坐标，用于地图定位、点位展示和空间聚合。
    lat = db.Column(db.Float)  # 该字段用于存储纬度坐标，用于地图定位、点位展示和空间聚合。

    district = db.relationship("District", back_populates="facilities")  # 该关系用于关联district相关业务数据，便于接口查询时联动读取。

    def to_dict(self) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
            "id": self.id,  # 把id字段写入响应数据，供前端页面、图表或后续接口读取。
            "district_id": self.district_id,  # 把district_id字段写入响应数据，供前端页面、图表或后续接口读取。
            "name": self.name,  # 把name字段写入响应数据，供前端页面、图表或后续接口读取。
            "category": self.category,  # 把category字段写入响应数据，供前端页面、图表或后续接口读取。
            "category_label": FACILITY_CATEGORIES.get(self.category, self.category),  # 把category_label字段写入响应数据，供前端页面、图表或后续接口读取。
            "lng": self.lng,  # 把lng字段写入响应数据，供前端页面、图表或后续接口读取。
            "lat": self.lat,  # 把lat字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
