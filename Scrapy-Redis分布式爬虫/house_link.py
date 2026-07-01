import requests  # 导入 requests，用来请求区域列表页和房源列表页。
from lxml import etree  # 导入 lxml.etree，用 XPath 从网页中提取页数和房源链接。
import pandas as pd  # 导入 pandas，用来读取区域链接 CSV 并保存房源链接 CSV。
import re  # 导入正则模块，用来从分页文本里提取总页数。

region_link = pd.read_csv('/home/data/region_link.csv', encoding='utf-8')  # 读取上一步生成的城市/地区/区域链接表。
print(region_link.head())  # 打印前几行，确认 CSV 已正确读取。

url = region_link['链接'][0]  # 取第一个区域链接，用来测试分页结构。
html = requests.get(url).text  # 请求该区域列表页 HTML。
html_text = etree.HTML(html)  # 把 HTML 文本解析成 XPath 文档对象。
page_nodes = html_text.xpath('//div[@class="pagination"]//span[@class="current"]/text()')  # 提取分页组件中的当前页描述文本。
page_str = page_nodes[0].replace('\n', '').replace(' ', '')  # 去掉分页文本中的换行和空格。
print(page_str)  # 打印分页文本，检查是否包含“共X页”。

#获取总页数
pattern = re.compile("共(.*?)页", re.S)  # 构造正则，用来匹配“共”和“页”之间的总页数。
page_num = int(pattern.findall(page_str)[0])  # 从分页文本中提取总页数并转成整数。
print(page_num)  # 打印第一个区域的总页数。

pages = []  # 保存每个区域链接对应的总页数。
for i in range(len(region_link)):  # 遍历所有城市区域链接。
    url = region_link['链接'][i]  # 取当前区域列表页链接。
    html = requests.get(url).text  # 请求当前区域列表页 HTML。
    html_text = etree.HTML(html)  # 解析当前区域列表页 HTML。
    page_nodes = html_text.xpath('//div[@class="pagination"]//span[@class="current"]/text()')  # 提取当前区域的分页描述文本。
    page_str = page_nodes[0].replace('\n', '').replace(' ', '')  # 清理分页文本中的空白字符。
    pattern = re.compile("共(.*?)页", re.S)  # 构造提取总页数的正则表达式。
    page_num = int(pattern.findall(page_str)[0])  # 提取当前区域总页数并转成整数。
    pages.append(page_num)  # 把当前区域总页数加入列表。
print(pages)  # 打印所有区域页数，检查采集结果。

#将总页数加入DataFrame中
region_link['总页数'] = pages  # 给区域链接表新增“总页数”列。
print(region_link.head())  # 打印包含总页数的新表头部数据。

#只爬取前20页
get_pages = 20  # 设置每个区域最多只生成前 20 页的列表页链接。
house_info = pd.DataFrame()  # 创建空 DataFrame，用来累计所有房源列表页链接。
for i in range(len(region_link)):  # 遍历每个城市区域。
    city = []  # 临时保存当前区域生成的城市列。
    region = []  # 临时保存当前区域生成的地区列。
    house_url = []  # 临时保存当前区域生成的房源列表页链接。
    for j in range(region_link['总页数'][i]):  # 按当前区域总页数生成分页链接。
        if j < get_pages:  # 只处理前 get_pages 页。
            city.append(region_link['城市'][i])  # 保存当前分页链接所属城市。
            region.append(region_link['地区'][i])  # 保存当前分页链接所属地区。
            url = region_link['链接'][i][:-1] + str(j + 1)  # 把区域基础链接替换成第 j+1 页链接。
            house_url.append(url)  # 保存生成的房源列表页链接。
        else:  # 超过限定页数后停止当前区域分页生成。
            break  # 跳出当前区域的分页循环。
    house_info_temp = pd.DataFrame({'城市': city, '地区': region, '链接': house_url})  # 把当前区域分页链接整理成临时 DataFrame。
    house_info = pd.concat([house_info, house_info_temp])  # 将当前区域分页链接合并到总表中。
print(house_info.head())  # 打印房源列表页链接总表前几行。

#获取单页中所有房源的链接
house_info.reset_index(drop=True, inplace=True)  # 重置索引，方便后面按整数位置访问每一行。
url = house_info['链接'][0]  # 取第一个房源列表页链接做测试。
html = requests.get(url).text  # 请求该列表页 HTML。
html_text = etree.HTML(html)  # 解析该列表页 HTML。
page_nodes = html_text.xpath('//div[@class="info clear"]//div[@class="title"]//a')  # 提取该列表页中的房源详情链接节点。
for item in page_nodes:  # 遍历测试页里的房源链接节点。
    print(item.get('href'))  # 打印房源详情页链接，确认 XPath 结果。

#通过循环爬取所有房源的链接
city = []  # 保存每套房源所属城市。
region = []  # 保存每套房源所属地区。
house_url = []  # 保存每套房源详情页链接。
for i in range(len(house_info)):  # 遍历所有房源列表页。
    print('正在获取%s市%s的所有房源链接' % (house_info['城市'][i], house_info['地区'][i]))  # 打印当前正在处理的城市和地区。
    url = house_info['链接'][i]  # 取当前房源列表页链接。
    html = requests.get(url).text  # 请求当前列表页 HTML。
    html_text = etree.HTML(html)  # 解析当前列表页 HTML。
    page_nodes = html_text.xpath('//div[@class="info clear"]//div[@class="title"]//a')  # 提取当前列表页所有房源详情链接节点。
    for item in page_nodes:  # 遍历当前列表页中的每个房源链接。
        city.append(house_info['城市'][i])  # 记录该房源所属城市。
        region.append(house_info['地区'][i])  # 记录该房源所属地区。
        house_url.append(str(item.get('href')))  # 记录该房源详情页 URL。
print(len(city), len(region), len(house_url))  # 打印三列长度，检查数据是否对齐。

#保存到DataFrame中
house_link_info = pd.DataFrame({'城市': city, '地区': region, '链接': house_url})  # 将房源详情链接整理成 DataFrame。
house_link_info['链接'] = house_link_info['链接'].map(lambda x: x.replace('details', 'details/'))  # 规范详情页链接格式，补齐 details 后的斜杠。
print(house_link_info.head())  # 打印前几行，确认房源链接表生成正确。

#保存数据
house_link_info.to_csv('/home/data/house_link.csv', index=False, encoding='utf-8')  # 保存房源详情链接表，供 Scrapy 爬虫读取。
