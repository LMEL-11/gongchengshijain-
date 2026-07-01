# Define here the models for your scraped items  # 说明本文件用于定义 Scrapy 爬取结果的数据结构。
#  # 空注释行，用于分隔说明文字。
# See documentation in:  # 提示可以查看 Scrapy 官方文档了解 Item 的用法。
# https://docs.scrapy.org/en/latest/topics/items.html  # Scrapy Item 官方文档地址。

import scrapy  # 导入 Scrapy，使用 scrapy.Item 和 scrapy.Field 定义爬取字段。


class HouseInfoItem(scrapy.Item):  # 定义房源详情 Item，统一描述一套房源需要保存哪些字段。
    # define the fields for your item here like:  # Scrapy 模板提示：这里用于声明字段。
    # name = scrapy.Field()  # Scrapy 模板示例：可以像这样定义字段。
    city = scrapy.Field()  # 城市
    region = scrapy.Field()  # 地区
    link = scrapy.Field()  # 房源链接
    mingcheng = scrapy.Field()  # 小区名称
    quyu = scrapy.Field()  # 所在区域
    huxing = scrapy.Field()  # 房屋户型
    louceng = scrapy.Field()  # 所在楼层
    mianji = scrapy.Field()  # 建筑面积
    huxingjiegou = scrapy.Field()  # 户型结构
    chaoxiang = scrapy.Field()  # 房屋朝向
    jianzhujiegou = scrapy.Field()  # 建筑结构
    zhuangxiu = scrapy.Field()  # 装修情况
    tihu = scrapy.Field()  # 梯户比例
    shijian = scrapy.Field()  # 挂牌时间
    quanshu = scrapy.Field()  # 交易权属
    chanquan = scrapy.Field()  # 产权所属
    diya = scrapy.Field()  # 抵押信息
    price = scrapy.Field()  # 房价
    jingdu = scrapy.Field()  # 经度
    weidu = scrapy.Field()  # 纬度
    maidian = scrapy.Field()  # 核心卖点
    jieshao = scrapy.Field()  # 小区介绍
    huxingjieshao = scrapy.Field()  # 户型介绍
    jiaotong = scrapy.Field()  # 交通出行
    pass  # 类体结束占位；字段已经在上方声明完成。
