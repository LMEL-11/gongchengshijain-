"""抓取条目定义。字段与后端 `models/property.py` 的 Property 一一对应，
另含 city / district 用于在管道里 get_or_create 城市与行政区。"""
import scrapy  # 导入 scrapy 模块，为当前文件提供所需功能。


class HousingItem(scrapy.Item):  # 定义 HousingItem(scrapy.Item 类，封装对应的数据结构或业务行为。
    """定义 Scrapy 爬取房源时在管道间传递的数据字段。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    # 归属（用于解析出 Property 的外键）
    city = scrapy.Field()  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
    district = scrapy.Field()  # 设置 district 的值，供后续业务判断、查询或响应组装使用。

    # Property 字段
    title = scrapy.Field()  # 设置 title 的值，供后续业务判断、查询或响应组装使用。
    total_price = scrapy.Field()  # 设置 total_price 的值，供后续业务判断、查询或响应组装使用。
    unit_price = scrapy.Field()  # 设置 unit_price 的值，供后续业务判断、查询或响应组装使用。
    area = scrapy.Field()  # 设置 area 的值，供后续业务判断、查询或响应组装使用。
    rooms = scrapy.Field()  # 设置 rooms 的值，供后续业务判断、查询或响应组装使用。
    halls = scrapy.Field()  # 设置 halls 的值，供后续业务判断、查询或响应组装使用。
    floor = scrapy.Field()  # 设置 floor 的值，供后续业务判断、查询或响应组装使用。
    total_floors = scrapy.Field()  # 设置 total_floors 的值，供后续业务判断、查询或响应组装使用。
    build_year = scrapy.Field()  # 设置 build_year 的值，供后续业务判断、查询或响应组装使用。
    orientation = scrapy.Field()  # 设置 orientation 的值，供后续业务判断、查询或响应组装使用。
    decoration = scrapy.Field()  # 设置 decoration 的值，供后续业务判断、查询或响应组装使用。
    has_elevator = scrapy.Field()  # 设置 has_elevator 的值，供后续业务判断、查询或响应组装使用。
    listing_type = scrapy.Field()  # 设置 listing_type 的值，供后续业务判断、查询或响应组装使用。
    lng = scrapy.Field()  # 设置 lng 的值，供后续业务判断、查询或响应组装使用。
    lat = scrapy.Field()  # 设置 lat 的值，供后续业务判断、查询或响应组装使用。
    source = scrapy.Field()  # 设置 source 的值，供后续业务判断、查询或响应组装使用。
    source_url = scrapy.Field()  # 设置 source_url 的值，供后续业务判断、查询或响应组装使用。
