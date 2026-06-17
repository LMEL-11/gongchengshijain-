"""行政区 District model."""
from extensions import db


class District(db.Model):
    __tablename__ = "districts"

    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(
        db.Integer, db.ForeignKey("cities.id"), nullable=False, index=True
    )
    name = db.Column(db.String(50), nullable=False)  # 海淀区
    lng = db.Column(db.Float)
    lat = db.Column(db.Float)
    # Stored grid position (col, row) used to lay out the 3D city map.
    grid_x = db.Column(db.Integer, default=0)
    grid_y = db.Column(db.Integer, default=0)

    city = db.relationship("City", back_populates="districts")
    properties = db.relationship(
        "Property", back_populates="district", cascade="all, delete-orphan"
    )
    facilities = db.relationship(
        "Facility", back_populates="district", cascade="all, delete-orphan"
    )

    def avg_unit_price(self) -> float:
        """Average listing price per square metre (元/㎡)."""
        prices = [p.unit_price for p in self.properties if p.unit_price]
        return round(sum(prices) / len(prices)) if prices else 0

    def to_dict(self, with_stats: bool = True) -> dict:
        data = {
            "id": self.id,
            "city_id": self.city_id,
            "name": self.name,
            "lng": self.lng,
            "lat": self.lat,
            "grid_x": self.grid_x,
            "grid_y": self.grid_y,
        }
        if with_stats:
            data["avg_unit_price"] = self.avg_unit_price()
            data["property_count"] = len(self.properties)
        return data
