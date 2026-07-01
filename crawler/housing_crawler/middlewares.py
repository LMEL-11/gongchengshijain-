"""下载中间件：把"浏览器登录态"的 Cookie 头附加到对 lianjia 的请求。

仅当 settings.LIANJIA_COOKIE 非空时启用（见 settings.py 末尾）。这是**使用用户本人登录
会话**的手段，不做任何反爬绕过（不破解验证码、不伪造身份）。请低频小量、自负账号风险。
"""


class CookieHeaderMiddleware:  # 定义 CookieHeaderMiddleware 类，封装对应的数据结构或业务行为。
    """若配置了 LIANJIA_COOKIE，则在每个 lianjia 请求上附加该 Cookie 头。"""  # 保留字符串内容，作为说明文本或页面展示文案。

    def __init__(self, cookie):  # 定义 __init__ 函数，集中处理这一段业务逻辑。
        """初始化对象实例并保存必要的运行状态。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        self.cookie = (cookie or "").strip()  # 设置 self.cookie 的值，供后续业务判断、查询或响应组装使用。

    @classmethod  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    def from_crawler(cls, crawler):  # 定义 from_crawler 函数，集中处理这一段业务逻辑。
        """从 Scrapy crawler 创建中间件实例。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        return cls(crawler.settings.get("LIANJIA_COOKIE", ""))  # 返回处理后的结果给调用方继续使用。

    def process_request(self, request, spider):  # 定义 process_request 函数，集中处理这一段业务逻辑。
        """为请求随机附加 Cookie 和 User-Agent 请求头。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        if self.cookie and "lianjia.com" in request.url:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            request.headers["Cookie"] = self.cookie  # 设置 request.headers["Cookie" 的值，供后续业务判断、查询或响应组装使用。
        return None  # 返回处理后的结果给调用方继续使用。
