"""示例爬虫：演示「请求 → 解析 → 入库」骨架（默认解析内置示例 HTML，不联网）。

真实使用时：把 ``SAMPLE_HTML`` 换成 ``self.fetch(list_page_url)`` 的返回值，并把
``parse`` 里的选择器换成目标页面的真实结构。务必遵守目标站点的 robots.txt 与 ToS。
"""
import re  # 导入 re 模块，为当前文件提供所需功能。
from typing import Iterable  # 从 typing 导入 Iterable，供本文件后续逻辑调用。

from .base import BaseSpider  # 从 .base 导入 BaseSpider，供本文件后续逻辑调用。

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

_ITEM_RE = re.compile(r'<li class="clear">(.*?)</li>', re.S)  # 设置 _ITEM_RE 的值，供后续业务判断、查询或响应组装使用。
_TITLE_RE = re.compile(r'<div class="title"><a href="(?P<url>[^"]+)">(?P<title>[^<]+)</a>')  # 设置 _TITLE_RE 的值，供后续业务判断、查询或响应组装使用。
_INFO_RE = re.compile(r'<div class="houseInfo">(?P<info>[^<]+)</div>')  # 设置 _INFO_RE 的值，供后续业务判断、查询或响应组装使用。
_TOTAL_RE = re.compile(r'<div class="totalPrice"><span>(?P<total>[\d.]+)</span>')  # 设置 _TOTAL_RE 的值，供后续业务判断、查询或响应组装使用。
_UNIT_RE = re.compile(r'<div class="unitPrice"><span>(?P<unit>[\d.]+)</span>')  # 设置 _UNIT_RE 的值，供后续业务判断、查询或响应组装使用。


class ExampleSpider(BaseSpider):  # 定义 ExampleSpider(BaseSpider 类，封装对应的数据结构或业务行为。
    """演示如何继承基础爬虫并解析示例房源数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    source_name = "example"  # 设置 source_name 的值，供后续业务判断、查询或响应组装使用。

    def parse(self, html: str) -> Iterable[dict]:  # 定义 parse 函数，集中处理这一段业务逻辑。
        """解析页面文本并产出结构化结果。"""  # 保留字符串内容，作为说明文本或页面展示文案。
        for block in _ITEM_RE.findall(html):  # 遍历当前数据集合，逐项完成处理。
            title_m = _TITLE_RE.search(block)  # 设置 title_m 的值，供后续业务判断、查询或响应组装使用。
            info_m = _INFO_RE.search(block)  # 设置 info_m 的值，供后续业务判断、查询或响应组装使用。
            total_m = _TOTAL_RE.search(block)  # 设置 total_m 的值，供后续业务判断、查询或响应组装使用。
            unit_m = _UNIT_RE.search(block)  # 设置 unit_m 的值，供后续业务判断、查询或响应组装使用。
            if not (title_m and info_m):  # 判断当前条件是否成立，决定是否进入对应处理分支。
                continue  # 跳过当前循环项，继续处理下一项。
            yield {**self._parse_info(info_m.group("info")),  # 产出当前请求或数据项，交给框架后续流程处理。
                   "title": title_m.group("title").strip(),  # 保留字符串内容，作为说明文本或页面展示文案。
                   "source_url": title_m.group("url"),  # 保留字符串内容，作为说明文本或页面展示文案。
                   "total_price": float(total_m.group("total")) if total_m else None,  # 保留字符串内容，作为说明文本或页面展示文案。
                   "unit_price": float(unit_m.group("unit")) if unit_m else None}  # 保留字符串内容，作为说明文本或页面展示文案。

    @staticmethod  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
    def _parse_info(info: str) -> dict:  # 定义 _parse_info 函数，集中处理这一段业务逻辑。
        """Parse "海淀区 | 2室1厅 | 89.5平米 | 南北 | 精装 | 有电梯"."""  # 保留字符串内容，作为说明文本或页面展示文案。
        parts = [p.strip() for p in info.split("|")]  # 设置 parts 的值，供后续业务判断、查询或响应组装使用。
        rec: dict = {"district": parts[0] if parts else None}  # 设置 rec: dict 的值，供后续业务判断、查询或响应组装使用。
        for p in parts[1:]:  # 遍历当前数据集合，逐项完成处理。
            if "室" in p and "厅" in p:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                m = re.match(r"(\d+)室(\d+)厅", p)  # 设置 m 的值，供后续业务判断、查询或响应组装使用。
                if m:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    rec["rooms"], rec["halls"] = int(m.group(1)), int(m.group(2))  # 设置 rec["rooms"], rec["halls" 的值，供后续业务判断、查询或响应组装使用。
            elif "平米" in p or "平" in p:  # 在前一个条件不成立时，继续判断这个补充分支。
                m = re.search(r"([\d.]+)", p)  # 设置 m 的值，供后续业务判断、查询或响应组装使用。
                if m:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    rec["area"] = float(m.group(1))  # 设置 rec["area" 的值，供后续业务判断、查询或响应组装使用。
            elif p in ("南", "北", "南北", "东", "西", "东南", "西南", "东北", "西北"):  # 在前一个条件不成立时，继续判断这个补充分支。
                rec["orientation"] = p  # 设置 rec["orientation" 的值，供后续业务判断、查询或响应组装使用。
            elif "装" in p:  # 在前一个条件不成立时，继续判断这个补充分支。
                rec["decoration"] = p  # 设置 rec["decoration" 的值，供后续业务判断、查询或响应组装使用。
            elif "电梯" in p:  # 在前一个条件不成立时，继续判断这个补充分支。
                rec["has_elevator"] = "有" in p  # 设置 rec["has_elevator" 的值，供后续业务判断、查询或响应组装使用。
        return rec  # 返回处理后的结果给调用方继续使用。


def run_demo(app, city_name: str = "北京") -> int:  # 定义 run_demo 函数，集中处理这一段业务逻辑。
    """Parse the embedded sample HTML and persist it (for demonstration)."""  # 保留字符串内容，作为说明文本或页面展示文案。
    spider = ExampleSpider()  # 设置 spider 的值，供后续业务判断、查询或响应组装使用。
    with app.app_context():  # 进入上下文管理流程，自动处理资源打开和释放。
        records = list(spider.parse(SAMPLE_HTML))  # 设置 records 的值，供后续业务判断、查询或响应组装使用。
        return spider.persist(records, city_name=city_name, province="北京市")  # 返回处理后的结果给调用方继续使用。


if __name__ == "__main__":  # pragma: no cover
    from app import app  # 从 app 导入 app，供本文件后续逻辑调用。

    print(f"已演示入库 {run_demo(app)} 条示例房源。")  # 输出当前处理结果或运行状态，方便调试和观察流程。
