import redis  # 导入 Redis 客户端，用来从 Scrapy-Redis 的结果队列中读取爬取到的房源数据。
import pandas as pd  # 导入 pandas，用 DataFrame 承接单条房源数据并写入 MySQL。
from sqlalchemy import create_engine, text  # 导入 SQLAlchemy 建库连接工具；text 当前保留备用。
import time  # 导入时间模块，用于队列暂时为空时暂停等待。

# 连接到Redis
redis_connect = redis.Redis(host='localhost', port=6379, db=0)  # 创建 Redis 连接对象，连接本机 6379 端口的 0 号库。
# 连接到MySQL
engine = create_engine('mysql+pymysql://root:1234@localhost:3306/house?charset=utf8mb4')  # 创建 MySQL 写入引擎，目标库是 house。
#data_one = redis_connect.lrange('HouseSpyder:items',0,0)  # 示例：从 Redis 队列头部取一条数据但不删除。
#print(eval(data_one[0]))  # 示例：把 Redis 中的字节内容转成 Python 对象后打印。

#house_data=pd.DataFrame(eval(data_one[0]),index=[0])  # 示例：把单条房源字典转换成一行 DataFrame。
#house_data.to_sql(name='house_info',con=engine,index=False,if_exists='append')  # 示例：把这行数据追加写入 house_info 表。


#del_data=redis_connect.lpop('HouseSpyder:items')  # 示例：从 Redis 队列左侧弹出一条数据，实现“读取后删除”。
i = 1  # 初始化已保存数据计数器，用于打印入库进度。
while True:  # 持续监听 Redis 队列，直到队列在等待后仍为空才退出。
    data_one = redis_connect.lrange('HouseSpyder:items', 0, 0)  # 查看队列第一条爬虫结果，但暂时不删除。
    if len(data_one) == 0:  # 判断当前 Redis 队列中是否没有待保存数据。
        print('waitting for 60s')  # 提示当前队列为空，将等待爬虫继续生产数据。
        time.sleep(60)  # 暂停 60 秒，给分布式爬虫继续写入 Redis 的时间。
        data_one = redis_connect.lrange('HouseSpyder:items', 0, 0)  # 等待结束后再次检查队列头部。
        if len(data_one) == 0:  # 如果二次检查仍然没有数据，认为保存任务可以结束。
            print('save end!')  # 输出保存结束提示。
            break  # 跳出无限循环，结束脚本。
    house_data = pd.DataFrame(eval(data_one[0]), index=[0])  # 将 Redis 中的一条房源结果转成单行 DataFrame。
    house_data.to_sql(name='house_info', con=engine, index=False, if_exists='append')  # 把单条房源追加写入 MySQL 的 house_info 表。
    del_data = redis_connect.lpop('HouseSpyder:items')  # 写入成功后从 Redis 队列弹出这条数据，避免重复入库。
    print('%d piece of data has been saved' % i)  # 打印当前已经保存到数据库的记录序号。
    i += 1  # 保存计数加一，为下一条数据更新序号。
