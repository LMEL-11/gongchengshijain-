"""周边配套设施 Facility model（学校、医院、地铁等）。"""
from extensions import db

# 设施类别 -> 中文名（前端图例使用）
FACILITY_CATEGORIES = {
    "school": "学校",
    "hospital": "医院",
    "subway": "地铁",
    "transport": "交通",
    "mall": "商场",
    "park": "公园",
}


class Facility(db.Model):
    """表示区域周边配套设施及其类型、位置和评分信息。"""
    __tablename__ = "facilities"

    id = db.Column(db.Integer, primary_key=True)
    district_id = db.Column(
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True
    )
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)  # school/hospital/subway/...
    lng = db.Column(db.Float)
    lat = db.Column(db.Float)

    district = db.relationship("District", back_populates="facilities")

    def to_dict(self) -> dict:
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {
            "id": self.id,
            "district_id": self.district_id,
            "name": self.name,
            "category": self.category,
            "category_label": FACILITY_CATEGORIES.get(self.category, self.category),
            "lng": self.lng,
            "lat": self.lat,
        }
