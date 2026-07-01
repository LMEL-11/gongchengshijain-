import requests  # 导入 requests，用来请求城市和区域入口页面。
from lxml import etree  # 导入 lxml.etree，用 XPath 解析网页 HTML。
import pandas as pd  # 导入 pandas，用来整理并保存城市、地区、链接数据。

#城市、地区、连接保存到region_link.csv文件中
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}  # 设置请求头，模拟浏览器访问目标站点。

url = 'http://node4:8000/'  # 设置城市列表入口页地址。
html = requests.get(url, headers=headers).text  # 请求入口页并获取 HTML 文本。
print(html)  # 打印 HTML，方便确认页面是否请求成功。

#通过XPath提取各城市数据
html_text = etree.HTML(html)  # 把 HTML 字符串解析成可执行 XPath 的文档对象。
city_nodes = html_text.xpath('//div[@class="city_list_tit c_b"]')  # 提取每个城市分组标题节点。
for item in city_nodes:  # 遍历每个城市分组，先调试查看其中包含的区域链接。
    # print(item.text)  # 调试用：打印当前城市名称。
    # 提取各地区名称及连接
    region_nodes = item.xpath('.//a')  # 在当前城市节点下查找所有区域链接。
    for region in region_nodes:  # 遍历当前城市下的区域链接节点。
        print(region.text, region.get('href'))  # 打印区域名称和对应链接，确认 XPath 提取结果。

city = []  # 保存每条区域链接所属的城市名称。
region = []  # 保存每条区域链接对应的地区名称。
region_link = []  # 保存每条区域链接的 URL。

for item in city_nodes:  # 再次遍历城市节点，正式组装结构化数据。
    region_nodes = html_text.xpath('//div[contains(text(),"%s")]/following-sibling::ul/li/a' % item.text)  # 根据城市标题找到它后面的区域列表链接。
    for region_node in region_nodes:  # 遍历该城市下所有区域链接。
        city.append(str(item.text))  # 记录当前区域所属城市。
        region.append(str(region_node.text))  # 记录当前区域名称。
        region_link.append(str(region_node.get('href')))  # 记录当前区域列表页链接。

region_info = pd.DataFrame({'城市': city, '地区': region, '链接': region_link})  # 把城市、地区、链接三列整理成 DataFrame。
print(region_info.head())  # 打印前几行，检查生成的区域链接表是否正确。

#在这之前，要先创建一个目录，cd /home   mkdir data
region_info.to_csv('/home/data/region_link.csv', index=False, encoding='utf-8')  # 将区域链接表保存到 /home/data/region_link.csv，供后续脚本读取。
