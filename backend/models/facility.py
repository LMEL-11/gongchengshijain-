"""周边配套设施 Facility model（学校、医院、地铁等）。"""
from extensions import db  # 逐行注释：导入本行所需的模块或对象。

# 设施类别 -> 中文名（前端图例使用）
FACILITY_CATEGORIES = {  # 逐行注释：赋值或更新当前变量/字段。
    "school": "学校",  # 逐行注释：设置当前数据项或参数。
    "hospital": "医院",  # 逐行注释：设置当前数据项或参数。
    "subway": "地铁",  # 逐行注释：设置当前数据项或参数。
    "transport": "交通",  # 逐行注释：设置当前数据项或参数。
    "mall": "商场",  # 逐行注释：设置当前数据项或参数。
    "park": "公园",  # 逐行注释：设置当前数据项或参数。
}  # 逐行注释：结束当前数据结构或调用块。


class Facility(db.Model):  # 逐行注释：声明类并定义相关数据或行为。
    """表示区域周边配套设施及其类型、位置和评分信息。"""
    __tablename__ = "facilities"  # 逐行注释：赋值或更新当前变量/字段。

    id = db.Column(db.Integer, primary_key=True)  # 逐行注释：赋值或更新当前变量/字段。
    district_id = db.Column(  # 逐行注释：赋值或更新当前变量/字段。
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True  # 逐行注释：赋值或更新当前变量/字段。
    )  # 逐行注释：结束当前数据结构或调用块。
    name = db.Column(db.String(100), nullable=False)  # 逐行注释：赋值或更新当前变量/字段。
    category = db.Column(db.String(20), nullable=False)  # school/hospital/subway/...
    lng = db.Column(db.Float)  # 逐行注释：赋值或更新当前变量/字段。
    lat = db.Column(db.Float)  # 逐行注释：赋值或更新当前变量/字段。

    district = db.relationship("District", back_populates="facilities")  # 逐行注释：赋值或更新当前变量/字段。

    def to_dict(self) -> dict:  # 逐行注释：声明函数或方法入口。
        """将当前模型实例转换为接口可返回的字典结构。"""
        return {  # 逐行注释：返回当前逻辑的处理结果。
            "id": self.id,  # 逐行注释：设置当前数据项或参数。
            "district_id": self.district_id,  # 逐行注释：设置当前数据项或参数。
            "name": self.name,  # 逐行注释：设置当前数据项或参数。
            "category": self.category,  # 逐行注释：设置当前数据项或参数。
            "category_label": FACILITY_CATEGORIES.get(self.category, self.category),  # 逐行注释：设置当前数据项或参数。
            "lng": self.lng,  # 逐行注释：设置当前数据项或参数。
            "lat": self.lat,  # 逐行注释：设置当前数据项或参数。
        }  # 逐行注释：结束当前数据结构或调用块。
