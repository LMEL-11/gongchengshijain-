"""Lookup extended Shandong listing fields from the raw TSV file."""
import csv  # 导入本行所需的模块或对象。
from functools import lru_cache  # 导入本行所需的模块或对象。
from pathlib import Path  # 导入本行所需的模块或对象。


BASE_DIR = Path(__file__).resolve().parent.parent  # 赋值或更新当前变量/字段。
HOUSE_INFO_FILE = BASE_DIR / "data" / "raw" / "house_info.tsv"  # 赋值或更新当前变量/字段。

DETAIL_FIELDS = {  # 赋值或更新当前变量/字段。
    "shijian": "listing_date",  # 设置当前数据项或参数。
    "quanshu": "ownership_type",  # 设置当前数据项或参数。
    "chanquan": "property_right",  # 设置当前数据项或参数。
    "diya": "mortgage",  # 设置当前数据项或参数。
    "maidian": "selling_point",  # 设置当前数据项或参数。
    "jieshao": "community_intro",  # 设置当前数据项或参数。
    "huxingjieshao": "layout_intro",  # 设置当前数据项或参数。
    "jiaotong": "transport_intro",  # 设置当前数据项或参数。
}  # 结束当前数据结构或调用块。


def _clean_text(value):  # 声明函数或方法入口。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    if value is None:  # 根据条件判断是否进入该分支。
        return None  # 返回当前逻辑的处理结果。
    text = str(value).replace("\u00a0", " ").strip()  # 赋值或更新当前变量/字段。
    if not text or text in {"None", "暂无数据", "未知"}:  # 根据条件判断是否进入该分支。
        return None  # 返回当前逻辑的处理结果。
    return text  # 返回当前逻辑的处理结果。


@lru_cache(maxsize=1)  # 应用装饰器配置路由、权限或命令。
def _details_by_url():  # 声明函数或方法入口。
    """按来源链接查找房源交易扩展记录并返回字典。"""
    if not HOUSE_INFO_FILE.exists():  # 根据条件判断是否进入该分支。
        return {}  # 返回当前逻辑的处理结果。

    details = {}  # 赋值或更新当前变量/字段。
    with HOUSE_INFO_FILE.open("r", encoding="utf-8-sig", newline="") as fh:  # 进入上下文管理器并自动处理资源。
        reader = csv.DictReader(fh, delimiter="\t")  # 赋值或更新当前变量/字段。
        for row in reader:  # 遍历集合中的每一项并执行处理。
            url = _clean_text(row.get("link"))  # 赋值或更新当前变量/字段。
            if not url:  # 根据条件判断是否进入该分支。
                continue  # 跳过本轮循环剩余逻辑。
            item = {  # 赋值或更新当前变量/字段。
                target: _clean_text(row.get(source))  # 设置当前数据项或参数。
                for source, target in DETAIL_FIELDS.items()  # 遍历集合中的每一项并执行处理。
            }  # 结束当前数据结构或调用块。
            if any(item.values()):  # 根据条件判断是否进入该分支。
                details[url] = item  # 赋值或更新当前变量/字段。
    return details  # 返回当前逻辑的处理结果。


def get_property_details(source_url):  # 声明函数或方法入口。
    """Return extended detail fields for a listing source URL."""
    if not source_url:  # 根据条件判断是否进入该分支。
        return {}  # 返回当前逻辑的处理结果。
    return _details_by_url().get(source_url, {})  # 返回当前逻辑的处理结果。


def clean_detail_dict(data):  # 声明函数或方法入口。
    """Remove empty values from a transaction/detail mapping."""
    return {k: v for k, v in (data or {}).items() if _clean_text(v)}  # 返回当前逻辑的处理结果。


def get_property_transaction_details(prop):  # 声明函数或方法入口。
    """Return admin-maintained transaction fields, falling back to raw TSV details."""
    raw = get_property_details(prop.source_url)  # 赋值或更新当前变量/字段。
    manual = prop.transaction.to_dict() if getattr(prop, "transaction", None) else {}  # 赋值或更新当前变量/字段。
    return {**clean_detail_dict(raw), **clean_detail_dict(manual)}  # 返回当前逻辑的处理结果。
