"""行政区 District model."""
from extensions import db  # 逐行注释：导入本行所需的模块或对象。


class District(db.Model):  # 逐行注释：声明类并定义相关数据或行为。
    """表示城市下的区域信息、地图位置和房源关联。"""
    __tablename__ = "districts"  # 逐行注释：赋值或更新当前变量/字段。

    id = db.Column(db.Integer, primary_key=True)  # 逐行注释：赋值或更新当前变量/字段。
    city_id = db.Column(  # 逐行注释：赋值或更新当前变量/字段。
        db.Integer, db.ForeignKey("cities.id"), nullable=False, index=True  # 逐行注释：赋值或更新当前变量/字段。
    )  # 逐行注释：结束当前数据结构或调用块。
    name = db.Column(db.String(50), nullable=False)  # 海淀区
    lng = db.Column(db.Float)  # 逐行注释：赋值或更新当前变量/字段。
    lat = db.Column(db.Float)  # 逐行注释：赋值或更新当前变量/字段。
    # Stored grid position (col, row) used to lay out the 3D city map.
    grid_x = db.Column(db.Integer, default=0)  # 逐行注释：赋值或更新当前变量/字段。
    grid_y = db.Column(db.Integer, default=0)  # 逐行注释：赋值或更新当前变量/字段。

    city = db.relationship("City", back_populates="districts")  # 逐行注释：赋值或更新当前变量/字段。
    properties = db.relationship(  # 逐行注释：赋值或更新当前变量/字段。
        "Property", back_populates="district", cascade="all, delete-orphan"  # 逐行注释：赋值或更新当前变量/字段。
    )  # 逐行注释：结束当前数据结构或调用块。
    facilities = db.relationship(  # 逐行注释：赋值或更新当前变量/字段。
        "Facility", back_populates="district", cascade="all, delete-orphan"  # 逐行注释：赋值或更新当前变量/字段。
    )  # 逐行注释：结束当前数据结构或调用块。

    def avg_unit_price(self) -> float:  # 逐行注释：声明函数或方法入口。
        """Average listing price per square metre (元/㎡)."""
        prices = [p.unit_price for p in self.properties if p.unit_price]  # 逐行注释：赋值或更新当前变量/字段。
        return round(sum(prices) / len(prices)) if prices else 0  # 逐行注释：返回当前逻辑的处理结果。

    def to_dict(self, with_stats: bool = True) -> dict:  # 逐行注释：声明函数或方法入口。
        """将当前模型实例转换为接口可返回的字典结构。"""
        data = {  # 逐行注释：赋值或更新当前变量/字段。
            "id": self.id,  # 逐行注释：设置当前数据项或参数。
            "city_id": self.city_id,  # 逐行注释：设置当前数据项或参数。
            "name": self.name,  # 逐行注释：设置当前数据项或参数。
            "lng": self.lng,  # 逐行注释：设置当前数据项或参数。
            "lat": self.lat,  # 逐行注释：设置当前数据项或参数。
            "grid_x": self.grid_x,  # 逐行注释：设置当前数据项或参数。
            "grid_y": self.grid_y,  # 逐行注释：设置当前数据项或参数。
        }  # 逐行注释：结束当前数据结构或调用块。
        if with_stats:  # 逐行注释：根据条件判断是否进入该分支。
            data["avg_unit_price"] = self.avg_unit_price()  # 逐行注释：赋值或更新当前变量/字段。
            data["property_count"] = len(self.properties)  # 逐行注释：赋值或更新当前变量/字段。
        return data  # 逐行注释：返回当前逻辑的处理结果。
