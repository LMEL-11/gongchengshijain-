"""行政区 District model."""  # 保留字符串内容，作为说明文本或页面展示文案。
from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。


class District(db.Model):  # 定义 District(db.Model 类，封装对应的数据结构或业务行为。
    """表示城市下的区域信息、地图位置和房源关联。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    __tablename__ = "districts"  # 设置 __tablename__ 的值，供后续业务判断、查询或响应组装使用。

    id = db.Column(db.Integer, primary_key=True)  # 设置 id 的值，供后续业务判断、查询或响应组装使用。
    city_id = db.Column(  # 设置 city_id 的值，供后续业务判断、查询或响应组装使用。
        db.Integer, db.ForeignKey("cities.id"), nullable=False, index=True  # 设置 db.Integer, db.ForeignKey("cities.id"), nullable 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。
    name = db.Column(db.String(50), nullable=False)  # 设置 name 的值，供后续业务判断、查询或响应组装使用。
    lng = db.Column(db.Float)  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
    lat = db.Column(db.Float)  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。
    # Stored grid position (col, row) used to lay out the 3D city map.
    grid_x = db.Column(db.Integer, default=0)  # 设置 grid_x 的值，供后续业务判断、查询或响应组装使用。
    grid_y = db.Column(db.Integer, default=0)  # 设置 grid_y 的值，供后续业务判断、查询或响应组装使用。

    city = db.relationship("City", back_populates="districts")  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
    properties = db.relationship(  # 设置 properties 的值，供后续业务判断、查询或响应组装使用。
        "Property", back_populates="district", cascade="all, delete-orphan"  # 设置 "Property", back_populates 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。
    facilities = db.relationship(  # 设置 facilities 的值，供后续业务判断、查询或响应组装使用。
        "Facility", back_populates="district", cascade="all, delete-orphan"  # 设置 "Facility", back_populates 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。

    def avg_unit_price(self) -> float:  # 定义 avg_unit_price 函数，集中处理这一段业务逻辑。
        """Average listing price per square metre (元/㎡)."""  # 保留字符串内容，作为说明文本或页面展示文案。
        prices = [p.unit_price for p in self.properties if p.unit_price]  # 设置 prices 的值，供后续业务判断、查询或响应组装使用。
        return round(sum(prices) / len(prices)) if prices else 0  # 返回处理后的结果给调用方继续使用。

    def to_dict(self, with_stats: bool = True) -> dict:  # 定义 to_dict 函数，集中处理这一段业务逻辑。
        """将当前模型实例转换为接口可返回的字典结构。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        data = {  # 设置 data 的值，供后续业务判断、查询或响应组装使用。
            "id": self.id,  # 保留字符串内容，作为说明文本或页面展示文案。
            "city_id": self.city_id,  # 保留字符串内容，作为说明文本或页面展示文案。
            "name": self.name,  # 保留字符串内容，作为说明文本或页面展示文案。
            "lng": self.lng,  # 保留字符串内容，作为说明文本或页面展示文案。
            "lat": self.lat,  # 保留字符串内容，作为说明文本或页面展示文案。
            "grid_x": self.grid_x,  # 保留字符串内容，作为说明文本或页面展示文案。
            "grid_y": self.grid_y,  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
        if with_stats:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            data["avg_unit_price"] = self.avg_unit_price()  # 设置 data["avg_unit_price" 的值，供后续业务判断、查询或响应组装使用。
            data["property_count"] = len(self.properties)  # 设置 data["property_count" 的值，供后续业务判断、查询或响应组装使用。
        return data  # 返回处理后的结果给调用方继续使用。
