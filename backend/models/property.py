"""房源 Property (listing) model."""
from datetime import datetime

from extensions import db


class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)
    district_id = db.Column(
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True
    )

    title = db.Column(db.String(200), nullable=False)
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

    lng = db.Column(db.Float)
    lat = db.Column(db.Float)

    source = db.Column(db.String(50))  # 数据来源
    source_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    district = db.relationship("District", back_populates="properties")

    def layout(self) -> str:
        """Human-readable layout, e.g. "3室2厅"."""
        return f"{self.rooms or 0}室{self.halls or 0}厅"

    def to_dict(self, detail: bool = False) -> dict:
        data = {
            "id": self.id,
            "district_id": self.district_id,
            "district_name": self.district.name if self.district else None,
            "city_name": self.district.city.name if self.district and self.district.city else None,
            "title": self.title,
            "total_price": self.total_price,
            "unit_price": self.unit_price,
            "area": self.area,
            "layout": self.layout(),
            "rooms": self.rooms,
            "halls": self.halls,
            "listing_type": self.listing_type,
        }
        if detail:
            data.update(
                {
                    "floor": self.floor,
                    "total_floors": self.total_floors,
                    "build_year": self.build_year,
                    "orientation": self.orientation,
                    "decoration": self.decoration,
                    "has_elevator": self.has_elevator,
                    "lng": self.lng,
                    "lat": self.lat,
                    "source": self.source,
                    "source_url": self.source_url,
                    "created_at": self.created_at.isoformat() if self.created_at else None,
                }
            )
        return data
