from sqlalchemy import create_engine, text  # 导入 SQLAlchemy 工具，用于连接 MySQL 并包装 SQL 文本。
import pandas as pd  # 导入 pandas，用 DataFrame 承接数据库查询结果并做清洗分析。
import numpy as np  # 导入 numpy，用 np.nan 表示缺失值。

# 创建数据库连接
engine = create_engine('mysql+pymysql://root:1234@localhost:3306/house')  # 创建连接 house 数据库的 SQLAlchemy 引擎。
sql = text('SELECT * FROM house_info')  # 定义查询 house_info 全量数据的 SQL。
connect = engine.connect()  # 建立数据库连接，供 pandas 读取数据。

# 读取数据
df = pd.read_sql(sql, connect)  # 从 MySQL 读取 house_info 表，并加载为 DataFrame。
print(df.head(10))  # 打印前 10 行，初步查看原始数据结构。
print(df.info())  # 打印字段类型和非空数量，了解原始表的数据质量。

# 将缺失值占位符替换为 NaN，并统计每列的缺失值数量
df.replace(to_replace=['', 'None', 'NULL'], value=np.nan, inplace=True)  # 把空字符串、None、NULL 这些占位符统一替换为 NaN。
print(df.isna().sum())  # 统计每一列缺失值数量，观察需要重点清洗的字段。

# 删除不需要的维度（增加了 'jiaotong' 列）
data = df.drop(['link', 'jingdu', 'weidu', 'maidian', 'jieshao', 'huxingjieshao', 'jiaotong'], axis=1)  # 删除链接、坐标和长文本字段，保留用于结构化分析的字段。
print(data.info())  # 打印删除字段后的数据结构。

data2 = data.drop(['region', 'mingcheng', 'quyu', 'mianji', 'price', 'shijian'], axis=1)  # 再去掉连续值和名称字段，只保留类别字段用于查看取值。
for column in data2.columns:  # 遍历所有类别字段。
    print('%s:\n' % column, data2[column].unique())  # 打印每个类别字段的唯一值，判断是否需要归一化。

data['price'] = data['price'].astype(float)  # 将单价字段从字符串转换为浮点数。
print(data['price'].describe())  # 输出单价的描述统计，观察均值、最大值、最小值和异常值。

data['mianji'] = data['mianji'].apply(lambda x: float(x.replace('㎡', '')))  # 去掉面积字段中的“㎡”，并转换为浮点数。
print(data['mianji'].head(10))  # 打印前 10 条面积，确认转换成功。

data['quanshu'].fillna(data['quanshu'].mode().values[0], inplace=True)  # 用交易权属字段的众数填充缺失值。
print(data['quanshu'].isna().sum())  # 检查交易权属字段是否还存在缺失值。


def save_data(x):  # 定义通用截断函数，用于整理抵押和楼层等文本字段。
    if x.strip() == "暂无数据":  # 如果字段明确表示暂无数据，就保留这个标签。
        return "暂无数据"  # 返回暂无数据，避免被截断成不完整文本。
    else:  # 其他正常文本只保留前三个字符。
        return x[:3]  # 返回文本前三个字符，用于压缩分类值。


data['diya'] = data['diya'].apply(lambda x: save_data(x))  # 清洗抵押信息字段，把长文本压缩为主要类别。
print(data['diya'].unique())  # 打印抵押信息清洗后的唯一值。

data['louceng'] = data['louceng'].apply(lambda x: save_data(x))  # 清洗楼层字段，只保留低/中/高楼层等核心分类。
print(data['louceng'].unique())  # 打印楼层清洗后的唯一值。


def orientation(x):  # 定义朝向归一化函数，把复杂朝向压缩成主朝向。
    # 强制转换为字符串并去空格，防止非字符串类型报错
    x = str(x).strip()  # 把输入转为字符串并去除首尾空白。

    if "东南" in x:  # 如果朝向里包含东南。
        if x.count("南") > 1:  # 如果文本里出现多个“南”，说明可能还有南北或西南等复合朝向。
            # 补全因截图截断的代码：移除了"东南"和"西南"之后，判断是否还不包含"南"
            if "南" not in x.replace("东南", "").replace("西南", ""):  # 去掉东南/西南后没有额外南向时，保留东南。
                return "东南"  # 返回东南朝向。
            else:  # 如果还包含额外南向，就归为南。
                return "南"  # 返回南向。
        else:  # 只出现一次南时，说明主要是东南。
            return "东南"  # 返回东南朝向。

    elif "西南" in x:  # 如果朝向里包含西南。
        if x.count("南") > 1:  # 如果还有其他南向信息。
            return "南"  # 归一化为南向。
        else:  # 只有西南这一类复合朝向。
            return "西南"  # 返回西南朝向。

    elif "南" in x:  # 如果包含南但不属于上面的东南/西南特殊情况。
        return "南"  # 返回南向。

    elif "东" in x:  # 如果包含东但没有南。
        return "东"  # 返回东向。

    elif "西" in x:  # 如果包含西但没有南。
        return "西"  # 返回西向。

    else:  # 以上都没有命中时，用北向作为兜底分类。
        return "北"  # 返回北向。


# 应用清洗函数并统计分布
data['chaoxiang'] = data['chaoxiang'].apply(lambda x: orientation(x))  # 对朝向字段逐条执行归一化。
print(data['chaoxiang'].value_counts())  # 统计各朝向类别的数量。

abnorm_data = data[data['price'] < 1000]  # 找出单价低于 1000 的异常房源记录。
print(len(abnorm_data))  # 打印异常低价记录数量。

data1 = data.drop(abnorm_data.index)  # 删除异常低价记录，得到后续分析用数据集。
print(len(data1))  # 打印删除异常值后的数据量。

now = pd.to_datetime('2023-08-21')  # 设置分析基准日期，用来计算挂牌时长。
data1['shijian'] = pd.to_datetime(data1['shijian'])  # 将挂牌时间字段转换为 pandas 日期类型。
long_data = now - data1['shijian']  # 计算每套房源从挂牌到基准日的时间差。
print(long_data)  # 打印挂牌时长结果。

bins1 = pd.to_timedelta([0, 60, 120, 365, 730, 1460, 4000], unit='D')  # 定义挂牌时长分箱边界。
labels1 = ['两个月内', '一个季度', '一年', '两年', '3年', '3年以上']  # 定义挂牌时长分箱标签。
data1['long_datas'] = pd.cut(long_data, bins1, labels=labels1)  # 将挂牌时长切分成可分析的区间标签。
print(data1['long_datas'])  # 打印挂牌时长分箱结果。

data1['year_month'] = data1['shijian'].apply(lambda x: x.strftime("%Y-%m"))  # 从挂牌日期中提取年月，便于按月统计。
print(data1['year_month'])  # 打印年月字段，检查转换结果。

bins = [0, 60, 90, 120, 150, 300, 1000]  # 定义面积区间边界。
labels = ['60平以下', '60-90平', '90-120平', '120-150平', '150-300平', '300平以上']  # 定义面积区间标签。
data1['mianji_data'] = pd.cut(data1['mianji'], bins, labels=labels)  # 将面积切分成面积段。
print(data1['mianji_data'])  # 打印面积分箱结果。

citys = data1['city'].unique()  # 获取数据集中所有城市名称。
for city in citys:  # 按城市逐个处理小区定位。
    data_temp = data1[data1['city'] == city]  # 筛选当前城市的数据。
    regions = data_temp['region'].unique()  # 获取当前城市下所有行政区。
    for region in regions:  # 遍历当前城市下的每个行政区。
        data_mean = data_temp[data_temp['region'] == region]['price'].mean()  # 计算当前城市当前区域的平均单价。
        upper_limit = data_mean + data_mean * 0.40  # 定义高端小区阈值：区域均价上浮 40%。
        lower_limit = data_mean - data_mean * 0.40  # 定义低端小区阈值：区域均价下浮 40%。

        # 拼接后的 .loc 定位赋值代码
        data1.loc[(data1['city'] == city) & (data1['region'] == region) & (data1['price'] > upper_limit), 'dingwei'] = '高端小区'  # 高于上限的房源标记为高端小区。
        data1.loc[(data1['city'] == city) & (data1['region'] == region) & (data1['price'] < lower_limit), 'dingwei'] = '低端小区'  # 低于下限的房源标记为低端小区。
        data1.loc[(data1['city'] == city) & (data1['region'] == region) & (data1['price'].between(lower_limit, upper_limit)), 'dingwei'] = '中端小区'  # 在上下限之间的房源标记为中端小区。

# 统计清洗定位后的数据分布
print(data1['dingwei'].value_counts())  # 打印高端/中端/低端小区的数量分布。
