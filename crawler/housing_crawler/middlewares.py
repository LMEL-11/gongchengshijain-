"""下载中间件：把"浏览器登录态"的 Cookie 头附加到对 lianjia 的请求。

仅当 settings.LIANJIA_COOKIE 非空时启用（见 settings.py 末尾）。这是**使用用户本人登录
会话**的手段，不做任何反爬绕过（不破解验证码、不伪造身份）。请低频小量、自负账号风险。
"""


class CookieHeaderMiddleware:
    """若配置了 LIANJIA_COOKIE，则在每个 lianjia 请求上附加该 Cookie 头。"""

    def __init__(self, cookie):
        self.cookie = (cookie or "").strip()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get("LIANJIA_COOKIE", ""))

    def process_request(self, request, spider):
        if self.cookie and "lianjia.com" in request.url:
            request.headers["Cookie"] = self.cookie
        return None
