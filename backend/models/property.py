"""房源 Property (listing) model."""  # 保留字符串内容，作为说明文本或页面展示文案。
from datetime import datetime  # 从 datetime 导入 datetime，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。


class Property(db.Model):  # 定义 Property(db.Model 类，封装对应的数据结构或业务行为。
    """表示单套房源的价格、面积、楼层、坐标和来源信息。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    __tablename__ = "properties"  # 设置 __tablename__ 的值，供后续业务判断、查询或响应组装使用。

    id = db.Column(db.Integer, primary_key=True)  # 设置 id 的值，供后续业务判断、查询或响应组装使用。
    district_id = db.Column(  # 设置 district_id 的值，供后续业务判断、查询或响应组装使用。
        db.Integer, db.ForeignKey("districts.id"), nullable=False, index=True  # 设置 db.Integer, db.ForeignKey("districts.id"), nullable 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。

    title = db.Column(db.String(200), nullable=False)  # 设置 title 的值，供后续业务判断、查询或响应组装使用。
    total_price = db.Column(db.Float)  # 设置 total_price 的值，供后续业务判断、查询或响应组装使用。
    unit_price = db.Column(db.Float, index=True)  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
    area = db.Column(db.Float)  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
    rooms = db.Column(db.Integer, default=0)  # 设置 rooms 的值，供后续业务判断、查询或响应组装使用。
    halls = db.Column(db.Integer, default=0)  # 设置 halls 的值，供后续业务判断、查询或响应组装使用。
    floor = db.Column(db.Integer)  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
    total_floors = db.Column(db.Integer)  # 设置 total_floors 的值，供后续业务判断、查询或响应组装使用。
    build_year = db.Column(db.Integer)  # 设置 build_year 的值，供后续业务判断、查询或响应组装使用。
    orientation = db.Column(db.String(20))  # 设置 orientation 的值，供后续业务判断、查询或响应组装使用。
    decoration = db.Column(db.String(20))  # 设置 decoration 的值，供后续业务判断、查询或响应组装使用。
    has_elevator = db.Column(db.Boolean, default=False)  # 设置 has_elevator 的值，供后续业务判断、查询或响应组装使用。
    listing_type = db.Column(db.String(20), default="二手房")  # 设置 listing_type 的值，供后续业务判断、查询或响应组装使用。

    lng = db.Column(db.Float)  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
    lat = db.Column(db.Float)  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。

    source = db.Column(db.String(50))  # 设置 source 的值，供后续业务判断、查询或响应组装使用。
    source_url = db.Column(db.String(500))  # 设置 source_url 的值，供后续业务判断、查询或响应组装使用。
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 设置 created_at 的值，供后续业务判断、查询或响应组装使用。

    district = db.relationship("District", back_populates="properties")  # 设置 district 的值，供后续业务判断、查询或响应组装使用。
    transaction = db.relationship(  # 设置 transaction 的值，供后续业务判断、查询或响应组装使用。
        "PropertyTransaction",  # 保留字符串内容，作为说明文本或页面展示文案。
        back_populates="property",  # 设置 back_populates 的值，供后续业务判断、查询或响应组装使用。
        uselist=False,  # 设置 uselist 的值，供后续业务判断、查询或响应组装使用。
        cascade="all, delete-orphan",  # 设置 cascade 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。

    def layout(self) -> str:  # 定义 layout 函数，集中处理这一段业务逻辑。
        """Human-readable layout, e.g. "3室2厅"."""  # 保留字符串内容，作为说明文本或页面展示文案。
        return f"{self.rooms or 0}室{self.halls or 0}厅"  # 返回处理后的结果给调用方继续使用。

    def to_dict(self, detail: bool = False) -> dict:  # 定义 to_dict 函数，集中处理这一段业务逻辑。
        """将当前模型实例转换为接口可返回的字典结构。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        data = {  # 设置 data 的值，供后续业务判断、查询或响应组装使用。
            "id": self.id,  # 保留字符串内容，作为说明文本或页面展示文案。
            "district_id": self.district_id,  # 保留字符串内容，作为说明文本或页面展示文案。
            "district_name": self.district.name if self.district else None,  # 保留字符串内容，作为说明文本或页面展示文案。
            "city_name": self.district.city.name if self.district and self.district.city else None,  # 保留字符串内容，作为说明文本或页面展示文案。
            "title": self.title,  # 保留字符串内容，作为说明文本或页面展示文案。
            "total_price": self.total_price,  # 保留字符串内容，作为说明文本或页面展示文案。
            "unit_price": self.unit_price,  # 保留字符串内容，作为说明文本或页面展示文案。
            "area": self.area,  # 保留字符串内容，作为说明文本或页面展示文案。
            "layout": self.layout(),  # 保留字符串内容，作为说明文本或页面展示文案。
            "rooms": self.rooms,  # 保留字符串内容，作为说明文本或页面展示文案。
            "halls": self.halls,  # 保留字符串内容，作为说明文本或页面展示文案。
            "listing_type": self.listing_type,  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
        if detail:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            data.update(  # 执行当前代码行对应的业务处理步骤。
                {  # 执行当前代码行对应的业务处理步骤。
                    "floor": self.floor,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "total_floors": self.total_floors,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "build_year": self.build_year,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "orientation": self.orientation,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "decoration": self.decoration,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "has_elevator": self.has_elevator,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "lng": self.lng,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "lat": self.lat,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "source": self.source,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "source_url": self.source_url,  # 保留字符串内容，作为说明文本或页面展示文案。
                    "created_at": self.created_at.isoformat() if self.created_at else None,  # 保留字符串内容，作为说明文本或页面展示文案。
                }  # 结束当前多行数据结构或函数调用。
            )  # 结束当前多行数据结构或函数调用。
        return data  # 返回处理后的结果给调用方继续使用。
