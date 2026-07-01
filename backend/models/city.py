"""城市 City model."""  # 保留字符串内容，作为说明文本或页面展示文案。
from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。


class City(db.Model):  # 定义 City(db.Model 类，封装对应的数据结构或业务行为。
    """表示城市基础信息及其下属行政区关系。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    __tablename__ = "cities"  # 设置 __tablename__ 的值，供后续业务判断、查询或响应组装使用。

    id = db.Column(db.Integer, primary_key=True)  # 设置 id 的值，供后续业务判断、查询或响应组装使用。
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)  # 设置 name 的值，供后续业务判断、查询或响应组装使用。
    name_en = db.Column(db.String(50))  # 设置 name_en 的值，供后续业务判断、查询或响应组装使用。
    province = db.Column(db.String(50))  # 设置 province 的值，供后续业务判断、查询或响应组装使用。
    lng = db.Column(db.Float)  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
    lat = db.Column(db.Float)  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。

    districts = db.relationship(  # 设置 districts 的值，供后续业务判断、查询或响应组装使用。
        "District", back_populates="city", cascade="all, delete-orphan"  # 设置 "District", back_populates 的值，供后续业务判断、查询或响应组装使用。
    )  # 结束当前多行数据结构或函数调用。

    def to_dict(self) -> dict:  # 定义 to_dict 函数，集中处理这一段业务逻辑。
        """将当前模型实例转换为接口可返回的字典结构。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return {  # 返回处理后的结果给调用方继续使用。
            "id": self.id,  # 保留字符串内容，作为说明文本或页面展示文案。
            "name": self.name,  # 保留字符串内容，作为说明文本或页面展示文案。
            "name_en": self.name_en,  # 保留字符串内容，作为说明文本或页面展示文案。
            "province": self.province,  # 保留字符串内容，作为说明文本或页面展示文案。
            "lng": self.lng,  # 保留字符串内容，作为说明文本或页面展示文案。
            "lat": self.lat,  # 保留字符串内容，作为说明文本或页面展示文案。
            "district_count": len(self.districts),  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
