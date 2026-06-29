"""抓取条目定义。字段与后端 `models/property.py` 的 Property 一一对应，
另含 city / district 用于在管道里 get_or_create 城市与行政区。"""
import scrapy  # 导入本行所需的模块或对象。


class HousingItem(scrapy.Item):  # 声明类并定义相关数据或行为。
    """定义 Scrapy 爬取房源时在管道间传递的数据字段。"""
    # 归属（用于解析出 Property 的外键）
    city = scrapy.Field()          # 城市中文名，如 "北京"
    district = scrapy.Field()      # 行政区名，如 "朝阳"

    # Property 字段
    title = scrapy.Field()         # 标题（链家 h1，含小区+卖点）
    total_price = scrapy.Field()   # 总价（万元）
    unit_price = scrapy.Field()    # 单价（元/㎡）
    area = scrapy.Field()          # 建筑面积（㎡）
    rooms = scrapy.Field()         # 室
    halls = scrapy.Field()         # 厅
    floor = scrapy.Field()         # 所在楼层（精确层数，链家多为"低/中/高"，常为空）
    total_floors = scrapy.Field()  # 总楼层
    build_year = scrapy.Field()    # 建成年份
    orientation = scrapy.Field()   # 朝向，如 "南 北"
    decoration = scrapy.Field()    # 装修，如 "精装"
    has_elevator = scrapy.Field()  # 是否有电梯
    listing_type = scrapy.Field()  # "二手房"
    lng = scrapy.Field()           # 经度
    lat = scrapy.Field()           # 纬度
    source = scrapy.Field()        # "lianjia"
    source_url = scrapy.Field()    # 详情页 URL（去重键）
