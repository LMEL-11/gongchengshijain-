"""Scrapy 设置 —— 以「合规、礼貌」为第一原则。

⚠️ 合规与道德使用约定（请勿删改下列限速项去压测目标站）：
- ROBOTSTXT_OBEY=True：遵守目标站 robots.txt。
- 低并发 + 下载延迟 + AutoThrottle：尽量减小对目标站的压力。
- CLOSESPIDER_ITEMCOUNT：安全阀，默认抓满 200 条自动停止，避免误抓海量数据。
- 本项目仅用于课程学习/演示，不内置任何反爬绕过（验证码、登录态、代理轮换规避封禁等）。
  使用前请确认你有权抓取目标站，并遵守其服务条款（ToS）。
"""

BOT_NAME = "housing_crawler"  # 赋值或更新当前变量/字段。

SPIDER_MODULES = ["housing_crawler.spiders"]  # 赋值或更新当前变量/字段。
NEWSPIDER_MODULE = "housing_crawler.spiders"  # 赋值或更新当前变量/字段。

# --- 合规 ---
ROBOTSTXT_OBEY = True  # 赋值或更新当前变量/字段。
CONCURRENT_REQUESTS = 2  # 赋值或更新当前变量/字段。
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # 赋值或更新当前变量/字段。
DOWNLOAD_DELAY = 3.0                 # 每次请求间隔（秒）
RANDOMIZE_DOWNLOAD_DELAY = True  # 赋值或更新当前变量/字段。

# AutoThrottle：按目标站响应延迟动态调节，避免给对方造成压力
AUTOTHROTTLE_ENABLED = True  # 赋值或更新当前变量/字段。
AUTOTHROTTLE_START_DELAY = 3.0  # 赋值或更新当前变量/字段。
AUTOTHROTTLE_MAX_DELAY = 30.0  # 赋值或更新当前变量/字段。
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # 赋值或更新当前变量/字段。
AUTOTHROTTLE_DEBUG = False  # 赋值或更新当前变量/字段。

# 安全阀：默认抓满 200 条后自动停止（可用 -s CLOSESPIDER_ITEMCOUNT=0 取消，或调大）
CLOSESPIDER_ITEMCOUNT = 200  # 赋值或更新当前变量/字段。

# 重试 / 超时
RETRY_ENABLED = True  # 赋值或更新当前变量/字段。
RETRY_TIMES = 2  # 赋值或更新当前变量/字段。
DOWNLOAD_TIMEOUT = 20  # 赋值或更新当前变量/字段。

# 开发期 HTTP 缓存：重复调试时直接用本地缓存，减少对目标站的真实请求
HTTPCACHE_ENABLED = True  # 赋值或更新当前变量/字段。
HTTPCACHE_EXPIRATION_SECS = 86400  # 赋值或更新当前变量/字段。
HTTPCACHE_DIR = "httpcache"  # 赋值或更新当前变量/字段。
HTTPCACHE_IGNORE_HTTP_CODES = [401, 403, 404, 429, 500, 502, 503, 504]  # 赋值或更新当前变量/字段。

# 诚实标识的 UA。真实站点常需要浏览器型 UA 才返回正常页面；
# 如你的使用获得授权，可自行替换为浏览器 UA（不要用于绕过反爬/封禁）。
USER_AGENT = (  # 赋值或更新当前变量/字段。
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 "
    "housing-crawler/1.0 (educational; contact: you@example.com)"
)  # 结束当前数据结构或调用块。
DEFAULT_REQUEST_HEADERS = {  # 赋值或更新当前变量/字段。
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # 赋值或更新当前变量/字段。
    "Accept-Language": "zh-CN,zh;q=0.9",  # 赋值或更新当前变量/字段。
}  # 结束当前数据结构或调用块。

# Item 管道：先清洗校验，再写入数据库
ITEM_PIPELINES = {  # 赋值或更新当前变量/字段。
    "housing_crawler.pipelines.CleanValidatePipeline": 300,  # 设置当前数据项或参数。
    "housing_crawler.pipelines.DatabasePipeline": 800,  # 设置当前数据项或参数。
}  # 结束当前数据结构或调用块。

LOG_LEVEL = "INFO"  # 赋值或更新当前变量/字段。
FEED_EXPORT_ENCODING = "utf-8"  # 赋值或更新当前变量/字段。

# 现代 Scrapy 默认项（消除弃用告警）
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"  # 赋值或更新当前变量/字段。
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"  # 赋值或更新当前变量/字段。


# --- 可选：用"浏览器登录后"的会话 Cookie 抓取（区/详情页需登录时）---
# 来源优先级：环境变量 LIANJIA_COOKIE > 本地文件 crawler/cookies.txt（均已 gitignore）。
# ⚠️ 这是你本人账号的登录态：可能违反链家 ToS、有封号风险；请低频小量、勿提交/外传，cookie 会过期。
def _load_lianjia_cookie():  # 声明函数或方法入口。
    """从本地 Cookie 文件读取链家请求 Cookie。"""
    import os  # 导入本行所需的模块或对象。

    c = os.getenv("LIANJIA_COOKIE", "").strip()  # 赋值或更新当前变量/字段。
    if c:  # 根据条件判断是否进入该分支。
        return c  # 返回当前逻辑的处理结果。
    path = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")  # 赋值或更新当前变量/字段。
    try:  # 开始执行可能出现异常的逻辑。
        with open(path, encoding="utf-8") as fh:  # 进入上下文管理器并自动处理资源。
            for line in fh:  # 取第一行非注释、非空内容（# 开头的行会被忽略）
                line = line.strip().strip('"').strip("'")  # 赋值或更新当前变量/字段。
                if line and not line.startswith("#"):  # 根据条件判断是否进入该分支。
                    return line  # 返回当前逻辑的处理结果。
    except OSError:  # 捕获异常并执行错误处理。
        pass  # 保留语法占位以便后续扩展。
    return ""  # 返回当前逻辑的处理结果。


LIANJIA_COOKIE = _load_lianjia_cookie()  # 赋值或更新当前变量/字段。

# 仅在提供了 Cookie 时启用：直接发送完整 Cookie 头，关闭 Scrapy cookie jar 以免干扰
if LIANJIA_COOKIE:  # 根据条件判断是否进入该分支。
    COOKIES_ENABLED = False  # 赋值或更新当前变量/字段。
    DOWNLOADER_MIDDLEWARES = {  # 赋值或更新当前变量/字段。
        "housing_crawler.middlewares.CookieHeaderMiddleware": 543,  # 设置当前数据项或参数。
    }  # 结束当前数据结构或调用块。
