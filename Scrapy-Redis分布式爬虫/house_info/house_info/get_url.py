def getdata():  # 定义读取房源链接数据的函数，供爬虫 start_requests 调用。
    import pandas as pd  # 在函数内部导入 pandas，用来读取 CSV 文件。
    house_link = pd.read_csv('/home/data/house_link.csv', encoding='utf-8')  # 读取上游脚本生成的房源详情链接表。
    return house_link  # 返回 DataFrame，里面包含城市、地区、详情页链接三列。
