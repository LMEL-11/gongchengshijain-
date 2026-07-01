# Define your item pipelines here  # 说明本文件用于定义 Scrapy Item Pipeline。
#  # 空注释行，用于分隔模板说明。
# Don't forget to add your pipeline to the ITEM_PIPELINES setting  # 提醒自定义 pipeline 需要在 settings.py 中启用。
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html  # Scrapy Pipeline 官方文档地址。


# useful for handling different item types with a single interface  # 模板说明：ItemAdapter 可统一处理不同类型的 item。
from itemadapter import ItemAdapter  # 导入 ItemAdapter；当前代码暂未使用，保留为后续扩展。


class HouseInfoPipeline:  # 定义项目自己的 Pipeline 类。
    def process_item(self, item, spider):  # Scrapy 每产出一个 item 都会调用该方法。
        return item  # 原样返回 item，不做额外清洗；当前实际写入 Redis 由 scrapy_redis 的 RedisPipeline 完成。
