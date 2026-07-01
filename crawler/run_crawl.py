"""便捷启动脚本（无需记 scrapy 命令）。

用法：
  python run_crawl.py [city缩写] [城市中文名] [max_pages] [region]
示例：
  python run_crawl.py bj 北京 5
  python run_crawl.py jn 济南 3 lixiaqu

等价于：
  scrapy crawl lianjia -a city=bj -a city_name=北京 -a max_pages=5
"""
import sys  # 导入 sys 模块，为当前文件提供所需功能。

from scrapy.crawler import CrawlerProcess  # 从 scrapy.crawler 导入 CrawlerProcess，供本文件后续逻辑调用。
from scrapy.utils.project import get_project_settings  # 从 scrapy.utils.project 导入 get_project_settings，供本文件后续逻辑调用。

from housing_crawler.spiders.lianjia import LianjiaSpider  # 从 housing_crawler.spiders.lianjia 导入 LianjiaSpider，供本文件后续逻辑调用。


def main():  # 定义 main 函数，集中处理这一段业务逻辑。
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    args = sys.argv[1:]  # 设置 args 的值，供后续业务判断、查询或响应组装使用。
    kwargs = {}  # 设置 kwargs 的值，供后续业务判断、查询或响应组装使用。
    if len(args) >= 1:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        kwargs["city"] = args[0]  # 设置 kwargs["city" 的值，供后续业务判断、查询或响应组装使用。
    if len(args) >= 2:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        kwargs["city_name"] = args[1]  # 设置 kwargs["city_name" 的值，供后续业务判断、查询或响应组装使用。
    if len(args) >= 3:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        kwargs["max_pages"] = args[2]  # 设置 kwargs["max_pages" 的值，供后续业务判断、查询或响应组装使用。
    if len(args) >= 4:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        kwargs["region"] = args[3]  # 设置 kwargs["region" 的值，供后续业务判断、查询或响应组装使用。

    process = CrawlerProcess(get_project_settings())  # 设置 process 的值，供后续业务判断、查询或响应组装使用。
    process.crawl(LianjiaSpider, **kwargs)  # 执行当前代码行对应的业务处理步骤。
    process.start()  # 执行当前代码行对应的业务处理步骤。


if __name__ == "__main__":  # 判断当前条件是否成立，决定是否进入对应处理分支。
    main()  # 执行当前代码行对应的业务处理步骤。
