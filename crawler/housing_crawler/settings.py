"""Scrapy 设置 —— 以「合规、礼貌」为第一原则。

⚠️ 合规与道德使用约定（请勿删改下列限速项去压测目标站）：
- ROBOTSTXT_OBEY=True：遵守目标站 robots.txt。
- 低并发 + 下载延迟 + AutoThrottle：尽量减小对目标站的压力。
- CLOSESPIDER_ITEMCOUNT：安全阀，默认抓满 200 条自动停止，避免误抓海量数据。
- 本项目仅用于课程学习/演示，不内置任何反爬绕过（验证码、登录态、代理轮换规避封禁等）。
  使用前请确认你有权抓取目标站，并遵守其服务条款（ToS）。
"""

BOT_NAME = "housing_crawler"  # 计算或更新BOT_NAME中间数据，作为后续业务判断、统计或响应组装的输入。

SPIDER_MODULES = ["housing_crawler.spiders"]  # 初始化SPIDER_MODULES中间数据列表，用于收集清洗后的多条业务数据。
NEWSPIDER_MODULE = "housing_crawler.spiders"  # 计算或更新NEWSPIDER_MODULE中间数据，作为后续业务判断、统计或响应组装的输入。

# --- 合规 ---
ROBOTSTXT_OBEY = True  # 计算或更新ROBOTSTXT_OBEY中间数据，作为后续业务判断、统计或响应组装的输入。
CONCURRENT_REQUESTS = 2  # 计算或更新CONCURRENT_REQUESTS中间数据，作为后续业务判断、统计或响应组装的输入。
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # 计算或更新CONCURRENT_REQUESTS_PER_DOMAIN中间数据，作为后续业务判断、统计或响应组装的输入。
DOWNLOAD_DELAY = 3.0                 # 每次请求间隔（秒）
RANDOMIZE_DOWNLOAD_DELAY = True  # 计算或更新RANDOMIZE_DOWNLOAD_DELAY中间数据，作为后续业务判断、统计或响应组装的输入。

# AutoThrottle：按目标站响应延迟动态调节，避免给对方造成压力
AUTOTHROTTLE_ENABLED = True  # 计算或更新AUTOTHROTTLE_ENABLED中间数据，作为后续业务判断、统计或响应组装的输入。
AUTOTHROTTLE_START_DELAY = 3.0  # 计算或更新AUTOTHROTTLE_START_DELAY中间数据，作为后续业务判断、统计或响应组装的输入。
AUTOTHROTTLE_MAX_DELAY = 30.0  # 计算或更新AUTOTHROTTLE_MAX_DELAY中间数据，作为后续业务判断、统计或响应组装的输入。
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # 计算或更新AUTOTHROTTLE_TARGET_CONCURRENCY中间数据，作为后续业务判断、统计或响应组装的输入。
AUTOTHROTTLE_DEBUG = False  # 计算或更新AUTOTHROTTLE_DEBUG中间数据，作为后续业务判断、统计或响应组装的输入。

# 安全阀：默认抓满 200 条后自动停止（可用 -s CLOSESPIDER_ITEMCOUNT=0 取消，或调大）
CLOSESPIDER_ITEMCOUNT = 200  # 计算或更新CLOSESPIDER_ITEMCOUNT中间数据，作为后续业务判断、统计或响应组装的输入。

# 重试 / 超时
RETRY_ENABLED = True  # 计算或更新RETRY_ENABLED中间数据，作为后续业务判断、统计或响应组装的输入。
RETRY_TIMES = 2  # 计算或更新RETRY_TIMES中间数据，作为后续业务判断、统计或响应组装的输入。
DOWNLOAD_TIMEOUT = 20  # 计算或更新DOWNLOAD_TIMEOUT中间数据，作为后续业务判断、统计或响应组装的输入。

# 开发期 HTTP 缓存：重复调试时直接用本地缓存，减少对目标站的真实请求
HTTPCACHE_ENABLED = True  # 计算或更新HTTPCACHE_ENABLED中间数据，作为后续业务判断、统计或响应组装的输入。
HTTPCACHE_EXPIRATION_SECS = 86400  # 计算或更新HTTPCACHE_EXPIRATION_SECS中间数据，作为后续业务判断、统计或响应组装的输入。
HTTPCACHE_DIR = "httpcache"  # 计算或更新HTTPCACHE_DIR中间数据，作为后续业务判断、统计或响应组装的输入。
HTTPCACHE_IGNORE_HTTP_CODES = [401, 403, 404, 429, 500, 502, 503, 504]  # 初始化HTTPCACHE_IGNORE_HTTP_CODES中间数据列表，用于收集清洗后的多条业务数据。

# 诚实标识的 UA。真实站点常需要浏览器型 UA 才返回正常页面；
# 如你的使用获得授权，可自行替换为浏览器 UA（不要用于绕过反爬/封禁）。
USER_AGENT = (  # 计算或更新USER_AGENT中间数据，作为后续业务判断、统计或响应组装的输入。
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 "  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    "housing-crawler/1.0 (educational; contact: you@example.com)"  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
)  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
DEFAULT_REQUEST_HEADERS = {  # 初始化DEFAULT_REQUEST_HEADERS中间数据字典，用于承载接口返回或中间聚合结果。
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # 把Accept字段写入响应数据，供前端页面、图表或后续接口读取。
    "Accept-Language": "zh-CN,zh;q=0.9",  # 把Accept-Language字段写入响应数据，供前端页面、图表或后续接口读取。
}  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

# Item 管道：先清洗校验，再写入数据库
ITEM_PIPELINES = {  # 初始化ITEM_PIPELINES中间数据字典，用于承载接口返回或中间聚合结果。
    "housing_crawler.pipelines.CleanValidatePipeline": 300,  # 把housing_crawler.pipelines.CleanValidatePipeline字段写入响应数据，供前端页面、图表或后续接口读取。
    "housing_crawler.pipelines.DatabasePipeline": 800,  # 把housing_crawler.pipelines.DatabasePipeline字段写入响应数据，供前端页面、图表或后续接口读取。
}  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

LOG_LEVEL = "INFO"  # 计算或更新LOG_LEVEL中间数据，作为后续业务判断、统计或响应组装的输入。
FEED_EXPORT_ENCODING = "utf-8"  # 计算或更新FEED_EXPORT_ENCODING中间数据，作为后续业务判断、统计或响应组装的输入。

# 现代 Scrapy 默认项（消除弃用告警）
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"  # 计算或更新REQUEST_FINGERPRINTER_IMPLEMENTATION中间数据，作为后续业务判断、统计或响应组装的输入。
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"  # 计算或更新TWISTED_REACTOR中间数据，作为后续业务判断、统计或响应组装的输入。


# --- 可选：用"浏览器登录后"的会话 Cookie 抓取（区/详情页需登录时）---
# 来源优先级：环境变量 LIANJIA_COOKIE > 本地文件 crawler/cookies.txt（均已 gitignore）。
# ⚠️ 这是你本人账号的登录态：可能违反链家 ToS、有封号风险；请低频小量、勿提交/外传，cookie 会过期。
def _load_lianjia_cookie():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从本地 Cookie 文件读取链家请求 Cookie。"""
    import os  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

    c = os.getenv("LIANJIA_COOKIE", "").strip()  # 计算或更新c中间数据，作为后续业务判断、统计或响应组装的输入。
    if c:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return c  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    path = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")  # 计算或更新地图钻取路径，作为后续业务判断、统计或响应组装的输入。
    try:  # 开始执行可能失败的外部访问、数据转换或数据库操作。
        with open(path, encoding="utf-8") as fh:  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
            for line in fh:  # 取第一行非注释、非空内容（# 开头的行会被忽略）
                line = line.strip().strip('"').strip("'")  # 计算或更新line中间数据，作为后续业务判断、统计或响应组装的输入。
                if line and not line.startswith("#"):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                    return line  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    except OSError:  # 捕获异常并转换为可控的错误处理或提示信息。
        pass  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return ""  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


LIANJIA_COOKIE = _load_lianjia_cookie()  # 计算或更新LIANJIA_COOKIE中间数据，作为后续业务判断、统计或响应组装的输入。

# 仅在提供了 Cookie 时启用：直接发送完整 Cookie 头，关闭 Scrapy cookie jar 以免干扰
if LIANJIA_COOKIE:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    COOKIES_ENABLED = False  # 计算或更新COOKIES_ENABLED中间数据，作为后续业务判断、统计或响应组装的输入。
    DOWNLOADER_MIDDLEWARES = {  # 初始化DOWNLOADER_MIDDLEWARES中间数据字典，用于承载接口返回或中间聚合结果。
        "housing_crawler.middlewares.CookieHeaderMiddleware": 543,  # 把housing_crawler.middlewares.CookieHeaderMiddleware字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
