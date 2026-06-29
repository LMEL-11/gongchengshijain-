"""房源 Property (listing) model."""
from datetime import datetime  # 逐行注释：导入本行所需的模块或对象。

from extensions import db  # 逐行注释：导入本行所需的模块或对象。


class Property(db.Model):  # 逐行注释：声明类并定义相关数据或行为。
    """表示单套房源的价格、面积、楼层、坐标和来源信息。"""
    __tablename__ = "properties"  # 逐行注释：赋值或更新当前变量/字段。

    id = db.Column(db.Integer, primary_key=True)  # 逐行注释：赋值或更新当前变量/字段。
    district_id = db.Column(  # 逐行注释：赋值或更新当前变量/字段。
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True  # 逐行注释：赋值或更新当前变量/字段。
    )  # 逐行注释：结束当前数据结构或调用块。

    title = db.Column(db.String(200), nullable=False)  # 逐行注释：赋值或更新当前变量/字段。
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

    lng = db.Column(db.Float)  # 逐行注释：赋值或更新当前变量/字段。
    lat = db.Column(db.Float)  # 逐行注释：赋值或更新当前变量/字段。

    source = db.Column(db.String(50))  # 数据来源
    source_url = db.Column(db.String(500))  # 逐行注释：赋值或更新当前变量/字段。
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 逐行注释：赋值或更新当前变量/字段。

    district = db.relationship("District", back_populates="properties")  # 逐行注释：赋值或更新当前变量/字段。
    transaction = db.relationship(  # 逐行注释：赋值或更新当前变量/字段。
        "PropertyTransaction",  # 逐行注释：设置当前数据项或参数。
        back_populates="property",  # 逐行注释：赋值或更新当前变量/字段。
        uselist=False,  # 逐行注释：赋值或更新当前变量/字段。
        cascade="all, delete-orphan",  # 逐行注释：赋值或更新当前变量/字段。
    )  # 逐行注释：结束当前数据结构或调用块。

    def layout(self) -> str:  # 逐行注释：声明函数或方法入口。
        """Human-readable layout, e.g. "3室2厅"."""
        return f"{self.rooms or 0}室{self.halls or 0}厅"  # 逐行注释：返回当前逻辑的处理结果。

    def to_dict(self, detail: bool = False) -> dict:  # 逐行注释：声明函数或方法入口。
        """将当前模型实例转换为接口可返回的字典结构。"""
        data = {  # 逐行注释：赋值或更新当前变量/字段。
            "id": self.id,  # 逐行注释：设置当前数据项或参数。
            "district_id": self.district_id,  # 逐行注释：设置当前数据项或参数。
            "district_name": self.district.name if self.district else None,  # 逐行注释：设置当前数据项或参数。
            "city_name": self.district.city.name if self.district and self.district.city else None,  # 逐行注释：设置当前数据项或参数。
            "title": self.title,  # 逐行注释：设置当前数据项或参数。
            "total_price": self.total_price,  # 逐行注释：设置当前数据项或参数。
            "unit_price": self.unit_price,  # 逐行注释：设置当前数据项或参数。
            "area": self.area,  # 逐行注释：设置当前数据项或参数。
            "layout": self.layout(),  # 逐行注释：设置当前数据项或参数。
            "rooms": self.rooms,  # 逐行注释：设置当前数据项或参数。
            "halls": self.halls,  # 逐行注释：设置当前数据项或参数。
            "listing_type": self.listing_type,  # 逐行注释：设置当前数据项或参数。
        }  # 逐行注释：结束当前数据结构或调用块。
        if detail:  # 逐行注释：根据条件判断是否进入该分支。
            data.update(  # 逐行注释：执行本行代码逻辑。
                {  # 逐行注释：执行本行代码逻辑。
                    "floor": self.floor,  # 逐行注释：设置当前数据项或参数。
                    "total_floors": self.total_floors,  # 逐行注释：设置当前数据项或参数。
                    "build_year": self.build_year,  # 逐行注释：设置当前数据项或参数。
                    "orientation": self.orientation,  # 逐行注释：设置当前数据项或参数。
                    "decoration": self.decoration,  # 逐行注释：设置当前数据项或参数。
                    "has_elevator": self.has_elevator,  # 逐行注释：设置当前数据项或参数。
                    "lng": self.lng,  # 逐行注释：设置当前数据项或参数。
                    "lat": self.lat,  # 逐行注释：设置当前数据项或参数。
                    "source": self.source,  # 逐行注释：设置当前数据项或参数。
                    "source_url": self.source_url,  # 逐行注释：设置当前数据项或参数。
                    "created_at": self.created_at.isoformat() if self.created_at else None,  # 逐行注释：设置当前数据项或参数。
                }  # 逐行注释：结束当前数据结构或调用块。
            )  # 逐行注释：结束当前数据结构或调用块。
        return data  # 逐行注释：返回当前逻辑的处理结果。
