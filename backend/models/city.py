"""城市 City model."""
from extensions import db  # 导入本行所需的模块或对象。


class City(db.Model):  # 声明类并定义相关数据或行为。
    """表示城市基础信息及其下属行政区关系。"""
    __tablename__ = "cities"  # 赋值或更新当前变量/字段。

    id = db.Column(db.Integer, primary_key=True)  # 赋值或更新当前变量/字段。
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)  # 北京
    name_en = db.Column(db.String(50))  # beijing
    province = db.Column(db.String(50))  # 赋值或更新当前变量/字段。
    lng = db.Column(db.Float)  # 中心经度
    lat = db.Column(db.Float)  # 中心纬度

    districts = db.relationship(  # 赋值或更新当前变量/字段。
        "District", back_populates="city", cascade="all, delete-orphan"  # 赋值或更新当前变量/字段。
    )  # 结束当前数据结构或调用块。

    def to_dict(self) -> dict:  # 声明函数或方法入口。
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {  # 返回当前逻辑的处理结果。
            "id": self.id,  # 设置当前数据项或参数。
            "name": self.name,  # 设置当前数据项或参数。
            "name_en": self.name_en,  # 设置当前数据项或参数。
            "province": self.province,  # 设置当前数据项或参数。
            "lng": self.lng,  # 设置当前数据项或参数。
            "lat": self.lat,  # 设置当前数据项或参数。
            "district_count": len(self.districts),  # 设置当前数据项或参数。
        }  # 结束当前数据结构或调用块。
