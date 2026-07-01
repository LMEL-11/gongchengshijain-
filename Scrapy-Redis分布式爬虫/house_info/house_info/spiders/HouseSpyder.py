import scrapy  # 导入 Scrapy 框架，用于构造请求并解析响应。
from scrapy_redis.spiders import RedisSpider  # 导入 Scrapy-Redis 的分布式爬虫基类。
from house_info.items import HouseInfoItem  # 导入房源 Item，统一保存每套房源的字段。
from house_info.get_url import getdata  # 导入读取 house_link.csv 的函数，获取待爬取房源链接。
import re  # 导入正则模块，用于从页面脚本里提取经纬度。
import warnings  # 导入 warnings 模块，用于关闭无关警告。

warnings.filterwarnings('ignore')  # 忽略运行中的警告输出，让爬虫日志更干净。


class HousespyderSpider(RedisSpider):  # 定义房源详情爬虫类，继承 RedisSpider 以支持分布式调度。
    name = "HouseSpyder"  # 设置爬虫名称，Redis 队列和运行命令会使用这个名称。
    allowed_domains = ["node4"]  # 限制爬虫只访问 node4 域名，避免跑到其他站点。
    #start_urls = ["http://node4/"]  # 普通 Scrapy 起始链接示例；当前爬虫改为从 CSV 生成请求。

    def start_requests(self):  # 重写起始请求方法，从 CSV 房源链接表生成详情页请求。
        mydata = getdata()  # 读取 /home/data/house_link.csv，得到城市、地区、详情页链接。
        for i in range(len(mydata)):  # 遍历每一条待爬取房源链接。
            item = HouseInfoItem()  # 创建一个空 Item，用来在请求和解析之间传递基础字段。
            item['city'] = mydata['城市'][i]  # 将 CSV 中的城市写入 Item。
            item['region'] = mydata['地区'][i]  # 将 CSV 中的地区写入 Item。
            item['link'] = mydata['链接'][i]  # 将 CSV 中的详情页链接写入 Item。
            yield scrapy.Request(url=item['link'], callback=self.parse, meta={'item': item})  # 发起详情页请求，并通过 meta 把 Item 传给 parse。

    def parse(self, response):  # 解析单个房源详情页，提取结构化字段。
        item = response.meta['item']  # 取回 start_requests 中传入的基础 Item。
        name_node = response.xpath('//div[@class="communityName"]//a[@class="info"]/text()').getall()  # 提取小区名称。
        load_node = response.xpath('//div[@class="areaName"]//a[@class="supplement"]/text()')  # 提取页面中的商圈/区域名称。
        price_node = response.xpath('//span[@class="unitPriceValue"]//text()').getall()  # 提取房源单价文本。
        info_nodes = response.xpath('//div[@class="base"]//li//text()').getall()  # 提取基础属性列表，如户型、楼层、面积、朝向等。
        trade_nodes = response.xpath('//div[@class="transaction"]//div[@class="content"]/ul/li/span/text()').getall()  # 提取交易属性列表，如挂牌时间、权属、产权、抵押等。
        base_nodes = response.xpath('//div[@class="baseattribute clear"]//div[@class="content"]/text()').getall()  # 提取卖点、小区介绍、户型介绍和交通介绍文本。
        pattern = re.compile('BMap.Point' + '(.*?)' + ';', re.S)  # 构造正则，定位页面脚本中的百度地图坐标。
        pos = pattern.findall(response.text)[0]  # 提取 BMap.Point(...) 中的经纬度参数字符串。
        item['mingcheng'] = str(name_node[0])  # 保存小区名称。
        item['quyu'] = str(load_node[0])  # 保存房源所在商圈/区域。
        item['huxing'] = str(info_nodes[1])  # 保存户型字段。
        item['louceng'] = str(info_nodes[3])  # 保存楼层字段。
        item['mianji'] = str(info_nodes[5])  # 保存建筑面积字段。
        item['huxingjiegou'] = str(info_nodes[7])  # 保存户型结构字段。
        item['chaoxiang'] = str(info_nodes[13])  # 保存房屋朝向字段。
        item['jianzhujiegou'] = str(info_nodes[15])  # 保存建筑结构字段。
        item['zhuangxiu'] = str(info_nodes[17])  # 保存装修情况字段。
        item['tihu'] = str(info_nodes[19])  # 保存梯户比例字段。
        item['shijian'] = str(trade_nodes[1])  # 保存挂牌时间字段。
        item['quanshu'] = str(trade_nodes[3])  # 保存交易权属字段。
        item['chanquan'] = str(trade_nodes[11])  # 保存产权所属字段。
        item['diya'] = str(trade_nodes[13]).replace(' ', '').replace('\n', '')  # 保存抵押信息，并清理空格和换行。
        item['price'] = str(price_node[0])  # 保存房源单价。
        item['jingdu'] = eval(pos)[0]  # 将坐标字符串转为元组后保存经度。
        item['weidu'] = eval(pos)[1]  # 将坐标字符串转为元组后保存纬度。
        item['maidian'] = base_nodes[0].replace(' ', '').replace('\n', '')  # 保存核心卖点，并清理空白字符。
        item['jieshao'] = base_nodes[1].replace(' ', '').replace('\n', '')  # 保存小区介绍，并清理空白字符。
        item['huxingjieshao'] = base_nodes[2].replace(' ', '').replace('\n', '')  # 保存户型介绍，并清理空白字符。
        item['jiaotong'] = base_nodes[3].replace(' ', '').replace('\n', '')  # 保存交通出行介绍，并清理空白字符。
        yield item  # 将完整房源 Item 交给 Scrapy pipeline；当前配置会写入 Redis 队列。
