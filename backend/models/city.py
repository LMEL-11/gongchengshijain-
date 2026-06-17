"""城市 City model."""
from extensions import db


class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)  # 北京
    name_en = db.Column(db.String(50))  # beijing
    province = db.Column(db.String(50))
    lng = db.Column(db.Float)  # 中心经度
    lat = db.Column(db.Float)  # 中心纬度

    districts = db.relationship(
        "District", back_populates="city", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "name_en": self.name_en,
            "province": self.province,
            "lng": self.lng,
            "lat": self.lat,
            "district_count": len(self.districts),
        }
