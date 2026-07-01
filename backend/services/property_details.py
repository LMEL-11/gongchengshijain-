"""Lookup extended Shandong listing fields from the raw TSV file."""  # 保留字符串内容，作为说明文本或页面展示文案。
import csv  # 导入 csv 模块，为当前文件提供所需功能。
from functools import lru_cache  # 从 functools 导入 lru_cache，供本文件后续逻辑调用。
from pathlib import Path  # 从 pathlib 导入 Path，供本文件后续逻辑调用。


BASE_DIR = Path(__file__).resolve().parent.parent  # 设置 BASE_DIR 的值，供后续业务判断、查询或响应组装使用。
HOUSE_INFO_FILE = BASE_DIR / "data" / "raw" / "house_info.tsv"  # 设置 HOUSE_INFO_FILE 的值，供后续业务判断、查询或响应组装使用。

DETAIL_FIELDS = {  # 设置 DETAIL_FIELDS 的值，供后续业务判断、查询或响应组装使用。
    "shijian": "listing_date",  # 保留字符串内容，作为说明文本或页面展示文案。
    "quanshu": "ownership_type",  # 保留字符串内容，作为说明文本或页面展示文案。
    "chanquan": "property_right",  # 保留字符串内容，作为说明文本或页面展示文案。
    "diya": "mortgage",  # 保留字符串内容，作为说明文本或页面展示文案。
    "maidian": "selling_point",  # 保留字符串内容，作为说明文本或页面展示文案。
    "jieshao": "community_intro",  # 保留字符串内容，作为说明文本或页面展示文案。
    "huxingjieshao": "layout_intro",  # 保留字符串内容，作为说明文本或页面展示文案。
    "jiaotong": "transport_intro",  # 保留字符串内容，作为说明文本或页面展示文案。
}  # 结束当前多行数据结构或函数调用。


def _clean_text(value):  # 定义 _clean_text 函数，集中处理这一段业务逻辑。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if value is None:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return None  # 返回处理后的结果给调用方继续使用。
    text = str(value).replace("\u00a0", " ").strip()  # 设置 text 的值，供后续业务判断、查询或响应组装使用。
    if not text or text in {"None", "暂无数据", "未知"}:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return None  # 返回处理后的结果给调用方继续使用。
    return text  # 返回处理后的结果给调用方继续使用。


@lru_cache(maxsize=1)  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def _details_by_url():  # 定义 _details_by_url 函数，集中处理这一段业务逻辑。
    """按来源链接查找房源交易扩展记录并返回字典。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if not HOUSE_INFO_FILE.exists():  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return {}  # 返回处理后的结果给调用方继续使用。

    details = {}  # 设置 details 的值，供后续业务判断、查询或响应组装使用。
    with HOUSE_INFO_FILE.open("r", encoding="utf-8-sig", newline="") as fh:  # 进入上下文管理流程，自动处理资源打开和释放。
        reader = csv.DictReader(fh, delimiter="\t")  # 设置 reader 的值，供后续业务判断、查询或响应组装使用。
        for row in reader:  # 遍历当前数据集合，逐项完成处理。
            url = _clean_text(row.get("link"))  # 设置 url 的值，供后续业务判断、查询或响应组装使用。
            if not url:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                continue  # 跳过当前循环项，继续处理下一项。
            item = {  # 设置 item 的值，供后续业务判断、查询或响应组装使用。
                target: _clean_text(row.get(source))  # 执行当前代码行对应的业务处理步骤。
                for source, target in DETAIL_FIELDS.items()  # 遍历当前数据集合，逐项完成处理。
            }  # 结束当前多行数据结构或函数调用。
            if any(item.values()):  # 判断当前条件是否成立，决定是否进入对应处理分支。
                details[url] = item  # 设置 details[url 的值，供后续业务判断、查询或响应组装使用。
    return details  # 返回处理后的结果给调用方继续使用。


def get_property_details(source_url):  # 定义 get_property_details 函数，集中处理这一段业务逻辑。
    """Return extended detail fields for a listing source URL."""  # 保留字符串内容，作为说明文本或页面展示文案。
    if not source_url:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return {}  # 返回处理后的结果给调用方继续使用。
    return _details_by_url().get(source_url, {})  # 返回处理后的结果给调用方继续使用。


def clean_detail_dict(data):  # 定义 clean_detail_dict 函数，集中处理这一段业务逻辑。
    """Remove empty values from a transaction/detail mapping."""  # 保留字符串内容，作为说明文本或页面展示文案。
    return {k: v for k, v in (data or {}).items() if _clean_text(v)}  # 返回处理后的结果给调用方继续使用。


def get_property_transaction_details(prop):  # 定义 get_property_transaction_details 函数，集中处理这一段业务逻辑。
    """Return admin-maintained transaction fields, falling back to raw TSV details."""  # 保留字符串内容，作为说明文本或页面展示文案。
    raw = get_property_details(prop.source_url)  # 设置 raw 的值，供后续业务判断、查询或响应组装使用。
    manual = prop.transaction.to_dict() if getattr(prop, "transaction", None) else {}  # 设置 manual 的值，供后续业务判断、查询或响应组装使用。
    return {**clean_detail_dict(raw), **clean_detail_dict(manual)}  # 返回处理后的结果给调用方继续使用。
