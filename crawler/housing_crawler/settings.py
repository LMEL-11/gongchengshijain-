"""Scrapy 设置 —— 以「合规、礼貌」为第一原则。

⚠️ 合规与道德使用约定（请勿删改下列限速项去压测目标站）：
- ROBOTSTXT_OBEY=True：遵守目标站 robots.txt。
- 低并发 + 下载延迟 + AutoThrottle：尽量减小对目标站的压力。
- CLOSESPIDER_ITEMCOUNT：安全阀，默认抓满 200 条自动停止，避免误抓海量数据。
- 本项目仅用于课程学习/演示，不内置任何反爬绕过（验证码、登录态、代理轮换规避封禁等）。
  使用前请确认你有权抓取目标站，并遵守其服务条款（ToS）。
"""

BOT_NAME = "housing_crawler"

SPIDER_MODULES = ["housing_crawler.spiders"]
NEWSPIDER_MODULE = "housing_crawler.spiders"

# --- 合规 ---
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 3.0                 # 每次请求间隔（秒）
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle：按目标站响应延迟动态调节，避免给对方造成压力
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 3.0
AUTOTHROTTLE_MAX_DELAY = 30.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# 安全阀：默认抓满 200 条后自动停止（可用 -s CLOSESPIDER_ITEMCOUNT=0 取消，或调大）
CLOSESPIDER_ITEMCOUNT = 200

# 重试 / 超时
RETRY_ENABLED = True
RETRY_TIMES = 2
DOWNLOAD_TIMEOUT = 20

# 开发期 HTTP 缓存：重复调试时直接用本地缓存，减少对目标站的真实请求
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [401, 403, 404, 429, 500, 502, 503, 504]

# 诚实标识的 UA。真实站点常需要浏览器型 UA 才返回正常页面；
# 如你的使用获得授权，可自行替换为浏览器 UA（不要用于绕过反爬/封禁）。
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 "
    "housing-crawler/1.0 (educational; contact: you@example.com)"
)
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# Item 管道：先清洗校验，再写入数据库
ITEM_PIPELINES = {
    "housing_crawler.pipelines.CleanValidatePipeline": 300,
    "housing_crawler.pipelines.DatabasePipeline": 800,
}

LOG_LEVEL = "INFO"
FEED_EXPORT_ENCODING = "utf-8"

# 现代 Scrapy 默认项（消除弃用告警）
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"


# --- 可选：用"浏览器登录后"的会话 Cookie 抓取（区/详情页需登录时）---
# 来源优先级：环境变量 LIANJIA_COOKIE > 本地文件 crawler/cookies.txt（均已 gitignore）。
# ⚠️ 这是你本人账号的登录态：可能违反链家 ToS、有封号风险；请低频小量、勿提交/外传，cookie 会过期。
def _load_lianjia_cookie():
    """从本地 Cookie 文件读取链家请求 Cookie。"""
    import os

    c = os.getenv("LIANJIA_COOKIE", "").strip()
    if c:
        return c
    path = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:  # 取第一行非注释、非空内容（# 开头的行会被忽略）
                line = line.strip().strip('"').strip("'")
                if line and not line.startswith("#"):
                    return line
    except OSError:
        pass
    return ""


LIANJIA_COOKIE = _load_lianjia_cookie()

# 仅在提供了 Cookie 时启用：直接发送完整 Cookie 头，关闭 Scrapy cookie jar 以免干扰
if LIANJIA_COOKIE:
    COOKIES_ENABLED = False
    DOWNLOADER_MIDDLEWARES = {
        "housing_crawler.middlewares.CookieHeaderMiddleware": 543,
    }
