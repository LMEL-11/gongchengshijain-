"""Lookup extended Shandong listing fields from the raw TSV file."""
import csv  # 逐行注释：导入本行所需的模块或对象。
from functools import lru_cache  # 逐行注释：导入本行所需的模块或对象。
from pathlib import Path  # 逐行注释：导入本行所需的模块或对象。


BASE_DIR = Path(__file__).resolve().parent.parent  # 逐行注释：赋值或更新当前变量/字段。
HOUSE_INFO_FILE = BASE_DIR / "data" / "raw" / "house_info.tsv"  # 逐行注释：赋值或更新当前变量/字段。

DETAIL_FIELDS = {  # 逐行注释：赋值或更新当前变量/字段。
    "shijian": "listing_date",  # 逐行注释：设置当前数据项或参数。
    "quanshu": "ownership_type",  # 逐行注释：设置当前数据项或参数。
    "chanquan": "property_right",  # 逐行注释：设置当前数据项或参数。
    "diya": "mortgage",  # 逐行注释：设置当前数据项或参数。
    "maidian": "selling_point",  # 逐行注释：设置当前数据项或参数。
    "jieshao": "community_intro",  # 逐行注释：设置当前数据项或参数。
    "huxingjieshao": "layout_intro",  # 逐行注释：设置当前数据项或参数。
    "jiaotong": "transport_intro",  # 逐行注释：设置当前数据项或参数。
}  # 逐行注释：结束当前数据结构或调用块。


def _clean_text(value):  # 逐行注释：声明函数或方法入口。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    if value is None:  # 逐行注释：根据条件判断是否进入该分支。
        return None  # 逐行注释：返回当前逻辑的处理结果。
    text = str(value).replace("\u00a0", " ").strip()  # 逐行注释：赋值或更新当前变量/字段。
    if not text or text in {"None", "暂无数据", "未知"}:  # 逐行注释：根据条件判断是否进入该分支。
        return None  # 逐行注释：返回当前逻辑的处理结果。
    return text  # 逐行注释：返回当前逻辑的处理结果。


@lru_cache(maxsize=1)  # 逐行注释：应用装饰器配置路由、权限或命令。
def _details_by_url():  # 逐行注释：声明函数或方法入口。
    """按来源链接查找房源交易扩展记录并返回字典。"""
    if not HOUSE_INFO_FILE.exists():  # 逐行注释：根据条件判断是否进入该分支。
        return {}  # 逐行注释：返回当前逻辑的处理结果。

    details = {}  # 逐行注释：赋值或更新当前变量/字段。
    with HOUSE_INFO_FILE.open("r", encoding="utf-8-sig", newline="") as fh:  # 逐行注释：进入上下文管理器并自动处理资源。
        reader = csv.DictReader(fh, delimiter="\t")  # 逐行注释：赋值或更新当前变量/字段。
        for row in reader:  # 逐行注释：遍历集合中的每一项并执行处理。
            url = _clean_text(row.get("link"))  # 逐行注释：赋值或更新当前变量/字段。
            if not url:  # 逐行注释：根据条件判断是否进入该分支。
                continue  # 逐行注释：跳过本轮循环剩余逻辑。
            item = {  # 逐行注释：赋值或更新当前变量/字段。
                target: _clean_text(row.get(source))  # 逐行注释：设置当前数据项或参数。
                for source, target in DETAIL_FIELDS.items()  # 逐行注释：遍历集合中的每一项并执行处理。
            }  # 逐行注释：结束当前数据结构或调用块。
            if any(item.values()):  # 逐行注释：根据条件判断是否进入该分支。
                details[url] = item  # 逐行注释：赋值或更新当前变量/字段。
    return details  # 逐行注释：返回当前逻辑的处理结果。


def get_property_details(source_url):  # 逐行注释：声明函数或方法入口。
    """Return extended detail fields for a listing source URL."""
    if not source_url:  # 逐行注释：根据条件判断是否进入该分支。
        return {}  # 逐行注释：返回当前逻辑的处理结果。
    return _details_by_url().get(source_url, {})  # 逐行注释：返回当前逻辑的处理结果。


def clean_detail_dict(data):  # 逐行注释：声明函数或方法入口。
    """Remove empty values from a transaction/detail mapping."""
    return {k: v for k, v in (data or {}).items() if _clean_text(v)}  # 逐行注释：返回当前逻辑的处理结果。


def get_property_transaction_details(prop):  # 逐行注释：声明函数或方法入口。
    """Return admin-maintained transaction fields, falling back to raw TSV details."""
    raw = get_property_details(prop.source_url)  # 逐行注释：赋值或更新当前变量/字段。
    manual = prop.transaction.to_dict() if getattr(prop, "transaction", None) else {}  # 逐行注释：赋值或更新当前变量/字段。
    return {**clean_detail_dict(raw), **clean_detail_dict(manual)}  # 逐行注释：返回当前逻辑的处理结果。
