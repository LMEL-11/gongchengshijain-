"""便捷启动脚本（无需记 scrapy 命令）。

用法：
  python run_crawl.py [city缩写] [城市中文名] [max_pages] [region]
示例：
  python run_crawl.py bj 北京 5
  python run_crawl.py jn 济南 3 lixiaqu

等价于：
  scrapy crawl lianjia -a city=bj -a city_name=北京 -a max_pages=5
"""
import sys  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from scrapy.crawler import CrawlerProcess  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from scrapy.utils.project import get_project_settings  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from housing_crawler.spiders.lianjia import LianjiaSpider  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


def main():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    args = sys.argv[1:]  # 计算或更新args中间数据，作为后续业务判断、统计或响应组装的输入。
    kwargs = {}  # 初始化kwargs中间数据字典，用于承载接口返回或中间聚合结果。
    if len(args) >= 1:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        kwargs["city"] = args[0]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    if len(args) >= 2:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        kwargs["city_name"] = args[1]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    if len(args) >= 3:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        kwargs["max_pages"] = args[2]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    if len(args) >= 4:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        kwargs["region"] = args[3]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    process = CrawlerProcess(get_project_settings())  # 从请求或外部输入提取process中间数据，用于后续校验、查询或写入。
    process.crawl(LianjiaSpider, **kwargs)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    process.start()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。


if __name__ == "__main__":  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    main()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
