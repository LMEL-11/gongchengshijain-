"""便捷启动脚本（无需记 scrapy 命令）。

用法：
  python run_crawl.py [city缩写] [城市中文名] [max_pages] [region]
示例：
  python run_crawl.py bj 北京 5
  python run_crawl.py jn 济南 3 lixiaqu

等价于：
  scrapy crawl lianjia -a city=bj -a city_name=北京 -a max_pages=5
"""
import sys  # 导入本行所需的模块或对象。

from scrapy.crawler import CrawlerProcess  # 导入本行所需的模块或对象。
from scrapy.utils.project import get_project_settings  # 导入本行所需的模块或对象。

from housing_crawler.spiders.lianjia import LianjiaSpider  # 导入本行所需的模块或对象。


def main():  # 声明函数或方法入口。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    args = sys.argv[1:]  # 赋值或更新当前变量/字段。
    kwargs = {}  # 赋值或更新当前变量/字段。
    if len(args) >= 1:  # 根据条件判断是否进入该分支。
        kwargs["city"] = args[0]  # 赋值或更新当前变量/字段。
    if len(args) >= 2:  # 根据条件判断是否进入该分支。
        kwargs["city_name"] = args[1]  # 赋值或更新当前变量/字段。
    if len(args) >= 3:  # 根据条件判断是否进入该分支。
        kwargs["max_pages"] = args[2]  # 赋值或更新当前变量/字段。
    if len(args) >= 4:  # 根据条件判断是否进入该分支。
        kwargs["region"] = args[3]  # 赋值或更新当前变量/字段。

    process = CrawlerProcess(get_project_settings())  # 赋值或更新当前变量/字段。
    process.crawl(LianjiaSpider, **kwargs)  # 执行本行代码逻辑。
    process.start()  # 执行本行代码逻辑。


if __name__ == "__main__":  # 根据条件判断是否进入该分支。
    main()  # 执行本行代码逻辑。
