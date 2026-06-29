"""房源 Property (listing) model."""
from datetime import datetime  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


class Property(db.Model):  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """表示单套房源的价格、面积、楼层、坐标和来源信息。"""
    __tablename__ = "properties"  # 计算或更新__tablename__中间数据，作为后续业务判断、统计或响应组装的输入。

    id = db.Column(db.Integer, primary_key=True)  # 该字段用于存储记录主键编号，用于数据库定位和前端引用唯一数据。
    district_id = db.Column(  # 该字段用于存储所属行政区外键，用于把房源、设施或历史价格归属到区域。
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    title = db.Column(db.String(200), nullable=False)  # 该字段用于存储房源标题，用于列表展示、搜索匹配和去重参考。
    total_price = db.Column(db.Float)  # 总价（万元）
    unit_price = db.Column(db.Float, index=True)  # 单价（元/㎡）
    area = db.Column(db.Float)  # 建筑面积（㎡）
    rooms = db.Column(db.Integer, default=0)  # 室
    halls = db.Column(db.Integer, default=0)  # 厅
    floor = db.Column(db.Integer)  # 所在楼层
    total_floors = db.Column(db.Integer)  # 总楼层
    build_year = db.Column(db.Integer)  # 建成年份
    orientation = db.Column(db.String(20))  # 朝向，如 "南北"
    decoration = db.Column(db.String(20))  # 装修，如 "精装"
    has_elevator = db.Column(db.Boolean, default=False)  # 是否有电梯
    listing_type = db.Column(db.String(20), default="二手房")  # 二手房 / 出租

    lng = db.Column(db.Float)  # 该字段用于存储经度坐标，用于地图定位、点位展示和空间聚合。
    lat = db.Column(db.Float)  # 该字段用于存储纬度坐标，用于地图定位、点位展示和空间聚合。

    source = db.Column(db.String(50))  # 数据来源
    source_url = db.Column(db.String(500))  # 该字段用于存储原始房源链接，用于跨表关联、去重和追溯来源。
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 该字段用于存储记录创建时间，用于追踪数据写入时间和排序。

    district = db.relationship("District", back_populates="properties")  # 该关系用于关联district相关业务数据，便于接口查询时联动读取。
    transaction = db.relationship(  # 该关系用于关联transaction相关业务数据，便于接口查询时联动读取。
        "PropertyTransaction",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        back_populates="property",  # 计算或更新back_populates中间数据，作为后续业务判断、统计或响应组装的输入。
        uselist=False,  # 计算或更新uselist中间数据，作为后续业务判断、统计或响应组装的输入。
        cascade="all, delete-orphan",  # 计算或更新cascade中间数据，作为后续业务判断、统计或响应组装的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    def layout(self) -> str:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """Human-readable layout, e.g. "3室2厅"."""
        return f"{self.rooms or 0}室{self.halls or 0}厅"  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    def to_dict(self, detail: bool = False) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将当前模型实例转换为接口可返回的字典结构。"""
        data = {  # 初始化响应数据结构字典，用于承载接口返回或中间聚合结果。
            "id": self.id,  # 把id字段写入响应数据，供前端页面、图表或后续接口读取。
            "district_id": self.district_id,  # 把district_id字段写入响应数据，供前端页面、图表或后续接口读取。
            "district_name": self.district.name if self.district else None,  # 把district_name字段写入响应数据，供前端页面、图表或后续接口读取。
            "city_name": self.district.city.name if self.district and self.district.city else None,  # 把city_name字段写入响应数据，供前端页面、图表或后续接口读取。
            "title": self.title,  # 把title字段写入响应数据，供前端页面、图表或后续接口读取。
            "total_price": self.total_price,  # 把total_price字段写入响应数据，供前端页面、图表或后续接口读取。
            "unit_price": self.unit_price,  # 把unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
            "area": self.area,  # 把area字段写入响应数据，供前端页面、图表或后续接口读取。
            "layout": self.layout(),  # 把layout字段写入响应数据，供前端页面、图表或后续接口读取。
            "rooms": self.rooms,  # 把rooms字段写入响应数据，供前端页面、图表或后续接口读取。
            "halls": self.halls,  # 把halls字段写入响应数据，供前端页面、图表或后续接口读取。
            "listing_type": self.listing_type,  # 把listing_type字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        if detail:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            data.update(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                    "floor": self.floor,  # 把floor字段写入响应数据，供前端页面、图表或后续接口读取。
                    "total_floors": self.total_floors,  # 把total_floors字段写入响应数据，供前端页面、图表或后续接口读取。
                    "build_year": self.build_year,  # 把build_year字段写入响应数据，供前端页面、图表或后续接口读取。
                    "orientation": self.orientation,  # 把orientation字段写入响应数据，供前端页面、图表或后续接口读取。
                    "decoration": self.decoration,  # 把decoration字段写入响应数据，供前端页面、图表或后续接口读取。
                    "has_elevator": self.has_elevator,  # 把has_elevator字段写入响应数据，供前端页面、图表或后续接口读取。
                    "lng": self.lng,  # 把lng字段写入响应数据，供前端页面、图表或后续接口读取。
                    "lat": self.lat,  # 把lat字段写入响应数据，供前端页面、图表或后续接口读取。
                    "source": self.source,  # 把source字段写入响应数据，供前端页面、图表或后续接口读取。
                    "source_url": self.source_url,  # 把source_url字段写入响应数据，供前端页面、图表或后续接口读取。
                    "created_at": self.created_at.isoformat() if self.created_at else None,  # 把created_at字段写入响应数据，供前端页面、图表或后续接口读取。
                }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        return data  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
