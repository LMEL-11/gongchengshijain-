"""房价走势 PriceHistory model（按区按月的均价快照）。"""
from extensions import db


class PriceHistory(db.Model):
    __tablename__ = "price_history"

    id = db.Column(db.Integer, primary_key=True)
    district_id = db.Column(
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True
    )
    month = db.Column(db.String(7), nullable=False)  # 'YYYY-MM'
    avg_unit_price = db.Column(db.Float)  # 当月均价（元/㎡）

    district = db.relationship("District")

    def to_dict(self) -> dict:
        return {
            "district_id": self.district_id,
            "month": self.month,
            "avg_unit_price": self.avg_unit_price,
        }
