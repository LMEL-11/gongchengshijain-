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
import re
from urllib.parse import urljoin

import scrapy

from housing_crawler.items import HousingItem

# 城市拼音缩写 -> 中文名（链家用城市子域名，如 bj.lianjia.com）。可用 -a city_name= 覆盖。
CITY_MAP = {
    "bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "hz": "杭州",
    "cd": "成都", "nj": "南京", "wh": "武汉", "jn": "济南", "qd": "青岛",
    "tj": "天津", "cq": "重庆", "su": "苏州", "xa": "西安", "cs": "长沙",
    "zz": "郑州", "hf": "合肥", "dl": "大连", "xm": "厦门", "fz": "福州",
}

_DECORATIONS = {"毛坯", "简装", "精装", "豪装", "其他"}


def _int(s):
    """从文本中提取整数，无法解析时返回默认值。"""
    m = re.search(r"-?\d+", s or "")
    return int(m.group()) if m else None


def _float(s):
    """从文本中提取浮点数，无法解析时返回默认值。"""
    m = re.search(r"-?\d+(?:\.\d+)?", (s or "").replace(",", ""))
    return float(m.group()) if m else None


def _rooms_halls(s):
    """从户型文本中解析室和厅数量。"""
    s = s or ""
    r = re.search(r"(\d+)\s*室", s)
    h = re.search(r"(\d+)\s*厅", s)
    return (int(r.group(1)) if r else None, int(h.group(1)) if h else None)


def _parse_house_info(s):
    """解析列表页 houseInfo，如：
    "1室1厅 | 39.58平米 | 东北 | 简装 | 中楼层(共25层) | 2009年 | 板楼"
    """
    out = {}
    for p in [t.strip() for t in (s or "").split("|") if t.strip()]:
        if re.search(r"\d+\s*室|\d+\s*厅", p):
            out["rooms"], out["halls"] = _rooms_halls(p)
        elif "平米" in p or "㎡" in p:
            out["area"] = _float(p)
        elif re.search(r"共\s*(\d+)\s*层", p):
            out["total_floors"] = int(re.search(r"共\s*(\d+)\s*层", p).group(1))
        elif re.search(r"(\d{4})\s*年", p):
            out["build_year"] = int(re.search(r"(\d{4})\s*年", p).group(1))
        elif p in _DECORATIONS:
            out["decoration"] = p
        elif p and set(p) <= set("东南西北 "):
            out["orientation"] = p
    return out


class LianjiaSpider(scrapy.Spider):
    """负责按城市抓取链家二手房列表和可选详情页数据。"""
    name = "lianjia"
    allowed_domains = ["lianjia.com"]

    def __init__(self, city="bj", city_name=None, max_pages=5, region="",
                 follow_detail="0", auto_regions="0", max_regions="",
                 all_cities="0", cities="", *args, **kwargs):
        """初始化爬虫实例并保存运行参数。"""
        super().__init__(*args, **kwargs)
        self.city = city
        self.city_name = city_name or CITY_MAP.get(city, city)
        self.max_pages = int(max_pages)
        self.region = (region or "").strip("/")
        self.follow_detail = str(follow_detail).lower() in ("1", "true", "yes")
        self.auto_regions = str(auto_regions).lower() in ("1", "true", "yes")
        self.max_regions = int(max_regions) if str(max_regions).strip().isdigit() else None
        self.all_cities = str(all_cities).lower() in ("1", "true", "yes")
        self.cities_arg = (cities or "").strip()

    def _city_list(self):
        """多城市模式的 (子域名, 中文名) 列表。
        来源：-a cities=bj:北京,sh:上海 或 -a cities=bj,sh（名称查 CITY_MAP）；
              或 -a all_cities=1 读取 crawler/cities_all.txt（全国城市全集）。"""
        import os

        out, seen = [], set()
        if self.cities_arg:
            for tok in self.cities_arg.split(","):
                tok = tok.strip()
                if not tok:
                    continue
                sub, name = (tok.split(":", 1) + [None])[:2] if ":" in tok else (tok, None)
                sub = sub.strip()
                if sub and sub not in seen:
                    seen.add(sub)
                    out.append((sub, (name or CITY_MAP.get(sub, sub)).strip()))
            return out
        if self.all_cities:
            path = os.path.join(os.path.dirname(__file__), "..", "..", "cities_all.txt")
            try:
                with open(path, encoding="utf-8") as fh:
                    for line in fh:
                        parts = line.rstrip("\n").split("\t")
                        if len(parts) >= 2:
                            sub, name = parts[0].strip(), parts[1].strip()
                            # 跳过非城市子域名（资讯等）
                            if sub and sub not in seen and sub not in ("news", "www", "m"):
                                seen.add(sub)
                                out.append((sub, name))
            except OSError:
                self.logger.error("未找到 cities_all.txt（先运行城市目录抓取生成）")
        return out

    def start_requests(self):
        """为每个城市和页面生成链家列表页初始请求。"""
        # 多城市/全国模式：每城仅抓开放首页（区页需登录、pg2 起有验证码，故不深入）
        city_list = self._city_list()
        if city_list:
            self.logger.info("多城市模式：共 %d 城，仅抓各城首页（约 30 条/城）", len(city_list))
            for sub, name in city_list:
                base = f"https://{sub}.lianjia.com/ershoufang/"
                yield scrapy.Request(
                    base, callback=self.parse_list, errback=self._on_city_error,
                    meta={"page": 1, "base": base, "paginate": False, "city_name": name},
                )
            return

        landing = f"https://{self.city}.lianjia.com/ershoufang/"
        # 自动板块模式：先解析城市的区/板块列表，再逐个抓各区首页
        if self.auto_regions and not self.region:
            self.logger.info(
                "自动板块模式：解析 %s 的区/板块列表（入库城市名：%s）", landing, self.city_name
            )
            yield scrapy.Request(landing, callback=self.parse_regions)
            return

        path = f"ershoufang/{self.region}/" if self.region else "ershoufang/"
        base = f"https://{self.city}.lianjia.com/{path}"
        self.logger.info(
            "起始列表页：%s（入库城市名：%s，follow_detail=%s）",
            base, self.city_name, self.follow_detail,
        )
        yield scrapy.Request(
            base, callback=self.parse_list, meta={"page": 1, "base": base, "paginate": True}
        )

    def parse_regions(self, response):
        """从城市 /ershoufang/ 落地页解析区/板块链接（形如 /ershoufang/{字母}/）。"""
        seen, regions = set(), []
        for a in response.css("a"):
            m = re.match(r"^/ershoufang/([a-z]+)/$", a.attrib.get("href", ""))
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                regions.append((m.group(1), (a.css("::text").get() or "").strip()))
        if self.max_regions:
            regions = regions[: self.max_regions]
        if not regions:
            self.logger.warning("未解析到区/板块（可能被反爬拦截）：%s", response.url)
            return
        self.logger.info(
            "发现 %d 个区/板块：%s", len(regions), "，".join(n or s for s, n in regions)
        )
        for slug, name in regions:
            url = f"https://{self.city}.lianjia.com/ershoufang/{slug}/"
            yield scrapy.Request(
                url,
                callback=self.parse_list,
                meta={"page": 1, "base": url, "paginate": False, "region_name": name},
            )

    def _on_city_error(self, failure):
        """多城市模式下单个城市请求失败（DNS/超时等）只记录，不影响其他城市。"""
        req = getattr(failure, "request", None)
        self.logger.warning("城市请求失败，跳过：%s（%s）",
                            getattr(req, "url", "?"), failure.value)

    def parse_list(self, response):
        """解析链家列表页房源卡片并产出房源条目或详情请求。"""
        base = response.meta["base"]
        page = response.meta["page"]
        cards = response.css("ul.sellListContent li.clear")
        if not cards:
            city_name = response.meta.get("city_name") or self.city_name
            self.logger.warning(
                "[%s] 列表页未解析到房源（可能被反爬/登录拦截或页面结构已变）：%s",
                city_name, response.url,
            )
            return

        for li in cards:
            href = li.css("div.title a::attr(href)").get()
            house_info = " ".join(li.css(".houseInfo ::text").getall())
            region_links = li.css(".positionInfo a::text").getall()

            item = HousingItem()
            item["source"] = "lianjia"
            item["source_url"] = href            # 详情页 URL（作为去重键，不一定访问）
            item["listing_type"] = "二手房"
            item["city"] = response.meta.get("city_name") or self.city_name
            item["title"] = (li.css("div.title a::text").get() or "").strip() or house_info.strip()
            item["total_price"] = _float(" ".join(li.css(".totalPrice ::text").getall()))  # 万元
            item["unit_price"] = (
                _float(" ".join(li.css(".unitPrice ::text").getall()))
                or _float(li.css(".unitPrice::attr(data-price)").get())
            )  # 元/㎡
            # 自动板块模式下用区名作 district；否则用列表卡片里的商圈（最后一个链接）
            item["district"] = response.meta.get("region_name") or (
                region_links[-1].strip() if region_links else None
            )

            info = _parse_house_info(house_info)
            item["rooms"] = info.get("rooms")
            item["halls"] = info.get("halls")
            item["area"] = info.get("area")
            item["orientation"] = info.get("orientation")
            item["decoration"] = info.get("decoration")
            item["total_floors"] = info.get("total_floors")
            item["build_year"] = info.get("build_year")

            if self.follow_detail and href:
                # 可选：跟进详情页补充 楼层/经纬度（链家详情页有验证码，多半会被拦截）
                yield response.follow(href, callback=self.parse_detail, meta={"item": item})
            else:
                yield item

        # 翻页（仅非板块模式；受 max_pages 与 CLOSESPIDER_ITEMCOUNT 限制）
        if response.meta.get("paginate", True) and page < self.max_pages:
            nxt = page + 1
            yield scrapy.Request(
                urljoin(base, f"pg{nxt}/"),
                callback=self.parse_list,
                meta={"page": nxt, "base": base, "paginate": True,
                      "region_name": response.meta.get("region_name")},
            )

    def parse_detail(self, response):
        """可选的详情页补充解析（仅在 follow_detail=1 且未被验证码拦截时生效）。"""
        item = response.meta["item"]

        # 命中验证码/跳转页则放弃补充，直接产出列表页已得到的数据
        if "captcha" in response.url:
            self.logger.warning("详情页被验证码拦截，沿用列表页数据：%s", item["source_url"])
            yield item
            return

        base_info = {}
        for li in response.css(".introContent .base .content li"):
            label = (li.css(".label::text").get() or "").strip()
            texts = [t.strip() for t in li.css("::text").getall() if t.strip()]
            value = texts[-1] if texts else ""
            if label and value and value != label:
                base_info[label] = value

        if base_info.get("配备电梯"):
            item["has_elevator"] = "有" in base_info["配备电梯"]
        tf = re.search(r"共\s*(\d+)\s*层", base_info.get("所在楼层", ""))
        if tf:
            item["total_floors"] = int(tf.group(1))

        pos = re.search(r"resblockPosition['\"]?\s*[:=]\s*['\"]([\d.]+),([\d.]+)", response.text)
        if pos:
            item["lng"] = float(pos.group(1))
            item["lat"] = float(pos.group(2))

        yield item
