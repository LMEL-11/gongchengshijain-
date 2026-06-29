"""示例爬虫：演示「请求 → 解析 → 入库」骨架（默认解析内置示例 HTML，不联网）。

真实使用时：把 ``SAMPLE_HTML`` 换成 ``self.fetch(list_page_url)`` 的返回值，并把
``parse`` 里的选择器换成目标页面的真实结构。务必遵守目标站点的 robots.txt 与 ToS。
"""
import re  # 逐行注释：导入本行所需的模块或对象。
from typing import Iterable  # 逐行注释：导入本行所需的模块或对象。

from .base import BaseSpider  # 逐行注释：导入本行所需的模块或对象。

# 一段构造的示例列表页 HTML（仅用于演示解析逻辑）。
SAMPLE_HTML = """
<ul class="sellListContent">
  <li class="clear">
    <div class="title"><a href="https://example.com/h/1001">海淀学区两居 满五唯一</a></div>
    <div class="houseInfo">海淀区 | 2室1厅 | 89.5平米 | 南北 | 精装 | 有电梯</div>
    <div class="totalPrice"><span>880</span>万</div>
    <div class="unitPrice"><span>98324</span>元/平</div>
  </li>
  <li class="clear">
    <div class="title"><a href="https://example.com/h/1002">朝阳精装三居 近地铁</a></div>
    <div class="houseInfo">朝阳区 | 3室2厅 | 132平米 | 南 | 简装 | 有电梯</div>
    <div class="totalPrice"><span>1020</span>万</div>
    <div class="unitPrice"><span>77272</span>元/平</div>
  </li>
</ul>
"""

_ITEM_RE = re.compile(r'<li class="clear">(.*?)</li>', re.S)  # 逐行注释：赋值或更新当前变量/字段。
_TITLE_RE = re.compile(r'<div class="title"><a href="(?P<url>[^"]+)">(?P<title>[^<]+)</a>')  # 逐行注释：赋值或更新当前变量/字段。
_INFO_RE = re.compile(r'<div class="houseInfo">(?P<info>[^<]+)</div>')  # 逐行注释：赋值或更新当前变量/字段。
_TOTAL_RE = re.compile(r'<div class="totalPrice"><span>(?P<total>[\d.]+)</span>')  # 逐行注释：赋值或更新当前变量/字段。
_UNIT_RE = re.compile(r'<div class="unitPrice"><span>(?P<unit>[\d.]+)</span>')  # 逐行注释：赋值或更新当前变量/字段。


class ExampleSpider(BaseSpider):  # 逐行注释：声明类并定义相关数据或行为。
    """演示如何继承基础爬虫并解析示例房源数据。"""
    source_name = "example"  # 逐行注释：赋值或更新当前变量/字段。

    def parse(self, html: str) -> Iterable[dict]:  # 逐行注释：声明函数或方法入口。
        """解析页面文本并产出结构化结果。"""
        for block in _ITEM_RE.findall(html):  # 逐行注释：遍历集合中的每一项并执行处理。
            title_m = _TITLE_RE.search(block)  # 逐行注释：赋值或更新当前变量/字段。
            info_m = _INFO_RE.search(block)  # 逐行注释：赋值或更新当前变量/字段。
            total_m = _TOTAL_RE.search(block)  # 逐行注释：赋值或更新当前变量/字段。
            unit_m = _UNIT_RE.search(block)  # 逐行注释：赋值或更新当前变量/字段。
            if not (title_m and info_m):  # 逐行注释：根据条件判断是否进入该分支。
                continue  # 逐行注释：跳过本轮循环剩余逻辑。
            yield {**self._parse_info(info_m.group("info")),  # 逐行注释：设置当前数据项或参数。
                   "title": title_m.group("title").strip(),  # 逐行注释：设置当前数据项或参数。
                   "source_url": title_m.group("url"),  # 逐行注释：设置当前数据项或参数。
                   "total_price": float(total_m.group("total")) if total_m else None,  # 逐行注释：设置当前数据项或参数。
                   "unit_price": float(unit_m.group("unit")) if unit_m else None}  # 逐行注释：设置当前数据项或参数。

    @staticmethod  # 逐行注释：应用装饰器配置路由、权限或命令。
    def _parse_info(info: str) -> dict:  # 逐行注释：声明函数或方法入口。
        """Parse "海淀区 | 2室1厅 | 89.5平米 | 南北 | 精装 | 有电梯"."""
        parts = [p.strip() for p in info.split("|")]  # 逐行注释：赋值或更新当前变量/字段。
        rec: dict = {"district": parts[0] if parts else None}  # 逐行注释：赋值或更新当前变量/字段。
        for p in parts[1:]:  # 逐行注释：遍历集合中的每一项并执行处理。
            if "室" in p and "厅" in p:  # 逐行注释：根据条件判断是否进入该分支。
                m = re.match(r"(\d+)室(\d+)厅", p)  # 逐行注释：赋值或更新当前变量/字段。
                if m:  # 逐行注释：根据条件判断是否进入该分支。
                    rec["rooms"], rec["halls"] = int(m.group(1)), int(m.group(2))  # 逐行注释：赋值或更新当前变量/字段。
            elif "平米" in p or "平" in p:  # 逐行注释：根据条件判断是否进入该分支。
                m = re.search(r"([\d.]+)", p)  # 逐行注释：赋值或更新当前变量/字段。
                if m:  # 逐行注释：根据条件判断是否进入该分支。
                    rec["area"] = float(m.group(1))  # 逐行注释：赋值或更新当前变量/字段。
            elif p in ("南", "北", "南北", "东", "西", "东南", "西南", "东北", "西北"):  # 逐行注释：根据条件判断是否进入该分支。
                rec["orientation"] = p  # 逐行注释：赋值或更新当前变量/字段。
            elif "装" in p:  # 逐行注释：根据条件判断是否进入该分支。
                rec["decoration"] = p  # 逐行注释：赋值或更新当前变量/字段。
            elif "电梯" in p:  # 逐行注释：根据条件判断是否进入该分支。
                rec["has_elevator"] = "有" in p  # 逐行注释：赋值或更新当前变量/字段。
        return rec  # 逐行注释：返回当前逻辑的处理结果。


def run_demo(app, city_name: str = "北京") -> int:  # 逐行注释：声明函数或方法入口。
    """Parse the embedded sample HTML and persist it (for demonstration)."""
    spider = ExampleSpider()  # 逐行注释：赋值或更新当前变量/字段。
    with app.app_context():  # 逐行注释：进入上下文管理器并自动处理资源。
        records = list(spider.parse(SAMPLE_HTML))  # 逐行注释：赋值或更新当前变量/字段。
        return spider.persist(records, city_name=city_name, province="北京市")  # 逐行注释：返回当前逻辑的处理结果。


if __name__ == "__main__":  # pragma: no cover
    from app import app  # 逐行注释：导入本行所需的模块或对象。

    print(f"已演示入库 {run_demo(app)} 条示例房源。")  # 逐行注释：执行本行代码逻辑。
