# Define here the models for your spider middleware  # 说明本文件用于定义 Scrapy 爬虫中间件和下载器中间件。
#  # 空注释行，用于分隔模板说明。
# See documentation in:  # 提示可以查看 Scrapy 官方中间件文档。
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html  # Scrapy Spider Middleware 官方文档地址。

from scrapy import signals  # 导入 Scrapy 信号模块，用于监听爬虫启动等生命周期事件。

# useful for handling different item types with a single interface  # 模板说明：ItemAdapter 可统一处理不同类型的 item。
from itemadapter import is_item, ItemAdapter  # 导入 item 判断和适配工具；当前中间件模板暂未使用。


class HouseInfoSpiderMiddleware:  # 定义爬虫中间件类，位于引擎和 Spider 之间。
    # Not all methods need to be defined. If a method is not defined,  # 模板说明：中间件方法可以按需实现。
    # scrapy acts as if the spider middleware does not modify the  # 模板说明：未实现的方法等同于不修改数据。
    # passed objects.  # 模板说明：传入对象会原样继续流转。

    @classmethod  # 声明下面的方法是类方法，由 Scrapy 用类本身调用。
    def from_crawler(cls, crawler):  # Scrapy 创建中间件实例时会调用这个工厂方法。
        # This method is used by Scrapy to create your spiders.  # 模板说明：Scrapy 通过该方法创建中间件对象。
        s = cls()  # 创建当前中间件实例。
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)  # 将 spider_opened 方法绑定到爬虫打开信号。
        return s  # 返回中间件实例给 Scrapy 使用。

    def process_spider_input(self, response, spider):  # 每个响应进入 Spider 之前会经过这个方法。
        # Called for each response that goes through the spider  # 模板说明：该方法处理进入 Spider 的响应。
        # middleware and into the spider.  # 模板说明：响应会先过中间件再交给 Spider。

        # Should return None or raise an exception.  # 模板说明：返回 None 表示不拦截，抛异常表示中断处理。
        return None  # 不修改响应，让它继续进入 Spider 的解析函数。

    def process_spider_output(self, response, result, spider):  # Spider 解析完成后，结果会经过这个方法。
        # Called with the results returned from the Spider, after  # 模板说明：该方法接收 Spider 返回的 Request 或 Item。
        # it has processed the response.  # 模板说明：处理发生在 Spider 解析响应之后。

        # Must return an iterable of Request, or item objects.  # 模板说明：必须返回可迭代的 Request 或 Item。
        for i in result:  # 遍历 Spider 产出的每一个结果。
            yield i  # 原样返回结果，让后续流程继续处理。

    def process_spider_exception(self, response, exception, spider):  # Spider 或前置中间件抛异常时会调用。
        # Called when a spider or process_spider_input() method  # 模板说明：Spider 或 process_spider_input 出错会触发这里。
        # (from other spider middleware) raises an exception.  # 模板说明：其他爬虫中间件的异常也会进入这里。

        # Should return either None or an iterable of Request or item objects.  # 模板说明：可返回 None 或补救性的 Request/Item。
        pass  # 当前不处理异常，交给 Scrapy 默认异常流程。

    def process_start_requests(self, start_requests, spider):  # 起始请求进入调度器前会经过这里。
        # Called with the start requests of the spider, and works  # 模板说明：该方法处理 Spider 的初始请求。
        # similarly to the process_spider_output() method, except  # 模板说明：行为类似 process_spider_output。
        # that it doesn’t have a response associated.  # 模板说明：区别是此时还没有响应对象。

        # Must return only requests (not items).  # 模板说明：这里只能返回 Request，不能返回 Item。
        for r in start_requests:  # 遍历 Spider 生成的起始请求。
            yield r  # 原样返回起始请求，让 Scrapy 调度器继续处理。

    def spider_opened(self, spider):  # 爬虫启动时由信号系统调用。
        spider.logger.info("Spider opened: %s" % spider.name)  # 在日志中记录当前爬虫已经启动。


class HouseInfoDownloaderMiddleware:  # 定义下载器中间件类，位于引擎和下载器之间。
    # Not all methods need to be defined. If a method is not defined,  # 模板说明：下载器中间件方法也可以按需实现。
    # scrapy acts as if the downloader middleware does not modify the  # 模板说明：未实现的方法等同于不修改请求或响应。
    # passed objects.  # 模板说明：传入对象会原样继续流转。

    @classmethod  # 声明下面的方法是类方法，由 Scrapy 创建中间件时调用。
    def from_crawler(cls, crawler):  # Scrapy 创建下载器中间件实例时会调用。
        # This method is used by Scrapy to create your spiders.  # 模板说明：Scrapy 通过该方法创建中间件对象。
        s = cls()  # 创建当前下载器中间件实例。
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)  # 绑定爬虫打开信号，用于记录日志。
        return s  # 返回下载器中间件实例给 Scrapy 使用。

    def process_request(self, request, spider):  # 请求发送到下载器之前会经过这个方法。
        # Called for each request that goes through the downloader  # 模板说明：每个请求都会经过下载器中间件。
        # middleware.  # 模板说明：这里可以改请求头、代理、Cookie 等。

        # Must either:  # 模板说明：该方法有几种合法返回方式。
        # - return None: continue processing this request  # 返回 None 表示继续下载当前请求。
        # - or return a Response object  # 返回 Response 表示直接用响应跳过下载。
        # - or return a Request object  # 返回 Request 表示改为调度新的请求。
        # - or raise IgnoreRequest: process_exception() methods of  # 抛 IgnoreRequest 会触发异常处理链。
        #   installed downloader middleware will be called  # 模板说明：已安装中间件的 process_exception 会被调用。
        return None  # 当前不修改请求，让 Scrapy 继续正常下载。

    def process_response(self, request, response, spider):  # 下载器拿到响应后会经过这个方法。
        # Called with the response returned from the downloader.  # 模板说明：该方法处理下载器返回的响应。

        # Must either;  # 模板说明：该方法也有几种合法返回方式。
        # - return a Response object  # 返回 Response 表示把响应交给后续流程。
        # - return a Request object  # 返回 Request 表示重新调度请求。
        # - or raise IgnoreRequest  # 抛 IgnoreRequest 表示丢弃该请求结果。
        return response  # 当前不修改响应，原样交给 Spider。

    def process_exception(self, request, exception, spider):  # 下载请求发生异常时会调用。
        # Called when a download handler or a process_request()  # 模板说明：下载器或 process_request 出错会进入这里。
        # (from other downloader middleware) raises an exception.  # 模板说明：其他下载器中间件的异常也会进入这里。

        # Must either:  # 模板说明：该方法有几种合法返回方式。
        # - return None: continue processing this exception  # 返回 None 表示继续交给其他异常处理器。
        # - return a Response object: stops process_exception() chain  # 返回 Response 表示用响应恢复流程并停止异常链。
        # - return a Request object: stops process_exception() chain  # 返回 Request 表示重新请求并停止异常链。
        pass  # 当前不处理下载异常，交给 Scrapy 默认异常流程。

    def spider_opened(self, spider):  # 爬虫启动时由信号系统调用。
        spider.logger.info("Spider opened: %s" % spider.name)  # 在日志中记录当前爬虫已经启动。
