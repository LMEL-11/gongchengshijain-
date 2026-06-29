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
import re  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from urllib.parse import urljoin  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

import scrapy  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from housing_crawler.items import HousingItem  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

# 城市拼音缩写 -> 中文名（链家用城市子域名，如 bj.lianjia.com）。可用 -a city_name= 覆盖。
CITY_MAP = {  # 初始化CITY_MAP中间数据字典，用于承载接口返回或中间聚合结果。
    "bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "hz": "杭州",  # 把bj字段写入响应数据，供前端页面、图表或后续接口读取。
    "cd": "成都", "nj": "南京", "wh": "武汉", "jn": "济南", "qd": "青岛",  # 把cd字段写入响应数据，供前端页面、图表或后续接口读取。
    "tj": "天津", "cq": "重庆", "su": "苏州", "xa": "西安", "cs": "长沙",  # 把tj字段写入响应数据，供前端页面、图表或后续接口读取。
    "zz": "郑州", "hf": "合肥", "dl": "大连", "xm": "厦门", "fz": "福州",  # 把zz字段写入响应数据，供前端页面、图表或后续接口读取。
}  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

_DECORATIONS = {"毛坯", "简装", "精装", "豪装", "其他"}  # 初始化_DECORATIONS中间数据字典，用于承载接口返回或中间聚合结果。


def _int(s):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从文本中提取整数，无法解析时返回默认值。"""
    m = re.search(r"-?\d+", s or "")  # 计算或更新m中间数据，作为后续业务判断、统计或响应组装的输入。
    return int(m.group()) if m else None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _float(s):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从文本中提取浮点数，无法解析时返回默认值。"""
    m = re.search(r"-?\d+(?:\.\d+)?", (s or "").replace(",", ""))  # 计算或更新m中间数据，作为后续业务判断、统计或响应组装的输入。
    return float(m.group()) if m else None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _rooms_halls(s):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从户型文本中解析室和厅数量。"""
    s = s or ""  # 计算或更新s中间数据，作为后续业务判断、统计或响应组装的输入。
    r = re.search(r"(\d+)\s*室", s)  # 计算或更新r中间数据，作为后续业务判断、统计或响应组装的输入。
    h = re.search(r"(\d+)\s*厅", s)  # 计算或更新h中间数据，作为后续业务判断、统计或响应组装的输入。
    return (int(r.group(1)) if r else None, int(h.group(1)) if h else None)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _parse_house_info(s):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """解析列表页 houseInfo，如：
    "1室1厅 | 39.58平米 | 东北 | 简装 | 中楼层(共25层) | 2009年 | 板楼"
    """
    out = {}  # 初始化out中间数据字典，用于承载接口返回或中间聚合结果。
    for p in [t.strip() for t in (s or "").split("|") if t.strip()]:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        if re.search(r"\d+\s*室|\d+\s*厅", p):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            out["rooms"], out["halls"] = _rooms_halls(p)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        elif "平米" in p or "㎡" in p:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            out["area"] = _float(p)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        elif re.search(r"共\s*(\d+)\s*层", p):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            out["total_floors"] = int(re.search(r"共\s*(\d+)\s*层", p).group(1))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        elif re.search(r"(\d{4})\s*年", p):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            out["build_year"] = int(re.search(r"(\d{4})\s*年", p).group(1))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        elif p in _DECORATIONS:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            out["decoration"] = p  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        elif p and set(p) <= set("东南西北 "):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            out["orientation"] = p  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return out  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


class LianjiaSpider(scrapy.Spider):  # 定义业务类或数据模型，封装该模块的数据结构与处理行为。
    """负责按城市抓取链家二手房列表和可选详情页数据。"""
    name = "lianjia"  # 计算或更新name中间数据，作为后续业务判断、统计或响应组装的输入。
    allowed_domains = ["lianjia.com"]  # 初始化allowed_domains中间数据列表，用于收集清洗后的多条业务数据。

    def __init__(self, city="bj", city_name=None, max_pages=5, region="",  # 定义函数入口，将输入参数转换为业务数据或接口响应。
                 follow_detail="0", auto_regions="0", max_regions="",  # 计算或更新follow_detail中间数据，作为后续业务判断、统计或响应组装的输入。
                 all_cities="0", cities="", *args, **kwargs):  # 计算或更新all_cities中间数据，作为后续业务判断、统计或响应组装的输入。
        """初始化爬虫实例并保存运行参数。"""
        super().__init__(*args, **kwargs)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.city = city  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.city_name = city_name or CITY_MAP.get(city, city)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.max_pages = int(max_pages)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.region = (region or "").strip("/")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.follow_detail = str(follow_detail).lower() in ("1", "true", "yes")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.auto_regions = str(auto_regions).lower() in ("1", "true", "yes")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.max_regions = int(max_regions) if str(max_regions).strip().isdigit() else None  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.all_cities = str(all_cities).lower() in ("1", "true", "yes")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        self.cities_arg = (cities or "").strip()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    def _city_list(self):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """多城市模式的 (子域名, 中文名) 列表。
        来源：-a cities=bj:北京,sh:上海 或 -a cities=bj,sh（名称查 CITY_MAP）；
              或 -a all_cities=1 读取 crawler/cities_all.txt（全国城市全集）。"""
        import os  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

        out, seen = [], set()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        if self.cities_arg:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            for tok in self.cities_arg.split(","):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
                tok = tok.strip()  # 计算或更新tok中间数据，作为后续业务判断、统计或响应组装的输入。
                if not tok:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                    continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                sub, name = (tok.split(":", 1) + [None])[:2] if ":" in tok else (tok, None)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                sub = sub.strip()  # 计算或更新sub中间数据，作为后续业务判断、统计或响应组装的输入。
                if sub and sub not in seen:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                    seen.add(sub)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                    out.append((sub, (name or CITY_MAP.get(sub, sub)).strip()))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            return out  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        if self.all_cities:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            path = os.path.join(os.path.dirname(__file__), "..", "..", "cities_all.txt")  # 计算或更新地图钻取路径，作为后续业务判断、统计或响应组装的输入。
            try:  # 开始执行可能失败的外部访问、数据转换或数据库操作。
                with open(path, encoding="utf-8") as fh:  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
                    for line in fh:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
                        parts = line.rstrip("\n").split("\t")  # 计算或更新parts中间数据，作为后续业务判断、统计或响应组装的输入。
                        if len(parts) >= 2:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                            sub, name = parts[0].strip(), parts[1].strip()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                            # 跳过非城市子域名（资讯等）
                            if sub and sub not in seen and sub not in ("news", "www", "m"):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                                seen.add(sub)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                                out.append((sub, name))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            except OSError:  # 捕获异常并转换为可控的错误处理或提示信息。
                self.logger.error("未找到 cities_all.txt（先运行城市目录抓取生成）")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        return out  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    def start_requests(self):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """为每个城市和页面生成链家列表页初始请求。"""
        # 多城市/全国模式：每城仅抓开放首页（区页需登录、pg2 起有验证码，故不深入）
        city_list = self._city_list()  # 计算或更新city_list中间数据，作为后续业务判断、统计或响应组装的输入。
        if city_list:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            self.logger.info("多城市模式：共 %d 城，仅抓各城首页（约 30 条/城）", len(city_list))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            for sub, name in city_list:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
                base = f"https://{sub}.lianjia.com/ershoufang/"  # 计算或更新base中间数据，作为后续业务判断、统计或响应组装的输入。
                yield scrapy.Request(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                    base, callback=self.parse_list, errback=self._on_city_error,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                    meta={"page": 1, "base": base, "paginate": False, "city_name": name},  # 初始化meta中间数据字典，用于承载接口返回或中间聚合结果。
                )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            return  # 提前结束当前处理流程，避免无效数据继续向后流转。

        landing = f"https://{self.city}.lianjia.com/ershoufang/"  # 计算或更新landing中间数据，作为后续业务判断、统计或响应组装的输入。
        # 自动板块模式：先解析城市的区/板块列表，再逐个抓各区首页
        if self.auto_regions and not self.region:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            self.logger.info(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                "自动板块模式：解析 %s 的区/板块列表（入库城市名：%s）", landing, self.city_name  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            yield scrapy.Request(landing, callback=self.parse_regions)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            return  # 提前结束当前处理流程，避免无效数据继续向后流转。

        path = f"ershoufang/{self.region}/" if self.region else "ershoufang/"  # 计算或更新地图钻取路径，作为后续业务判断、统计或响应组装的输入。
        base = f"https://{self.city}.lianjia.com/{path}"  # 计算或更新base中间数据，作为后续业务判断、统计或响应组装的输入。
        self.logger.info(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "起始列表页：%s（入库城市名：%s，follow_detail=%s）",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            base, self.city_name, self.follow_detail,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        yield scrapy.Request(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            base, callback=self.parse_list, meta={"page": 1, "base": base, "paginate": True}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    def parse_regions(self, response):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """从城市 /ershoufang/ 落地页解析区/板块链接（形如 /ershoufang/{字母}/）。"""
        seen, regions = set(), []  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        for a in response.css("a"):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            m = re.match(r"^/ershoufang/([a-z]+)/$", a.attrib.get("href", ""))  # 计算或更新m中间数据，作为后续业务判断、统计或响应组装的输入。
            if m and m.group(1) not in seen:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                seen.add(m.group(1))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                regions.append((m.group(1), (a.css("::text").get() or "").strip()))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        if self.max_regions:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            regions = regions[: self.max_regions]  # 计算或更新regions中间数据，作为后续业务判断、统计或响应组装的输入。
        if not regions:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            self.logger.warning("未解析到区/板块（可能被反爬拦截）：%s", response.url)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            return  # 提前结束当前处理流程，避免无效数据继续向后流转。
        self.logger.info(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "发现 %d 个区/板块：%s", len(regions), "，".join(n or s for s, n in regions)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        for slug, name in regions:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            url = f"https://{self.city}.lianjia.com/ershoufang/{slug}/"  # 计算或更新url中间数据，作为后续业务判断、统计或响应组装的输入。
            yield scrapy.Request(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                url,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                callback=self.parse_list,  # 计算或更新callback中间数据，作为后续业务判断、统计或响应组装的输入。
                meta={"page": 1, "base": url, "paginate": False, "region_name": name},  # 初始化meta中间数据字典，用于承载接口返回或中间聚合结果。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    def _on_city_error(self, failure):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """多城市模式下单个城市请求失败（DNS/超时等）只记录，不影响其他城市。"""
        req = getattr(failure, "request", None)  # 计算或更新req中间数据，作为后续业务判断、统计或响应组装的输入。
        self.logger.warning("城市请求失败，跳过：%s（%s）",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                            getattr(req, "url", "?"), failure.value)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    def parse_list(self, response):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """解析链家列表页房源卡片并产出房源条目或详情请求。"""
        base = response.meta["base"]  # 计算或更新base中间数据，作为后续业务判断、统计或响应组装的输入。
        page = response.meta["page"]  # 计算或更新当前页码，作为后续业务判断、统计或响应组装的输入。
        cards = response.css("ul.sellListContent li.clear")  # 计算或更新cards中间数据，作为后续业务判断、统计或响应组装的输入。
        if not cards:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            city_name = response.meta.get("city_name") or self.city_name  # 计算或更新城市名称，作为后续业务判断、统计或响应组装的输入。
            self.logger.warning(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                "[%s] 列表页未解析到房源（可能被反爬/登录拦截或页面结构已变）：%s",  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                city_name, response.url,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            return  # 提前结束当前处理流程，避免无效数据继续向后流转。

        for li in cards:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            href = li.css("div.title a::attr(href)").get()  # 计算或更新href中间数据，作为后续业务判断、统计或响应组装的输入。
            house_info = " ".join(li.css(".houseInfo ::text").getall())  # 计算或更新house_info中间数据，作为后续业务判断、统计或响应组装的输入。
            region_links = li.css(".positionInfo a::text").getall()  # 计算或更新region_links中间数据，作为后续业务判断、统计或响应组装的输入。

            item = HousingItem()  # 计算或更新单条数据，作为后续业务判断、统计或响应组装的输入。
            item["source"] = "lianjia"  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["source_url"] = href            # 详情页 URL（作为去重键，不一定访问）
            item["listing_type"] = "二手房"  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["city"] = response.meta.get("city_name") or self.city_name  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["title"] = (li.css("div.title a::text").get() or "").strip() or house_info.strip()  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["total_price"] = _float(" ".join(li.css(".totalPrice ::text").getall()))  # 万元
            item["unit_price"] = (  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                _float(" ".join(li.css(".unitPrice ::text").getall()))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                or _float(li.css(".unitPrice::attr(data-price)").get())  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            )  # 元/㎡
            # 自动板块模式下用区名作 district；否则用列表卡片里的商圈（最后一个链接）
            item["district"] = response.meta.get("region_name") or (  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                region_links[-1].strip() if region_links else None  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

            info = _parse_house_info(house_info)  # 计算或更新info中间数据，作为后续业务判断、统计或响应组装的输入。
            item["rooms"] = info.get("rooms")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["halls"] = info.get("halls")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["area"] = info.get("area")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["orientation"] = info.get("orientation")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["decoration"] = info.get("decoration")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["total_floors"] = info.get("total_floors")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["build_year"] = info.get("build_year")  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

            if self.follow_detail and href:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                # 可选：跟进详情页补充 楼层/经纬度（链家详情页有验证码，多半会被拦截）
                yield response.follow(href, callback=self.parse_detail, meta={"item": item})  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            else:  # 处理前面条件未命中的数据场景，保证流程有兜底路径。
                yield item  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        # 翻页（仅非板块模式；受 max_pages 与 CLOSESPIDER_ITEMCOUNT 限制）
        if response.meta.get("paginate", True) and page < self.max_pages:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            nxt = page + 1  # 计算或更新nxt中间数据，作为后续业务判断、统计或响应组装的输入。
            yield scrapy.Request(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                urljoin(base, f"pg{nxt}/"),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                callback=self.parse_list,  # 计算或更新callback中间数据，作为后续业务判断、统计或响应组装的输入。
                meta={"page": nxt, "base": base, "paginate": True,  # 初始化meta中间数据字典，用于承载接口返回或中间聚合结果。
                      "region_name": response.meta.get("region_name")},  # 把region_name字段写入响应数据，供前端页面、图表或后续接口读取。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    def parse_detail(self, response):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
        """可选的详情页补充解析（仅在 follow_detail=1 且未被验证码拦截时生效）。"""
        item = response.meta["item"]  # 计算或更新单条数据，作为后续业务判断、统计或响应组装的输入。

        # 命中验证码/跳转页则放弃补充，直接产出列表页已得到的数据
        if "captcha" in response.url:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            self.logger.warning("详情页被验证码拦截，沿用列表页数据：%s", item["source_url"])  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            yield item  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            return  # 提前结束当前处理流程，避免无效数据继续向后流转。

        base_info = {}  # 初始化base_info中间数据字典，用于承载接口返回或中间聚合结果。
        for li in response.css(".introContent .base .content li"):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            label = (li.css(".label::text").get() or "").strip()  # 计算或更新label中间数据，作为后续业务判断、统计或响应组装的输入。
            texts = [t.strip() for t in li.css("::text").getall() if t.strip()]  # 初始化texts中间数据列表，用于收集清洗后的多条业务数据。
            value = texts[-1] if texts else ""  # 计算或更新value中间数据，作为后续业务判断、统计或响应组装的输入。
            if label and value and value != label:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                base_info[label] = value  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        if base_info.get("配备电梯"):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            item["has_elevator"] = "有" in base_info["配备电梯"]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        tf = re.search(r"共\s*(\d+)\s*层", base_info.get("所在楼层", ""))  # 计算或更新tf中间数据，作为后续业务判断、统计或响应组装的输入。
        if tf:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            item["total_floors"] = int(tf.group(1))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        pos = re.search(r"resblockPosition['\"]?\s*[:=]\s*['\"]([\d.]+),([\d.]+)", response.text)  # 计算或更新pos中间数据，作为后续业务判断、统计或响应组装的输入。
        if pos:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            item["lng"] = float(pos.group(1))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item["lat"] = float(pos.group(2))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

        yield item  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
