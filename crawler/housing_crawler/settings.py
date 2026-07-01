"""Scrapy 设置 —— 以「合规、礼貌」为第一原则。

⚠️ 合规与道德使用约定（请勿删改下列限速项去压测目标站）：
- ROBOTSTXT_OBEY=True：遵守目标站 robots.txt。
- 低并发 + 下载延迟 + AutoThrottle：尽量减小对目标站的压力。
- CLOSESPIDER_ITEMCOUNT：安全阀，默认抓满 200 条自动停止，避免误抓海量数据。
- 本项目仅用于课程学习/演示，不内置任何反爬绕过（验证码、登录态、代理轮换规避封禁等）。
  使用前请确认你有权抓取目标站，并遵守其服务条款（ToS）。
"""

BOT_NAME = "housing_crawler"  # 设置 BOT_NAME 的值，供后续业务判断、查询或响应组装使用。

SPIDER_MODULES = ["housing_crawler.spiders"]  # 设置 SPIDER_MODULES 的值，供后续业务判断、查询或响应组装使用。
NEWSPIDER_MODULE = "housing_crawler.spiders"  # 设置 NEWSPIDER_MODULE 的值，供后续业务判断、查询或响应组装使用。

# --- 合规 ---
ROBOTSTXT_OBEY = True  # 设置 ROBOTSTXT_OBEY 的值，供后续业务判断、查询或响应组装使用。
CONCURRENT_REQUESTS = 2  # 设置 CONCURRENT_REQUESTS 的值，供后续业务判断、查询或响应组装使用。
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # 设置 CONCURRENT_REQUESTS_PER_DOMAIN 的值，供后续业务判断、查询或响应组装使用。
DOWNLOAD_DELAY = 3.0  # 设置 DOWNLOAD_DELAY 的值，供后续业务判断、查询或响应组装使用。
RANDOMIZE_DOWNLOAD_DELAY = True  # 设置 RANDOMIZE_DOWNLOAD_DELAY 的值，供后续业务判断、查询或响应组装使用。

# AutoThrottle：按目标站响应延迟动态调节，避免给对方造成压力
AUTOTHROTTLE_ENABLED = True  # 设置 AUTOTHROTTLE_ENABLED 的值，供后续业务判断、查询或响应组装使用。
AUTOTHROTTLE_START_DELAY = 3.0  # 设置 AUTOTHROTTLE_START_DELAY 的值，供后续业务判断、查询或响应组装使用。
AUTOTHROTTLE_MAX_DELAY = 30.0  # 设置 AUTOTHROTTLE_MAX_DELAY 的值，供后续业务判断、查询或响应组装使用。
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # 设置 AUTOTHROTTLE_TARGET_CONCURRENCY 的值，供后续业务判断、查询或响应组装使用。
AUTOTHROTTLE_DEBUG = False  # 设置 AUTOTHROTTLE_DEBUG 的值，供后续业务判断、查询或响应组装使用。

# 安全阀：默认抓满 200 条后自动停止（可用 -s CLOSESPIDER_ITEMCOUNT=0 取消，或调大）
CLOSESPIDER_ITEMCOUNT = 200  # 设置 CLOSESPIDER_ITEMCOUNT 的值，供后续业务判断、查询或响应组装使用。

# 重试 / 超时
RETRY_ENABLED = True  # 设置 RETRY_ENABLED 的值，供后续业务判断、查询或响应组装使用。
RETRY_TIMES = 2  # 设置 RETRY_TIMES 的值，供后续业务判断、查询或响应组装使用。
DOWNLOAD_TIMEOUT = 20  # 设置 DOWNLOAD_TIMEOUT 的值，供后续业务判断、查询或响应组装使用。

# 开发期 HTTP 缓存：重复调试时直接用本地缓存，减少对目标站的真实请求
HTTPCACHE_ENABLED = True  # 设置 HTTPCACHE_ENABLED 的值，供后续业务判断、查询或响应组装使用。
HTTPCACHE_EXPIRATION_SECS = 86400  # 设置 HTTPCACHE_EXPIRATION_SECS 的值，供后续业务判断、查询或响应组装使用。
HTTPCACHE_DIR = "httpcache"  # 设置 HTTPCACHE_DIR 的值，供后续业务判断、查询或响应组装使用。
HTTPCACHE_IGNORE_HTTP_CODES = [401, 403, 404, 429, 500, 502, 503, 504]  # 设置 HTTPCACHE_IGNORE_HTTP_CODES 的值，供后续业务判断、查询或响应组装使用。

# 诚实标识的 UA。真实站点常需要浏览器型 UA 才返回正常页面；
# 如你的使用获得授权，可自行替换为浏览器 UA（不要用于绕过反爬/封禁）。
USER_AGENT = (  # 设置 USER_AGENT 的值，供后续业务判断、查询或响应组装使用。
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "  # 保留字符串内容，作为说明文本或页面展示文案。
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 "  # 保留字符串内容，作为说明文本或页面展示文案。
    "housing-crawler/1.0 (educational; contact: you@example.com)"  # 保留字符串内容，作为说明文本或页面展示文案。
)  # 结束当前多行数据结构或函数调用。
DEFAULT_REQUEST_HEADERS = {  # 设置 DEFAULT_REQUEST_HEADERS 的值，供后续业务判断、查询或响应组装使用。
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # 设置 "Accept": "text/html,application/xhtml+xml,application/xml;q 的值，供后续业务判断、查询或响应组装使用。
    "Accept-Language": "zh-CN,zh;q=0.9",  # 设置 "Accept-Language": "zh-CN,zh;q 的值，供后续业务判断、查询或响应组装使用。
}  # 结束当前多行数据结构或函数调用。

# Item 管道：先清洗校验，再写入数据库
ITEM_PIPELINES = {  # 设置 ITEM_PIPELINES 的值，供后续业务判断、查询或响应组装使用。
    "housing_crawler.pipelines.CleanValidatePipeline": 300,  # 保留字符串内容，作为说明文本或页面展示文案。
    "housing_crawler.pipelines.DatabasePipeline": 800,  # 保留字符串内容，作为说明文本或页面展示文案。
}  # 结束当前多行数据结构或函数调用。

LOG_LEVEL = "INFO"  # 设置 LOG_LEVEL 的值，供后续业务判断、查询或响应组装使用。
FEED_EXPORT_ENCODING = "utf-8"  # 设置 FEED_EXPORT_ENCODING 的值，供后续业务判断、查询或响应组装使用。

# 现代 Scrapy 默认项（消除弃用告警）
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"  # 设置 REQUEST_FINGERPRINTER_IMPLEMENTATION 的值，供后续业务判断、查询或响应组装使用。
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"  # 设置 TWISTED_REACTOR 的值，供后续业务判断、查询或响应组装使用。


# --- 可选：用"浏览器登录后"的会话 Cookie 抓取（区/详情页需登录时）---
# 来源优先级：环境变量 LIANJIA_COOKIE > 本地文件 crawler/cookies.txt（均已 gitignore）。
# ⚠️ 这是你本人账号的登录态：可能违反链家 ToS、有封号风险；请低频小量、勿提交/外传，cookie 会过期。
def _load_lianjia_cookie():  # 定义 _load_lianjia_cookie 函数，集中处理这一段业务逻辑。
    """从本地 Cookie 文件读取链家请求 Cookie。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    import os  # 导入 os 模块，为当前文件提供所需功能。

    c = os.getenv("LIANJIA_COOKIE", "").strip()  # 设置 c 的值，供后续业务判断、查询或响应组装使用。
    if c:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return c  # 返回处理后的结果给调用方继续使用。
    path = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")  # 把关联表纳入查询，获取跨表维度的数据。
    try:  # 开始执行可能抛出异常的代码块。
        with open(path, encoding="utf-8") as fh:  # 进入上下文管理流程，自动处理资源打开和释放。
            for line in fh:  # 遍历当前数据集合，逐项完成处理。
                line = line.strip().strip('"').strip("'")  # 设置 line 的值，供后续业务判断、查询或响应组装使用。
                if line and not line.startswith("#"):  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    return line  # 返回处理后的结果给调用方继续使用。
    except OSError:  # 捕获指定异常，并转入可控的错误处理流程。
        pass  # 保留空实现位置，表示这里暂不执行额外逻辑。
    return ""  # 返回处理后的结果给调用方继续使用。


LIANJIA_COOKIE = _load_lianjia_cookie()  # 设置 LIANJIA_COOKIE 的值，供后续业务判断、查询或响应组装使用。

# 仅在提供了 Cookie 时启用：直接发送完整 Cookie 头，关闭 Scrapy cookie jar 以免干扰
if LIANJIA_COOKIE:  # 判断当前条件是否成立，决定是否进入对应处理分支。
    COOKIES_ENABLED = False  # 设置 COOKIES_ENABLED 的值，供后续业务判断、查询或响应组装使用。
    DOWNLOADER_MIDDLEWARES = {  # 设置 DOWNLOADER_MIDDLEWARES 的值，供后续业务判断、查询或响应组装使用。
        "housing_crawler.middlewares.CookieHeaderMiddleware": 543,  # 保留字符串内容，作为说明文本或页面展示文案。
    }  # 结束当前多行数据结构或函数调用。
