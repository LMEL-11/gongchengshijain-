"""管理员录入的房源交易属性扩展信息。"""
from extensions import db


class PropertyTransaction(db.Model):
    __tablename__ = "property_transactions"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    listing_date = db.Column(db.String(30))
    ownership_type = db.Column(db.String(50))
    property_right = db.Column(db.String(50))
    mortgage = db.Column(db.String(100))
    selling_point = db.Column(db.Text)
    community_intro = db.Column(db.Text)
    layout_intro = db.Column(db.Text)
    transport_intro = db.Column(db.Text)

    property = db.relationship("Property", back_populates="transaction")

    def to_dict(self) -> dict:
        return {
            "listing_date": self.listing_date,
            "ownership_type": self.ownership_type,
            "property_right": self.property_right,
            "mortgage": self.mortgage,
            "selling_point": self.selling_point,
            "community_intro": self.community_intro,
            "layout_intro": self.layout_intro,
            "transport_intro": self.transport_intro,
        }
