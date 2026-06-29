"""便捷启动脚本（无需记 scrapy 命令）。

用法：
  python run_crawl.py [city缩写] [城市中文名] [max_pages] [region]
示例：
  python run_crawl.py bj 北京 5
  python run_crawl.py jn 济南 3 lixiaqu

等价于：
  scrapy crawl lianjia -a city=bj -a city_name=北京 -a max_pages=5
"""
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from housing_crawler.spiders.lianjia import LianjiaSpider


def main():
    """作为脚本入口执行当前文件的主要导入、迁移或启动流程。"""
    args = sys.argv[1:]
    kwargs = {}
    if len(args) >= 1:
        kwargs["city"] = args[0]
    if len(args) >= 2:
        kwargs["city_name"] = args[1]
    if len(args) >= 3:
        kwargs["max_pages"] = args[2]
    if len(args) >= 4:
        kwargs["region"] = args[3]

    process = CrawlerProcess(get_project_settings())
    process.crawl(LianjiaSpider, **kwargs)
    process.start()


if __name__ == "__main__":
    main()
