"""城市 City model."""
from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


class City(db.Model):  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """表示城市基础信息及其下属行政区关系。"""
    __tablename__ = "cities"  # 计算或更新__tablename__中间数据，作为后续业务判断、统计或响应组装的输入。

    id = db.Column(db.Integer, primary_key=True)  # 该字段用于存储记录主键编号，用于数据库定位和前端引用唯一数据。
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)  # 北京
    name_en = db.Column(db.String(50))  # beijing
    province = db.Column(db.String(50))  # 该字段用于存储所属省份名称，用于全国大屏按省份聚合房源。
    lng = db.Column(db.Float)  # 中心经度
    lat = db.Column(db.Float)  # 中心纬度

    districts = db.relationship(  # 该关系用于关联districts相关业务数据，便于接口查询时联动读取。
        "District", back_populates="city", cascade="all, delete-orphan"  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    def to_dict(self) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
            "id": self.id,  # 把id字段写入响应数据，供前端页面、图表或后续接口读取。
            "name": self.name,  # 把name字段写入响应数据，供前端页面、图表或后续接口读取。
            "name_en": self.name_en,  # 把name_en字段写入响应数据，供前端页面、图表或后续接口读取。
            "province": self.province,  # 把province字段写入响应数据，供前端页面、图表或后续接口读取。
            "lng": self.lng,  # 把lng字段写入响应数据，供前端页面、图表或后续接口读取。
            "lat": self.lat,  # 把lat字段写入响应数据，供前端页面、图表或后续接口读取。
            "district_count": len(self.districts),  # 把district_count字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
