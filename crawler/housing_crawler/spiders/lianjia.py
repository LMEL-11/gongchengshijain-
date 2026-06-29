"""链家二手房 Spider —— 爬取房源信息。

策略：**直接从列表页解析**（列表页含户型/面积/朝向/装修/楼层/总价/单价/小区/区域，
且实测可正常访问）。链家**详情页有验证码反爬**，默认不访问；如确有授权可
`-a follow_detail=1` 跟进详情页（届时可能被验证码拦截，本爬虫不做任何绕过）。

⚠️ 合规说明（详见 settings.py 顶部）：遵守 robots、低并发、下载延迟、抓取数量安全阀；
不破解验证码、不模拟登录、不轮换代理规避封禁。仅用于授权范围内的课程学习/演示。

用法：
  scrapy crawl lianjia -a city=bj -a city_name=北京 -a max_pages=5
  scrapy crawl lianjia -a city=jn -a city_name=济南 -a region=lixiaqu -a max_pages=3
"""
import re  # 导入本行所需的模块或对象。
from urllib.parse import urljoin  # 导入本行所需的模块或对象。

import scrapy  # 导入本行所需的模块或对象。

from housing_crawler.items import HousingItem  # 导入本行所需的模块或对象。

# 城市拼音缩写 -> 中文名（链家用城市子域名，如 bj.lianjia.com）。可用 -a city_name= 覆盖。
CITY_MAP = {  # 赋值或更新当前变量/字段。
    "bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "hz": "杭州",  # 设置当前数据项或参数。
    "cd": "成都", "nj": "南京", "wh": "武汉", "jn": "济南", "qd": "青岛",  # 设置当前数据项或参数。
    "tj": "天津", "cq": "重庆", "su": "苏州", "xa": "西安", "cs": "长沙",  # 设置当前数据项或参数。
    "zz": "郑州", "hf": "合肥", "dl": "大连", "xm": "厦门", "fz": "福州",  # 设置当前数据项或参数。
}  # 结束当前数据结构或调用块。

_DECORATIONS = {"毛坯", "简装", "精装", "豪装", "其他"}  # 赋值或更新当前变量/字段。


def _int(s):  # 声明函数或方法入口。
    """从文本中提取整数，无法解析时返回默认值。"""
    m = re.search(r"-?\d+", s or "")  # 赋值或更新当前变量/字段。
    return int(m.group()) if m else None  # 返回当前逻辑的处理结果。


def _float(s):  # 声明函数或方法入口。
    """从文本中提取浮点数，无法解析时返回默认值。"""
    m = re.search(r"-?\d+(?:\.\d+)?", (s or "").replace(",", ""))  # 赋值或更新当前变量/字段。
    return float(m.group()) if m else None  # 返回当前逻辑的处理结果。


def _rooms_halls(s):  # 声明函数或方法入口。
    """从户型文本中解析室和厅数量。"""
    s = s or ""  # 赋值或更新当前变量/字段。
    r = re.search(r"(\d+)\s*室", s)  # 赋值或更新当前变量/字段。
    h = re.search(r"(\d+)\s*厅", s)  # 赋值或更新当前变量/字段。
    return (int(r.group(1)) if r else None, int(h.group(1)) if h else None)  # 返回当前逻辑的处理结果。


def _parse_house_info(s):  # 声明函数或方法入口。
    """解析列表页 houseInfo，如：
    "1室1厅 | 39.58平米 | 东北 | 简装 | 中楼层(共25层) | 2009年 | 板楼"
    """
    out = {}  # 赋值或更新当前变量/字段。
    for p in [t.strip() for t in (s or "").split("|") if t.strip()]:  # 遍历集合中的每一项并执行处理。
        if re.search(r"\d+\s*室|\d+\s*厅", p):  # 根据条件判断是否进入该分支。
            out["rooms"], out["halls"] = _rooms_halls(p)  # 赋值或更新当前变量/字段。
        elif "平米" in p or "㎡" in p:  # 根据条件判断是否进入该分支。
            out["area"] = _float(p)  # 赋值或更新当前变量/字段。
        elif re.search(r"共\s*(\d+)\s*层", p):  # 根据条件判断是否进入该分支。
            out["total_floors"] = int(re.search(r"共\s*(\d+)\s*层", p).group(1))  # 赋值或更新当前变量/字段。
        elif re.search(r"(\d{4})\s*年", p):  # 根据条件判断是否进入该分支。
            out["build_year"] = int(re.search(r"(\d{4})\s*年", p).group(1))  # 赋值或更新当前变量/字段。
        elif p in _DECORATIONS:  # 根据条件判断是否进入该分支。
            out["decoration"] = p  # 赋值或更新当前变量/字段。
        elif p and set(p) <= set("东南西北 "):  # 根据条件判断是否进入该分支。
            out["orientation"] = p  # 赋值或更新当前变量/字段。
    return out  # 返回当前逻辑的处理结果。


class LianjiaSpider(scrapy.Spider):  # 声明类并定义相关数据或行为。
    """负责按城市抓取链家二手房列表和可选详情页数据。"""
    name = "lianjia"  # 赋值或更新当前变量/字段。
    allowed_domains = ["lianjia.com"]  # 赋值或更新当前变量/字段。

    def __init__(self, city="bj", city_name=None, max_pages=5, region="",  # 声明函数或方法入口。
                 follow_detail="0", auto_regions="0", max_regions="",  # 赋值或更新当前变量/字段。
                 all_cities="0", cities="", *args, **kwargs):  # 赋值或更新当前变量/字段。
        """初始化爬虫实例并保存运行参数。"""
        super().__init__(*args, **kwargs)  # 执行本行代码逻辑。
        self.city = city  # 赋值或更新当前变量/字段。
        self.city_name = city_name or CITY_MAP.get(city, city)  # 赋值或更新当前变量/字段。
        self.max_pages = int(max_pages)  # 赋值或更新当前变量/字段。
        self.region = (region or "").strip("/")  # 赋值或更新当前变量/字段。
        self.follow_detail = str(follow_detail).lower() in ("1", "true", "yes")  # 赋值或更新当前变量/字段。
        self.auto_regions = str(auto_regions).lower() in ("1", "true", "yes")  # 赋值或更新当前变量/字段。
        self.max_regions = int(max_regions) if str(max_regions).strip().isdigit() else None  # 赋值或更新当前变量/字段。
        self.all_cities = str(all_cities).lower() in ("1", "true", "yes")  # 赋值或更新当前变量/字段。
        self.cities_arg = (cities or "").strip()  # 赋值或更新当前变量/字段。

    def _city_list(self):  # 声明函数或方法入口。
        """多城市模式的 (子域名, 中文名) 列表。
        来源：-a cities=bj:北京,sh:上海 或 -a cities=bj,sh（名称查 CITY_MAP）；
              或 -a all_cities=1 读取 crawler/cities_all.txt（全国城市全集）。"""
        import os  # 导入本行所需的模块或对象。

        out, seen = [], set()  # 赋值或更新当前变量/字段。
        if self.cities_arg:  # 根据条件判断是否进入该分支。
            for tok in self.cities_arg.split(","):  # 遍历集合中的每一项并执行处理。
                tok = tok.strip()  # 赋值或更新当前变量/字段。
                if not tok:  # 根据条件判断是否进入该分支。
                    continue  # 跳过本轮循环剩余逻辑。
                sub, name = (tok.split(":", 1) + [None])[:2] if ":" in tok else (tok, None)  # 赋值或更新当前变量/字段。
                sub = sub.strip()  # 赋值或更新当前变量/字段。
                if sub and sub not in seen:  # 根据条件判断是否进入该分支。
                    seen.add(sub)  # 执行本行代码逻辑。
                    out.append((sub, (name or CITY_MAP.get(sub, sub)).strip()))  # 执行本行代码逻辑。
            return out  # 返回当前逻辑的处理结果。
        if self.all_cities:  # 根据条件判断是否进入该分支。
            path = os.path.join(os.path.dirname(__file__), "..", "..", "cities_all.txt")  # 赋值或更新当前变量/字段。
            try:  # 开始执行可能出现异常的逻辑。
                with open(path, encoding="utf-8") as fh:  # 进入上下文管理器并自动处理资源。
                    for line in fh:  # 遍历集合中的每一项并执行处理。
                        parts = line.rstrip("\n").split("\t")  # 赋值或更新当前变量/字段。
                        if len(parts) >= 2:  # 根据条件判断是否进入该分支。
                            sub, name = parts[0].strip(), parts[1].strip()  # 赋值或更新当前变量/字段。
                            # 跳过非城市子域名（资讯等）
                            if sub and sub not in seen and sub not in ("news", "www", "m"):  # 根据条件判断是否进入该分支。
                                seen.add(sub)  # 执行本行代码逻辑。
                                out.append((sub, name))  # 执行本行代码逻辑。
            except OSError:  # 捕获异常并执行错误处理。
                self.logger.error("未找到 cities_all.txt（先运行城市目录抓取生成）")  # 执行本行代码逻辑。
        return out  # 返回当前逻辑的处理结果。

    def start_requests(self):  # 声明函数或方法入口。
        """为每个城市和页面生成链家列表页初始请求。"""
        # 多城市/全国模式：每城仅抓开放首页（区页需登录、pg2 起有验证码，故不深入）
        city_list = self._city_list()  # 赋值或更新当前变量/字段。
        if city_list:  # 根据条件判断是否进入该分支。
            self.logger.info("多城市模式：共 %d 城，仅抓各城首页（约 30 条/城）", len(city_list))  # 执行本行代码逻辑。
            for sub, name in city_list:  # 遍历集合中的每一项并执行处理。
                base = f"https://{sub}.lianjia.com/ershoufang/"  # 赋值或更新当前变量/字段。
                yield scrapy.Request(  # 执行本行代码逻辑。
                    base, callback=self.parse_list, errback=self._on_city_error,  # 赋值或更新当前变量/字段。
                    meta={"page": 1, "base": base, "paginate": False, "city_name": name},  # 赋值或更新当前变量/字段。
                )  # 结束当前数据结构或调用块。
            return  # 返回当前逻辑的处理结果。

        landing = f"https://{self.city}.lianjia.com/ershoufang/"  # 赋值或更新当前变量/字段。
        # 自动板块模式：先解析城市的区/板块列表，再逐个抓各区首页
        if self.auto_regions and not self.region:  # 根据条件判断是否进入该分支。
            self.logger.info(  # 执行本行代码逻辑。
                "自动板块模式：解析 %s 的区/板块列表（入库城市名：%s）", landing, self.city_name  # 执行本行代码逻辑。
            )  # 结束当前数据结构或调用块。
            yield scrapy.Request(landing, callback=self.parse_regions)  # 赋值或更新当前变量/字段。
            return  # 返回当前逻辑的处理结果。

        path = f"ershoufang/{self.region}/" if self.region else "ershoufang/"  # 赋值或更新当前变量/字段。
        base = f"https://{self.city}.lianjia.com/{path}"  # 赋值或更新当前变量/字段。
        self.logger.info(  # 执行本行代码逻辑。
            "起始列表页：%s（入库城市名：%s，follow_detail=%s）",  # 赋值或更新当前变量/字段。
            base, self.city_name, self.follow_detail,  # 设置当前数据项或参数。
        )  # 结束当前数据结构或调用块。
        yield scrapy.Request(  # 执行本行代码逻辑。
            base, callback=self.parse_list, meta={"page": 1, "base": base, "paginate": True}  # 赋值或更新当前变量/字段。
        )  # 结束当前数据结构或调用块。

    def parse_regions(self, response):  # 声明函数或方法入口。
        """从城市 /ershoufang/ 落地页解析区/板块链接（形如 /ershoufang/{字母}/）。"""
        seen, regions = set(), []  # 赋值或更新当前变量/字段。
        for a in response.css("a"):  # 遍历集合中的每一项并执行处理。
            m = re.match(r"^/ershoufang/([a-z]+)/$", a.attrib.get("href", ""))  # 赋值或更新当前变量/字段。
            if m and m.group(1) not in seen:  # 根据条件判断是否进入该分支。
                seen.add(m.group(1))  # 执行本行代码逻辑。
                regions.append((m.group(1), (a.css("::text").get() or "").strip()))  # 设置当前数据项或参数。
        if self.max_regions:  # 根据条件判断是否进入该分支。
            regions = regions[: self.max_regions]  # 赋值或更新当前变量/字段。
        if not regions:  # 根据条件判断是否进入该分支。
            self.logger.warning("未解析到区/板块（可能被反爬拦截）：%s", response.url)  # 执行本行代码逻辑。
            return  # 返回当前逻辑的处理结果。
        self.logger.info(  # 执行本行代码逻辑。
            "发现 %d 个区/板块：%s", len(regions), "，".join(n or s for s, n in regions)  # 执行本行代码逻辑。
        )  # 结束当前数据结构或调用块。
        for slug, name in regions:  # 遍历集合中的每一项并执行处理。
            url = f"https://{self.city}.lianjia.com/ershoufang/{slug}/"  # 赋值或更新当前变量/字段。
            yield scrapy.Request(  # 执行本行代码逻辑。
                url,  # 设置当前数据项或参数。
                callback=self.parse_list,  # 赋值或更新当前变量/字段。
                meta={"page": 1, "base": url, "paginate": False, "region_name": name},  # 赋值或更新当前变量/字段。
            )  # 结束当前数据结构或调用块。

    def _on_city_error(self, failure):  # 声明函数或方法入口。
        """多城市模式下单个城市请求失败（DNS/超时等）只记录，不影响其他城市。"""
        req = getattr(failure, "request", None)  # 赋值或更新当前变量/字段。
        self.logger.warning("城市请求失败，跳过：%s（%s）",  # 设置当前数据项或参数。
                            getattr(req, "url", "?"), failure.value)  # 执行本行代码逻辑。

    def parse_list(self, response):  # 声明函数或方法入口。
        """解析链家列表页房源卡片并产出房源条目或详情请求。"""
        base = response.meta["base"]  # 赋值或更新当前变量/字段。
        page = response.meta["page"]  # 赋值或更新当前变量/字段。
        cards = response.css("ul.sellListContent li.clear")  # 赋值或更新当前变量/字段。
        if not cards:  # 根据条件判断是否进入该分支。
            city_name = response.meta.get("city_name") or self.city_name  # 赋值或更新当前变量/字段。
            self.logger.warning(  # 执行本行代码逻辑。
                "[%s] 列表页未解析到房源（可能被反爬/登录拦截或页面结构已变）：%s",  # 设置当前数据项或参数。
                city_name, response.url,  # 设置当前数据项或参数。
            )  # 结束当前数据结构或调用块。
            return  # 返回当前逻辑的处理结果。

        for li in cards:  # 遍历集合中的每一项并执行处理。
            href = li.css("div.title a::attr(href)").get()  # 赋值或更新当前变量/字段。
            house_info = " ".join(li.css(".houseInfo ::text").getall())  # 赋值或更新当前变量/字段。
            region_links = li.css(".positionInfo a::text").getall()  # 赋值或更新当前变量/字段。

            item = HousingItem()  # 赋值或更新当前变量/字段。
            item["source"] = "lianjia"  # 赋值或更新当前变量/字段。
            item["source_url"] = href            # 详情页 URL（作为去重键，不一定访问）
            item["listing_type"] = "二手房"  # 赋值或更新当前变量/字段。
            item["city"] = response.meta.get("city_name") or self.city_name  # 赋值或更新当前变量/字段。
            item["title"] = (li.css("div.title a::text").get() or "").strip() or house_info.strip()  # 赋值或更新当前变量/字段。
            item["total_price"] = _float(" ".join(li.css(".totalPrice ::text").getall()))  # 万元
            item["unit_price"] = (  # 赋值或更新当前变量/字段。
                _float(" ".join(li.css(".unitPrice ::text").getall()))  # 设置当前数据项或参数。
                or _float(li.css(".unitPrice::attr(data-price)").get())  # 设置当前数据项或参数。
            )  # 元/㎡
            # 自动板块模式下用区名作 district；否则用列表卡片里的商圈（最后一个链接）
            item["district"] = response.meta.get("region_name") or (  # 赋值或更新当前变量/字段。
                region_links[-1].strip() if region_links else None  # 执行本行代码逻辑。
            )  # 结束当前数据结构或调用块。

            info = _parse_house_info(house_info)  # 赋值或更新当前变量/字段。
            item["rooms"] = info.get("rooms")  # 赋值或更新当前变量/字段。
            item["halls"] = info.get("halls")  # 赋值或更新当前变量/字段。
            item["area"] = info.get("area")  # 赋值或更新当前变量/字段。
            item["orientation"] = info.get("orientation")  # 赋值或更新当前变量/字段。
            item["decoration"] = info.get("decoration")  # 赋值或更新当前变量/字段。
            item["total_floors"] = info.get("total_floors")  # 赋值或更新当前变量/字段。
            item["build_year"] = info.get("build_year")  # 赋值或更新当前变量/字段。

            if self.follow_detail and href:  # 根据条件判断是否进入该分支。
                # 可选：跟进详情页补充 楼层/经纬度（链家详情页有验证码，多半会被拦截）
                yield response.follow(href, callback=self.parse_detail, meta={"item": item})  # 赋值或更新当前变量/字段。
            else:  # 处理条件不满足时的兜底分支。
                yield item  # 执行本行代码逻辑。

        # 翻页（仅非板块模式；受 max_pages 与 CLOSESPIDER_ITEMCOUNT 限制）
        if response.meta.get("paginate", True) and page < self.max_pages:  # 根据条件判断是否进入该分支。
            nxt = page + 1  # 赋值或更新当前变量/字段。
            yield scrapy.Request(  # 执行本行代码逻辑。
                urljoin(base, f"pg{nxt}/"),  # 设置当前数据项或参数。
                callback=self.parse_list,  # 赋值或更新当前变量/字段。
                meta={"page": nxt, "base": base, "paginate": True,  # 赋值或更新当前变量/字段。
                      "region_name": response.meta.get("region_name")},  # 设置当前数据项或参数。
            )  # 结束当前数据结构或调用块。

    def parse_detail(self, response):  # 声明函数或方法入口。
        """可选的详情页补充解析（仅在 follow_detail=1 且未被验证码拦截时生效）。"""
        item = response.meta["item"]  # 赋值或更新当前变量/字段。

        # 命中验证码/跳转页则放弃补充，直接产出列表页已得到的数据
        if "captcha" in response.url:  # 根据条件判断是否进入该分支。
            self.logger.warning("详情页被验证码拦截，沿用列表页数据：%s", item["source_url"])  # 执行本行代码逻辑。
            yield item  # 执行本行代码逻辑。
            return  # 返回当前逻辑的处理结果。

        base_info = {}  # 赋值或更新当前变量/字段。
        for li in response.css(".introContent .base .content li"):  # 遍历集合中的每一项并执行处理。
            label = (li.css(".label::text").get() or "").strip()  # 赋值或更新当前变量/字段。
            texts = [t.strip() for t in li.css("::text").getall() if t.strip()]  # 赋值或更新当前变量/字段。
            value = texts[-1] if texts else ""  # 赋值或更新当前变量/字段。
            if label and value and value != label:  # 根据条件判断是否进入该分支。
                base_info[label] = value  # 赋值或更新当前变量/字段。

        if base_info.get("配备电梯"):  # 根据条件判断是否进入该分支。
            item["has_elevator"] = "有" in base_info["配备电梯"]  # 赋值或更新当前变量/字段。
        tf = re.search(r"共\s*(\d+)\s*层", base_info.get("所在楼层", ""))  # 赋值或更新当前变量/字段。
        if tf:  # 根据条件判断是否进入该分支。
            item["total_floors"] = int(tf.group(1))  # 赋值或更新当前变量/字段。

        pos = re.search(r"resblockPosition['\"]?\s*[:=]\s*['\"]([\d.]+),([\d.]+)", response.text)  # 赋值或更新当前变量/字段。
        if pos:  # 根据条件判断是否进入该分支。
            item["lng"] = float(pos.group(1))  # 赋值或更新当前变量/字段。
            item["lat"] = float(pos.group(2))  # 赋值或更新当前变量/字段。

        yield item  # 执行本行代码逻辑。
