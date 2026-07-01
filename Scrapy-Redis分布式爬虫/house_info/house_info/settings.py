# Scrapy settings for house_info project  # 说明这是 house_info 这个 Scrapy 项目的配置文件。
#  # 空注释行，用于分隔文件头说明。
# For simplicity, this file contains only settings considered important or  # Scrapy 模板说明：这里只保留常用配置。
# commonly used. You can find more settings consulting the documentation:  # Scrapy 模板说明：更多配置可以查官方文档。
#  # 空注释行，用于分隔文档链接。
#     https://docs.scrapy.org/en/latest/topics/settings.html  # Scrapy 通用配置文档。
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html  # 下载器中间件配置文档。
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html  # 爬虫中间件配置文档。

BOT_NAME = "house_info"  # 设置 Scrapy 项目名称，日志和运行时会显示该名称。

SPIDER_MODULES = ["house_info.spiders"]  # 指定 Scrapy 到 house_info.spiders 包中查找爬虫。
NEWSPIDER_MODULE = "house_info.spiders"  # 指定 scrapy genspider 新建爬虫时默认放入的模块。


# Crawl responsibly by identifying yourself (and your website) on the user-agent  # Scrapy 模板提示：正式爬取时应设置清晰的 User-Agent。
#USER_AGENT = "house_info (+http://www.yourdomain.com)"  # User-Agent 示例配置，当前没有启用。

# Obey robots.txt rules  # Scrapy 模板提示：是否遵守 robots.txt 协议。
ROBOTSTXT_OBEY = False  # 关闭 robots.txt 限制，让爬虫可以访问目标页面。

# Configure maximum concurrent requests performed by Scrapy (default: 16)  # Scrapy 模板提示：可以设置最大并发请求数。
#CONCURRENT_REQUESTS = 32  # 最大并发请求数示例，当前下面使用了正式配置。
CONCURRENT_REQUESTS = 32  # 设置全局最大并发请求数为 32，提高抓取速度。
CONCURRENT_ITEMS = 200  # 设置同时处理的 Item 数量上限为 200。
# Configure a delay for requests for the same website (default: 0)  # Scrapy 模板提示：可以设置同站点请求延迟。
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay  # 下载延迟配置说明链接。
# See also autothrottle settings and docs  # 提醒也可以结合自动限速配置。
#DOWNLOAD_DELAY = 3  # 下载延迟示例，当前未启用固定延迟。
# The download delay setting will honor only one of:  # Scrapy 模板提示：下载延迟会受域名/IP 并发配置影响。
#CONCURRENT_REQUESTS_PER_DOMAIN = 16  # 单域名并发示例，当前未启用。
#CONCURRENT_REQUESTS_PER_IP = 16  # 单 IP 并发示例，当前未启用。

# Disable cookies (enabled by default)  # Scrapy 模板提示：可以关闭 Cookie。
#COOKIES_ENABLED = False  # Cookie 开关示例，当前未启用。

# Disable Telnet Console (enabled by default)  # Scrapy 模板提示：可以关闭 Telnet 控制台。
#TELNETCONSOLE_ENABLED = False  # Telnet 控制台开关示例，当前未启用。

# Override the default request headers:  # Scrapy 模板提示：这里可以覆盖默认请求头。
DEFAULT_REQUEST_HEADERS = {  # 设置默认请求头，所有请求都会带上这些头信息。
   # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # Accept 请求头示例，当前未启用。
   # "Accept-Language": "en",  # 语言请求头示例，当前未启用。
   "user_agent": 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'  # 设置浏览器标识，降低被目标站点识别为爬虫的概率。
}  # 默认请求头配置结束。

# Enable or disable spider middlewares  # Scrapy 模板提示：这里可以启用爬虫中间件。
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html  # 爬虫中间件文档链接。
#SPIDER_MIDDLEWARES = {  # 爬虫中间件配置示例，当前未启用。
#    "house_info.middlewares.HouseInfoSpiderMiddleware": 543,  # 项目爬虫中间件启用示例，数字表示优先级。
#}  # 爬虫中间件配置示例结束。

# Enable or disable downloader middlewares  # Scrapy 模板提示：这里可以启用下载器中间件。
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html  # 下载器中间件文档链接。
#DOWNLOADER_MIDDLEWARES = {  # 下载器中间件配置示例，当前未启用。
#    "house_info.middlewares.HouseInfoDownloaderMiddleware": 543,  # 项目下载器中间件启用示例，数字表示优先级。
#}  # 下载器中间件配置示例结束。

# Enable or disable extensions  # Scrapy 模板提示：这里可以启用或禁用扩展。
# See https://docs.scrapy.org/en/latest/topics/extensions.html  # Scrapy 扩展配置文档链接。
#EXTENSIONS = {  # 扩展配置示例，当前未启用。
#    "scrapy.extensions.telnet.TelnetConsole": None,  # 禁用 TelnetConsole 扩展示例。
#}  # 扩展配置示例结束。

# Configure item pipelines  # Scrapy 模板提示：这里可以配置 Item Pipeline。
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html  # Item Pipeline 文档链接。
#ITEM_PIPELINES = {  # 项目自定义 Pipeline 配置示例，当前被下面的 RedisPipeline 替代。
#    "house_info.pipelines.HouseInfoPipeline": 300,  # 启用自定义 HouseInfoPipeline 的示例。
#}  # 自定义 Pipeline 配置示例结束。

# Enable and configure the AutoThrottle extension (disabled by default)  # Scrapy 模板提示：可以启用自动限速。
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html  # 自动限速配置文档链接。
#AUTOTHROTTLE_ENABLED = True  # 自动限速开关示例，当前下面有正式启用配置。
# The initial download delay  # Scrapy 模板提示：自动限速初始延迟。
#AUTOTHROTTLE_START_DELAY = 5  # 自动限速初始延迟示例，当前未启用。
# The maximum download delay to be set in case of high latencies  # Scrapy 模板提示：高延迟时的最大等待时间。
#AUTOTHROTTLE_MAX_DELAY = 60  # 自动限速最大延迟示例，当前未启用。
# The average number of requests Scrapy should be sending in parallel to  # Scrapy 模板提示：目标平均并发。
# each remote server  # Scrapy 模板说明：上一行所说的并发是面向每个远程服务。
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # 自动限速目标并发示例，当前未启用。
# Enable showing throttling stats for every response received:  # Scrapy 模板提示：可开启自动限速调试信息。
#AUTOTHROTTLE_DEBUG = False  # 自动限速调试开关示例，当前未启用。

# Enable and configure HTTP caching (disabled by default)  # Scrapy 模板提示：可以启用 HTTP 缓存。
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings  # HTTP 缓存文档链接。
#HTTPCACHE_ENABLED = True  # HTTP 缓存开关示例，当前未启用。
#HTTPCACHE_EXPIRATION_SECS = 0  # 缓存过期时间示例，0 表示不过期。
#HTTPCACHE_DIR = "httpcache"  # 缓存目录示例。
#HTTPCACHE_IGNORE_HTTP_CODES = []  # 忽略缓存的 HTTP 状态码示例。
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"  # 文件系统缓存后端示例。

# Set settings whose default value is deprecated to a future-proof value  # Scrapy 模板提示：设置未来兼容配置。
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"  # 使用 Scrapy 2.7 的请求指纹算法，避免版本警告。
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"  # 设置 Twisted reactor，适配 asyncio 事件循环。
FEED_EXPORT_ENCODING = "utf-8"  # 设置导出文件编码为 UTF-8，避免中文乱码。

ITEM_PIPELINES = {  # 配置 Item Pipeline，决定爬虫产出的 item 交给谁处理。
    'scrapy_redis.pipelines.RedisPipeline': 300}  # 启用 Scrapy-Redis 的 RedisPipeline，把 item 写入 Redis 队列。

# 增加了一个去重容器类的配置，作用使用Redis的set集合来存储请求的指纹数据，从而实现请求去重的持久化
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"  # 使用 Scrapy-Redis 的去重器，把请求指纹存到 Redis。

# 使用scrapy-redis组件自己的调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"  # 使用 Scrapy-Redis 调度器，让多个爬虫实例共享 Redis 请求队列。

# 配置调度器是否要持久化，也就是当爬虫结束了，要不要清空Redis中请求队列和去重指纹的set。如果是True，就表示持久化
SCHEDULER_PERSIST = True  # 保留 Redis 中的请求队列和去重集合，爬虫停止后可继续接着跑。

# 配置当前项目连接的redis地址
REDIS_HOST = 'node1'  # redis服务的ip地址
REDIS_PORT = 6379  # 设置 Redis 服务端口。
REDIS_ENCODING = 'utf-8'  # 设置 Redis 数据编码，确保中文字段正常处理。

AUTOTHROTTLE_ENABLED = True  # 启用 Scrapy 自动限速，根据响应延迟自动调整请求速度。
HTTPERROR_ALLOWED_CODES = [301]  # 允许 301 状态码响应继续进入爬虫处理流程。
