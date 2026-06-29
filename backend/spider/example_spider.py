"""示例爬虫：演示「请求 → 解析 → 入库」骨架（默认解析内置示例 HTML，不联网）。

真实使用时：把 ``SAMPLE_HTML`` 换成 ``self.fetch(list_page_url)`` 的返回值，并把
``parse`` 里的选择器换成目标页面的真实结构。务必遵守目标站点的 robots.txt 与 ToS。
"""
import re  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from typing import Iterable  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from .base import BaseSpider  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

# 一段构造的示例列表页 HTML（仅用于演示解析逻辑）。
SAMPLE_HTML = """  # 计算或更新SAMPLE_HTML中间数据，作为后续业务判断、统计或响应组装的输入。
<ul class="sellListContent">  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
  <li class="clear">  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    <div class="title"><a href="https://example.com/h/1001">海淀学区两居 满五唯一</a></div>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    <div class="houseInfo">海淀区 | 2室1厅 | 89.5平米 | 南北 | 精装 | 有电梯</div>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    <div class="totalPrice"><span>880</span>万</div>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    <div class="unitPrice"><span>98324</span>元/平</div>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
  </li>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
  <li class="clear">  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    <div class="title"><a href="https://example.com/h/1002">朝阳精装三居 近地铁</a></div>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    <div class="houseInfo">朝阳区 | 3室2厅 | 132平米 | 南 | 简装 | 有电梯</div>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    <div class="totalPrice"><span>1020</span>万</div>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    <div class="unitPrice"><span>77272</span>元/平</div>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
  </li>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
</ul>  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
"""

_ITEM_RE = re.compile(r'<li class="clear">(.*?)</li>', re.S)
_TITLE_RE = re.compile(r'<div class="title"><a href="(?P<url>[^"]+)">(?P<title>[^<]+)</a>')
_INFO_RE = re.compile(r'<div class="houseInfo">(?P<info>[^<]+)</div>')
_TOTAL_RE = re.compile(r'<div class="totalPrice"><span>(?P<total>[\d.]+)</span>')
_UNIT_RE = re.compile(r'<div class="unitPrice"><span>(?P<unit>[\d.]+)</span>')


class ExampleSpider(BaseSpider):
    """演示如何继承基础爬虫并解析示例房源数据。"""
    source_name = "example"

    def parse(self, html: str) -> Iterable[dict]:
        """解析页面文本并产出结构化结果。"""
        for block in _ITEM_RE.findall(html):
            title_m = _TITLE_RE.search(block)
            info_m = _INFO_RE.search(block)
            total_m = _TOTAL_RE.search(block)
            unit_m = _UNIT_RE.search(block)
            if not (title_m and info_m):
                continue
            yield {**self._parse_info(info_m.group("info")),
                   "title": title_m.group("title").strip(),
                   "source_url": title_m.group("url"),
                   "total_price": float(total_m.group("total")) if total_m else None,
                   "unit_price": float(unit_m.group("unit")) if unit_m else None}

    @staticmethod
    def _parse_info(info: str) -> dict:
        """Parse "海淀区 | 2室1厅 | 89.5平米 | 南北 | 精装 | 有电梯"."""
        parts = [p.strip() for p in info.split("|")]
        rec: dict = {"district": parts[0] if parts else None}
        for p in parts[1:]:
            if "室" in p and "厅" in p:
                m = re.match(r"(\d+)室(\d+)厅", p)
                if m:
                    rec["rooms"], rec["halls"] = int(m.group(1)), int(m.group(2))
            elif "平米" in p or "平" in p:
                m = re.search(r"([\d.]+)", p)
                if m:
                    rec["area"] = float(m.group(1))
            elif p in ("南", "北", "南北", "东", "西", "东南", "西南", "东北", "西北"):
                rec["orientation"] = p
            elif "装" in p:
                rec["decoration"] = p
            elif "电梯" in p:
                rec["has_elevator"] = "有" in p
        return rec


def run_demo(app, city_name: str = "北京") -> int:
    """Parse the embedded sample HTML and persist it (for demonstration)."""
    spider = ExampleSpider()
    with app.app_context():
        records = list(spider.parse(SAMPLE_HTML))
        return spider.persist(records, city_name=city_name, province="北京市")


if __name__ == "__main__":  # pragma: no cover
    from app import app

    print(f"已演示入库 {run_demo(app)} 条示例房源。")
