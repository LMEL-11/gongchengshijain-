"""下载中间件：把"浏览器登录态"的 Cookie 头附加到对 lianjia 的请求。

仅当 settings.LIANJIA_COOKIE 非空时启用（见 settings.py 末尾）。这是**使用用户本人登录
会话**的手段，不做任何反爬绕过（不破解验证码、不伪造身份）。请低频小量、自负账号风险。
"""


class CookieHeaderMiddleware:  # 逐行注释：声明类并定义相关数据或行为。
    """若配置了 LIANJIA_COOKIE，则在每个 lianjia 请求上附加该 Cookie 头。"""

    def __init__(self, cookie):  # 逐行注释：声明函数或方法入口。
        """初始化对象实例并保存必要的运行状态。"""
        self.cookie = (cookie or "").strip()  # 逐行注释：赋值或更新当前变量/字段。

    @classmethod  # 逐行注释：应用装饰器配置路由、权限或命令。
    def from_crawler(cls, crawler):  # 逐行注释：声明函数或方法入口。
        """从 Scrapy crawler 创建中间件实例。"""
        return cls(crawler.settings.get("LIANJIA_COOKIE", ""))  # 逐行注释：返回当前逻辑的处理结果。

    def process_request(self, request, spider):  # 逐行注释：声明函数或方法入口。
        """为请求随机附加 Cookie 和 User-Agent 请求头。"""
        if self.cookie and "lianjia.com" in request.url:  # 逐行注释：根据条件判断是否进入该分支。
            request.headers["Cookie"] = self.cookie  # 逐行注释：赋值或更新当前变量/字段。
        return None  # 逐行注释：返回当前逻辑的处理结果。
