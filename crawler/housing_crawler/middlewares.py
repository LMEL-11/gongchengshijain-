"""下载中间件：把"浏览器登录态"的 Cookie 头附加到对 lianjia 的请求。

仅当 settings.LIANJIA_COOKIE 非空时启用（见 settings.py 末尾）。这是**使用用户本人登录
会话**的手段，不做任何反爬绕过（不破解验证码、不伪造身份）。请低频小量、自负账号风险。
"""


class CookieHeaderMiddleware:  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """若配置了 LIANJIA_COOKIE，则在每个 lianjia 请求上附加该 Cookie 头。"""

    def __init__(self, cookie):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """初始化对象实例并保存必要的运行状态。"""
        self.cookie = (cookie or "").strip()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    @classmethod  # 把下方函数注册为路由、权限校验或框架回调入口。
    def from_crawler(cls, crawler):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """从 Scrapy crawler 创建中间件实例。"""
        return cls(crawler.settings.get("LIANJIA_COOKIE", ""))  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    def process_request(self, request, spider):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """为请求随机附加 Cookie 和 User-Agent 请求头。"""
        if self.cookie and "lianjia.com" in request.url:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            request.headers["Cookie"] = self.cookie  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
