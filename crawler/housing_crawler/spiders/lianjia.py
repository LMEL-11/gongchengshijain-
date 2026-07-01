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
import re  # 导入 re 模块，为当前文件提供所需功能。
from urllib.parse import urljoin  # 从 urllib.parse 导入 urljoin，供本文件后续逻辑调用。

import scrapy  # 导入 scrapy 模块，为当前文件提供所需功能。

from housing_crawler.items import HousingItem  # 从 housing_crawler.items 导入 HousingItem，供本文件后续逻辑调用。

# 城市拼音缩写 -> 中文名（链家用城市子域名，如 bj.lianjia.com）。可用 -a city_name= 覆盖。
CITY_MAP = {  # 设置 CITY_MAP 的值，供后续业务判断、查询或响应组装使用。
    "bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "hz": "杭州",  # 保留字符串内容，作为说明文本或页面展示文案。
    "cd": "成都", "nj": "南京", "wh": "武汉", "jn": "济南", "qd": "青岛",  # 保留字符串内容，作为说明文本或页面展示文案。
    "tj": "天津", "cq": "重庆", "su": "苏州", "xa": "西安", "cs": "长沙",  # 保留字符串内容，作为说明文本或页面展示文案。
    "zz": "郑州", "hf": "合肥", "dl": "大连", "xm": "厦门", "fz": "福州",  # 保留字符串内容，作为说明文本或页面展示文案。
}  # 结束当前多行数据结构或函数调用。

_DECORATIONS = {"毛坯", "简装", "精装", "豪装", "其他"}  # 设置 _DECORATIONS 的值，供后续业务判断、查询或响应组装使用。


def _int(s):  # 定义 _int 函数，集中处理这一段业务逻辑。
    """从文本中提取整数，无法解析时返回默认值。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    m = re.search(r"-?\d+", s or "")  # 设置 m 的值，供后续业务判断、查询或响应组装使用。
    return int(m.group()) if m else None  # 返回处理后的结果给调用方继续使用。


def _float(s):  # 定义 _float 函数，集中处理这一段业务逻辑。
    """从文本中提取浮点数，无法解析时返回默认值。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    m = re.search(r"-?\d+(?:\.\d+)?", (s or "").replace(",", ""))  # 设置 m 的值，供后续业务判断、查询或响应组装使用。
    return float(m.group()) if m else None  # 返回处理后的结果给调用方继续使用。


def _rooms_halls(s):  # 定义 _rooms_halls 函数，集中处理这一段业务逻辑。
    """从户型文本中解析室和厅数量。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    s = s or ""  # 设置 s 的值，供后续业务判断、查询或响应组装使用。
    r = re.search(r"(\d+)\s*室", s)  # 设置 r 的值，供后续业务判断、查询或响应组装使用。
    h = re.search(r"(\d+)\s*厅", s)  # 设置 h 的值，供后续业务判断、查询或响应组装使用。
    return (int(r.group(1)) if r else None, int(h.group(1)) if h else None)  # 返回处理后的结果给调用方继续使用。


def _parse_house_info(s):  # 定义 _parse_house_info 函数，集中处理这一段业务逻辑。
    """解析列表页 houseInfo，如：
    "1室1厅 | 39.58平米 | 东北 | 简装 | 中楼层(共25层) | 2009年 | 板楼"
    """
    out = {}  # 设置 out 的值，供后续业务判断、查询或响应组装使用。
    for p in [t.strip() for t in (s or "").split("|") if t.strip()]:  # 遍历当前数据集合，逐项完成处理。
        if re.search(r"\d+\s*室|\d+\s*厅", p):  # 判断当前条件是否成立，决定是否进入对应处理分支。
            out["rooms"], out["halls"] = _rooms_halls(p)  # 设置 out["rooms"], out["halls" 的值，供后续业务判断、查询或响应组装使用。
        elif "平米" in p or "㎡" in p:  # 在前一个条件不成立时，继续判断这个补充分支。
            out["area"] = _float(p)  # 设置 out["area" 的值，供后续业务判断、查询或响应组装使用。
        elif re.search(r"共\s*(\d+)\s*层", p):  # 在前一个条件不成立时，继续判断这个补充分支。
            out["total_floors"] = int(re.search(r"共\s*(\d+)\s*层", p).group(1))  # 设置 out["total_floors" 的值，供后续业务判断、查询或响应组装使用。
        elif re.search(r"(\d{4})\s*年", p):  # 在前一个条件不成立时，继续判断这个补充分支。
            out["build_year"] = int(re.search(r"(\d{4})\s*年", p).group(1))  # 设置 out["build_year" 的值，供后续业务判断、查询或响应组装使用。
        elif p in _DECORATIONS:  # 在前一个条件不成立时，继续判断这个补充分支。
            out["decoration"] = p  # 设置 out["decoration" 的值，供后续业务判断、查询或响应组装使用。
        elif p and set(p) <= set("东南西北 "):  # 在前一个条件不成立时，继续判断这个补充分支。
            out["orientation"] = p  # 设置 out["orientation" 的值，供后续业务判断、查询或响应组装使用。
    return out  # 返回处理后的结果给调用方继续使用。


class LianjiaSpider(scrapy.Spider):  # 定义 LianjiaSpider(scrapy.Spider 类，封装对应的数据结构或业务行为。
    """负责按城市抓取链家二手房列表和可选详情页数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    name = "lianjia"  # 设置 name 的值，供后续业务判断、查询或响应组装使用。
    allowed_domains = ["lianjia.com"]  # 设置 allowed_domains 的值，供后续业务判断、查询或响应组装使用。

    def __init__(self, city="bj", city_name=None, max_pages=5, region="",  # 定义 __init__ 函数，集中处理这一段业务逻辑。
                 follow_detail="0", auto_regions="0", max_regions="",  # 设置 follow_detail 的值，供后续业务判断、查询或响应组装使用。
                 all_cities="0", cities="", *args, **kwargs):  # 设置 all_cities 的值，供后续业务判断、查询或响应组装使用。
        """初始化爬虫实例并保存运行参数。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        super().__init__(*args, **kwargs)  # 执行当前代码行对应的业务处理步骤。
        self.city = city  # 设置 self.city 的值，供后续业务判断、查询或响应组装使用。
        self.city_name = city_name or CITY_MAP.get(city, city)  # 设置 self.city_name 的值，供后续业务判断、查询或响应组装使用。
        self.max_pages = int(max_pages)  # 设置 self.max_pages 的值，供后续业务判断、查询或响应组装使用。
        self.region = (region or "").strip("/")  # 设置 self.region 的值，供后续业务判断、查询或响应组装使用。
        self.follow_detail = str(follow_detail).lower() in ("1", "true", "yes")  # 设置 self.follow_detail 的值，供后续业务判断、查询或响应组装使用。
        self.auto_regions = str(auto_regions).lower() in ("1", "true", "yes")  # 设置 self.auto_regions 的值，供后续业务判断、查询或响应组装使用。
        self.max_regions = int(max_regions) if str(max_regions).strip().isdigit() else None  # 设置 self.max_regions 的值，供后续业务判断、查询或响应组装使用。
        self.all_cities = str(all_cities).lower() in ("1", "true", "yes")  # 设置 self.all_cities 的值，供后续业务判断、查询或响应组装使用。
        self.cities_arg = (cities or "").strip()  # 设置 self.cities_arg 的值，供后续业务判断、查询或响应组装使用。

    def _city_list(self):  # 定义 _city_list 函数，集中处理这一段业务逻辑。
        """多城市模式的 (子域名, 中文名) 列表。
        来源：-a cities=bj:北京,sh:上海 或 -a cities=bj,sh（名称查 CITY_MAP）；
              或 -a all_cities=1 读取 crawler/cities_all.txt（全国城市全集）。"""
        import os  # 导入 os 模块，为当前文件提供所需功能。

        out, seen = [], set()  # 设置 out, seen 的值，供后续业务判断、查询或响应组装使用。
        if self.cities_arg:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            for tok in self.cities_arg.split(","):  # 遍历当前数据集合，逐项完成处理。
                tok = tok.strip()  # 设置 tok 的值，供后续业务判断、查询或响应组装使用。
                if not tok:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    continue  # 跳过当前循环项，继续处理下一项。
                sub, name = (tok.split(":", 1) + [None])[:2] if ":" in tok else (tok, None)  # 设置 sub, name 的值，供后续业务判断、查询或响应组装使用。
                sub = sub.strip()  # 设置 sub 的值，供后续业务判断、查询或响应组装使用。
                if sub and sub not in seen:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    seen.add(sub)  # 执行当前代码行对应的业务处理步骤。
                    out.append((sub, (name or CITY_MAP.get(sub, sub)).strip()))  # 执行当前代码行对应的业务处理步骤。
            return out  # 返回处理后的结果给调用方继续使用。
        if self.all_cities:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            path = os.path.join(os.path.dirname(__file__), "..", "..", "cities_all.txt")  # 把关联表纳入查询，获取跨表维度的数据。
            try:  # 开始执行可能抛出异常的代码块。
                with open(path, encoding="utf-8") as fh:  # 进入上下文管理流程，自动处理资源打开和释放。
                    for line in fh:  # 遍历当前数据集合，逐项完成处理。
                        parts = line.rstrip("\n").split("\t")  # 设置 parts 的值，供后续业务判断、查询或响应组装使用。
                        if len(parts) >= 2:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                            sub, name = parts[0].strip(), parts[1].strip()  # 设置 sub, name 的值，供后续业务判断、查询或响应组装使用。
                            # 跳过非城市子域名（资讯等）
                            if sub and sub not in seen and sub not in ("news", "www", "m"):  # 判断当前条件是否成立，决定是否进入对应处理分支。
                                seen.add(sub)  # 执行当前代码行对应的业务处理步骤。
                                out.append((sub, name))  # 执行当前代码行对应的业务处理步骤。
            except OSError:  # 捕获指定异常，并转入可控的错误处理流程。
                self.logger.error("未找到 cities_all.txt（先运行城市目录抓取生成）")  # 执行当前代码行对应的业务处理步骤。
        return out  # 返回处理后的结果给调用方继续使用。

    def start_requests(self):  # 定义 start_requests 函数，集中处理这一段业务逻辑。
        """为每个城市和页面生成链家列表页初始请求。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        # 多城市/全国模式：每城仅抓开放首页（区页需登录、pg2 起有验证码，故不深入）
        city_list = self._city_list()  # 设置 city_list 的值，供后续业务判断、查询或响应组装使用。
        if city_list:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            self.logger.info("多城市模式：共 %d 城，仅抓各城首页（约 30 条/城）", len(city_list))  # 执行当前代码行对应的业务处理步骤。
            for sub, name in city_list:  # 遍历当前数据集合，逐项完成处理。
                base = f"https://{sub}.lianjia.com/ershoufang/"  # 设置 base 的值，供后续业务判断、查询或响应组装使用。
                yield scrapy.Request(  # 产出当前请求或数据项，交给框架后续流程处理。
                    base, callback=self.parse_list, errback=self._on_city_error,  # 设置 base, callback 的值，供后续业务判断、查询或响应组装使用。
                    meta={"page": 1, "base": base, "paginate": False, "city_name": name},  # 设置 meta 的值，供后续业务判断、查询或响应组装使用。
                )  # 结束当前多行数据结构或函数调用。
            return  # 结束函数并返回空结果。

        landing = f"https://{self.city}.lianjia.com/ershoufang/"  # 设置 landing 的值，供后续业务判断、查询或响应组装使用。
        # 自动板块模式：先解析城市的区/板块列表，再逐个抓各区首页
        if self.auto_regions and not self.region:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            self.logger.info(  # 执行当前代码行对应的业务处理步骤。
                "自动板块模式：解析 %s 的区/板块列表（入库城市名：%s）", landing, self.city_name  # 保留字符串内容，作为说明文本或页面展示文案。
            )  # 结束当前多行数据结构或函数调用。
            yield scrapy.Request(landing, callback=self.parse_regions)  # 产出当前请求或数据项，交给框架后续流程处理。
            return  # 结束函数并返回空结果。

        path = f"ershoufang/{self.region}/" if self.region else "ershoufang/"  # 设置 path 的值，供后续业务判断、查询或响应组装使用。
        base = f"https://{self.city}.lianjia.com/{path}"  # 设置 base 的值，供后续业务判断、查询或响应组装使用。
        self.logger.info(  # 执行当前代码行对应的业务处理步骤。
            "起始列表页：%s（入库城市名：%s，follow_detail=%s）",  # 设置 "起始列表页：%s（入库城市名：%s，follow_detail 的值，供后续业务判断、查询或响应组装使用。
            base, self.city_name, self.follow_detail,  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        yield scrapy.Request(  # 产出当前请求或数据项，交给框架后续流程处理。
            base, callback=self.parse_list, meta={"page": 1, "base": base, "paginate": True}  # 设置 base, callback 的值，供后续业务判断、查询或响应组装使用。
        )  # 结束当前多行数据结构或函数调用。

    def parse_regions(self, response):  # 定义 parse_regions 函数，集中处理这一段业务逻辑。
        """从城市 /ershoufang/ 落地页解析区/板块链接（形如 /ershoufang/{字母}/）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        seen, regions = set(), []  # 设置 seen, regions 的值，供后续业务判断、查询或响应组装使用。
        for a in response.css("a"):  # 遍历当前数据集合，逐项完成处理。
            m = re.match(r"^/ershoufang/([a-z]+)/$", a.attrib.get("href", ""))  # 设置 m 的值，供后续业务判断、查询或响应组装使用。
            if m and m.group(1) not in seen:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                seen.add(m.group(1))  # 执行当前代码行对应的业务处理步骤。
                regions.append((m.group(1), (a.css("::text").get() or "").strip()))  # 执行当前代码行对应的业务处理步骤。
        if self.max_regions:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            regions = regions[: self.max_regions]  # 设置 regions 的值，供后续业务判断、查询或响应组装使用。
        if not regions:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            self.logger.warning("未解析到区/板块（可能被反爬拦截）：%s", response.url)  # 执行当前代码行对应的业务处理步骤。
            return  # 结束函数并返回空结果。
        self.logger.info(  # 执行当前代码行对应的业务处理步骤。
            "发现 %d 个区/板块：%s", len(regions), "，".join(n or s for s, n in regions)  # 把关联表纳入查询，获取跨表维度的数据。
        )  # 结束当前多行数据结构或函数调用。
        for slug, name in regions:  # 遍历当前数据集合，逐项完成处理。
            url = f"https://{self.city}.lianjia.com/ershoufang/{slug}/"  # 设置 url 的值，供后续业务判断、查询或响应组装使用。
            yield scrapy.Request(  # 产出当前请求或数据项，交给框架后续流程处理。
                url,  # 执行当前代码行对应的业务处理步骤。
                callback=self.parse_list,  # 设置 callback 的值，供后续业务判断、查询或响应组装使用。
                meta={"page": 1, "base": url, "paginate": False, "region_name": name},  # 设置 meta 的值，供后续业务判断、查询或响应组装使用。
            )  # 结束当前多行数据结构或函数调用。

    def _on_city_error(self, failure):  # 定义 _on_city_error 函数，集中处理这一段业务逻辑。
        """多城市模式下单个城市请求失败（DNS/超时等）只记录，不影响其他城市。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        req = getattr(failure, "request", None)  # 设置 req 的值，供后续业务判断、查询或响应组装使用。
        self.logger.warning("城市请求失败，跳过：%s（%s）",  # 执行当前代码行对应的业务处理步骤。
                            getattr(req, "url", "?"), failure.value)  # 执行当前代码行对应的业务处理步骤。

    def parse_list(self, response):  # 定义 parse_list 函数，集中处理这一段业务逻辑。
        """解析链家列表页房源卡片并产出房源条目或详情请求。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        base = response.meta["base"]  # 设置 base 的值，供后续业务判断、查询或响应组装使用。
        page = response.meta["page"]  # 设置 page 的值，供后续业务判断、查询或响应组装使用。
        cards = response.css("ul.sellListContent li.clear")  # 设置 cards 的值，供后续业务判断、查询或响应组装使用。
        if not cards:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            city_name = response.meta.get("city_name") or self.city_name  # 设置 city_name 的值，供后续业务判断、查询或响应组装使用。
            self.logger.warning(  # 执行当前代码行对应的业务处理步骤。
                "[%s] 列表页未解析到房源（可能被反爬/登录拦截或页面结构已变）：%s",  # 保留字符串内容，作为说明文本或页面展示文案。
                city_name, response.url,  # 执行当前代码行对应的业务处理步骤。
            )  # 结束当前多行数据结构或函数调用。
            return  # 结束函数并返回空结果。

        for li in cards:  # 遍历当前数据集合，逐项完成处理。
            href = li.css("div.title a::attr(href)").get()  # 设置 href 的值，供后续业务判断、查询或响应组装使用。
            house_info = " ".join(li.css(".houseInfo ::text").getall())  # 把关联表纳入查询，获取跨表维度的数据。
            region_links = li.css(".positionInfo a::text").getall()  # 设置 region_links 的值，供后续业务判断、查询或响应组装使用。

            item = HousingItem()  # 设置 item 的值，供后续业务判断、查询或响应组装使用。
            item["source"] = "lianjia"  # 设置 item["source" 的值，供后续业务判断、查询或响应组装使用。
            item["source_url"] = href  # 设置 item["source_url" 的值，供后续业务判断、查询或响应组装使用。
            item["listing_type"] = "二手房"  # 设置 item["listing_type" 的值，供后续业务判断、查询或响应组装使用。
            item["city"] = response.meta.get("city_name") or self.city_name  # 设置 item["city" 的值，供后续业务判断、查询或响应组装使用。
            item["title"] = (li.css("div.title a::text").get() or "").strip() or house_info.strip()  # 设置 item["title" 的值，供后续业务判断、查询或响应组装使用。
            item["total_price"] = _float(" ".join(li.css(".totalPrice ::text").getall()))  # 把关联表纳入查询，获取跨表维度的数据。
            item["unit_price"] = (  # 设置 item["unit_price" 的值，供后续业务判断、查询或响应组装使用。
                _float(" ".join(li.css(".unitPrice ::text").getall()))  # 把关联表纳入查询，获取跨表维度的数据。
                or _float(li.css(".unitPrice::attr(data-price)").get())  # 执行当前代码行对应的业务处理步骤。
            )  # 结束当前多行数据结构或函数调用。
            # 自动板块模式下用区名作 district；否则用列表卡片里的商圈（最后一个链接）
            item["district"] = response.meta.get("region_name") or (  # 设置 item["district" 的值，供后续业务判断、查询或响应组装使用。
                region_links[-1].strip() if region_links else None  # 执行当前代码行对应的业务处理步骤。
            )  # 结束当前多行数据结构或函数调用。

            info = _parse_house_info(house_info)  # 设置 info 的值，供后续业务判断、查询或响应组装使用。
            item["rooms"] = info.get("rooms")  # 设置 item["rooms" 的值，供后续业务判断、查询或响应组装使用。
            item["halls"] = info.get("halls")  # 设置 item["halls" 的值，供后续业务判断、查询或响应组装使用。
            item["area"] = info.get("area")  # 设置 item["area" 的值，供后续业务判断、查询或响应组装使用。
            item["orientation"] = info.get("orientation")  # 设置 item["orientation" 的值，供后续业务判断、查询或响应组装使用。
            item["decoration"] = info.get("decoration")  # 设置 item["decoration" 的值，供后续业务判断、查询或响应组装使用。
            item["total_floors"] = info.get("total_floors")  # 设置 item["total_floors" 的值，供后续业务判断、查询或响应组装使用。
            item["build_year"] = info.get("build_year")  # 设置 item["build_year" 的值，供后续业务判断、查询或响应组装使用。

            if self.follow_detail and href:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                # 可选：跟进详情页补充 楼层/经纬度（链家详情页有验证码，多半会被拦截）
                yield response.follow(href, callback=self.parse_detail, meta={"item": item})  # 产出当前请求或数据项，交给框架后续流程处理。
            else:  # 处理前面条件都未命中的兜底分支。
                yield item  # 产出当前请求或数据项，交给框架后续流程处理。

        # 翻页（仅非板块模式；受 max_pages 与 CLOSESPIDER_ITEMCOUNT 限制）
        if response.meta.get("paginate", True) and page < self.max_pages:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            nxt = page + 1  # 设置 nxt 的值，供后续业务判断、查询或响应组装使用。
            yield scrapy.Request(  # 产出当前请求或数据项，交给框架后续流程处理。
                urljoin(base, f"pg{nxt}/"),  # 执行当前代码行对应的业务处理步骤。
                callback=self.parse_list,  # 设置 callback 的值，供后续业务判断、查询或响应组装使用。
                meta={"page": nxt, "base": base, "paginate": True,  # 设置 meta 的值，供后续业务判断、查询或响应组装使用。
                      "region_name": response.meta.get("region_name")},  # 保留字符串内容，作为说明文本或页面展示文案。
            )  # 结束当前多行数据结构或函数调用。

    def parse_detail(self, response):  # 定义 parse_detail 函数，集中处理这一段业务逻辑。
        """可选的详情页补充解析（仅在 follow_detail=1 且未被验证码拦截时生效）。"""  # 设置 """可选的详情页补充解析（仅在 follow_detail 的值，供后续业务判断、查询或响应组装使用。
        item = response.meta["item"]  # 设置 item 的值，供后续业务判断、查询或响应组装使用。

        # 命中验证码/跳转页则放弃补充，直接产出列表页已得到的数据
        if "captcha" in response.url:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            self.logger.warning("详情页被验证码拦截，沿用列表页数据：%s", item["source_url"])  # 执行当前代码行对应的业务处理步骤。
            yield item  # 产出当前请求或数据项，交给框架后续流程处理。
            return  # 结束函数并返回空结果。

        base_info = {}  # 设置 base_info 的值，供后续业务判断、查询或响应组装使用。
        for li in response.css(".introContent .base .content li"):  # 遍历当前数据集合，逐项完成处理。
            label = (li.css(".label::text").get() or "").strip()  # 设置 label 的值，供后续业务判断、查询或响应组装使用。
            texts = [t.strip() for t in li.css("::text").getall() if t.strip()]  # 设置 texts 的值，供后续业务判断、查询或响应组装使用。
            value = texts[-1] if texts else ""  # 设置 value 的值，供后续业务判断、查询或响应组装使用。
            if label and value and value != label:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                base_info[label] = value  # 设置 base_info[label 的值，供后续业务判断、查询或响应组装使用。

        if base_info.get("配备电梯"):  # 判断当前条件是否成立，决定是否进入对应处理分支。
            item["has_elevator"] = "有" in base_info["配备电梯"]  # 设置 item["has_elevator" 的值，供后续业务判断、查询或响应组装使用。
        tf = re.search(r"共\s*(\d+)\s*层", base_info.get("所在楼层", ""))  # 设置 tf 的值，供后续业务判断、查询或响应组装使用。
        if tf:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            item["total_floors"] = int(tf.group(1))  # 设置 item["total_floors" 的值，供后续业务判断、查询或响应组装使用。

        pos = re.search(r"resblockPosition['\"]?\s*[:=]\s*['\"]([\d.]+),([\d.]+)", response.text)  # 设置 pos 的值，供后续业务判断、查询或响应组装使用。
        if pos:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            item["lng"] = float(pos.group(1))  # 设置 item["lng" 的值，供后续业务判断、查询或响应组装使用。
            item["lat"] = float(pos.group(2))  # 设置 item["lat" 的值，供后续业务判断、查询或响应组装使用。

        yield item  # 产出当前请求或数据项，交给框架后续流程处理。
