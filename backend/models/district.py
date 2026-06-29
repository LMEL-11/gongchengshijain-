"""行政区 District model."""
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


class District(db.Model):  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """表示城市下的区域信息、地图位置和房源关联。"""
    __tablename__ = "districts"  # 计算或更新__tablename__中间数据，作为后续业务判断、统计或响应组装的输入。

    id = db.Column(db.Integer, primary_key=True)  # 该字段用于存储记录主键编号，用于数据库定位和前端引用唯一数据。
    city_id = db.Column(  # 该字段用于存储所属城市外键，用于把区域、房源或统计数据归属到城市。
        db.Integer, db.ForeignKey("cities.id"), nullable=False, index=True  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    name = db.Column(db.String(50), nullable=False)  # 海淀区
    lng = db.Column(db.Float)  # 该字段用于存储经度坐标，用于地图定位、点位展示和空间聚合。
    lat = db.Column(db.Float)  # 该字段用于存储纬度坐标，用于地图定位、点位展示和空间聚合。
    # Stored grid position (col, row) used to lay out the 3D city map.
    grid_x = db.Column(db.Integer, default=0)  # 该字段用于存储3D城市地图网格列位置，用于把行政区摆放到可视化布局中。
    grid_y = db.Column(db.Integer, default=0)  # 该字段用于存储3D城市地图网格行位置，用于把行政区摆放到可视化布局中。

    city = db.relationship("City", back_populates="districts")  # 该关系用于关联city相关业务数据，便于接口查询时联动读取。
    properties = db.relationship(  # 该关系用于关联properties相关业务数据，便于接口查询时联动读取。
        "Property", back_populates="district", cascade="all, delete-orphan"  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    facilities = db.relationship(  # 该关系用于关联facilities相关业务数据，便于接口查询时联动读取。
        "Facility", back_populates="district", cascade="all, delete-orphan"  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    def avg_unit_price(self) -> float:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """Average listing price per square metre (元/㎡)."""
        prices = [p.unit_price for p in self.properties if p.unit_price]  # 初始化prices中间数据列表，用于收集清洗后的多条业务数据。
        return round(sum(prices) / len(prices)) if prices else 0  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    def to_dict(self, with_stats: bool = True) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将当前模型实例转换为接口可返回的字典结构。"""
        data = {  # 初始化响应数据结构字典，用于承载接口返回或中间聚合结果。
            "id": self.id,  # 把id字段写入响应数据，供前端页面、图表或后续接口读取。
            "city_id": self.city_id,  # 把city_id字段写入响应数据，供前端页面、图表或后续接口读取。
            "name": self.name,  # 把name字段写入响应数据，供前端页面、图表或后续接口读取。
            "lng": self.lng,  # 把lng字段写入响应数据，供前端页面、图表或后续接口读取。
            "lat": self.lat,  # 把lat字段写入响应数据，供前端页面、图表或后续接口读取。
            "grid_x": self.grid_x,  # 把grid_x字段写入响应数据，供前端页面、图表或后续接口读取。
            "grid_y": self.grid_y,  # 把grid_y字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        if with_stats:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            data["avg_unit_price"] = self.avg_unit_price()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            data["property_count"] = len(self.properties)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return data  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
