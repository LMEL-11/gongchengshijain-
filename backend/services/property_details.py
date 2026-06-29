"""Lookup extended Shandong listing fields from the raw TSV file."""
import csv  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from functools import lru_cache  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from pathlib import Path  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。


BASE_DIR = Path(__file__).resolve().parent.parent  # 计算或更新BASE_DIR中间数据，作为后续业务判断、统计或响应组装的输入。
HOUSE_INFO_FILE = BASE_DIR / "data" / "raw" / "house_info.tsv"  # 计算或更新HOUSE_INFO_FILE中间数据，作为后续业务判断、统计或响应组装的输入。

DETAIL_FIELDS = {  # 初始化DETAIL_FIELDS中间数据字典，用于承载接口返回或中间聚合结果。
    "shijian": "listing_date",  # 把shijian字段写入响应数据，供前端页面、图表或后续接口读取。
    "quanshu": "ownership_type",  # 把quanshu字段写入响应数据，供前端页面、图表或后续接口读取。
    "chanquan": "property_right",  # 把chanquan字段写入响应数据，供前端页面、图表或后续接口读取。
    "diya": "mortgage",  # 把diya字段写入响应数据，供前端页面、图表或后续接口读取。
    "maidian": "selling_point",  # 把maidian字段写入响应数据，供前端页面、图表或后续接口读取。
    "jieshao": "community_intro",  # 把jieshao字段写入响应数据，供前端页面、图表或后续接口读取。
    "huxingjieshao": "layout_intro",  # 把huxingjieshao字段写入响应数据，供前端页面、图表或后续接口读取。
    "jiaotong": "transport_intro",  # 把jiaotong字段写入响应数据，供前端页面、图表或后续接口读取。
}  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def _clean_text(value):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    if value is None:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    text = str(value).replace("\u00a0", " ").strip()  # 计算或更新text中间数据，作为后续业务判断、统计或响应组装的输入。
    if not text or text in {"None", "暂无数据", "未知"}:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return None  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return text  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@lru_cache(maxsize=1)  # 把下方函数注册为路由、权限校验或框架回调入口。
def _details_by_url():  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """按来源链接查找房源交易扩展记录并返回字典。"""
    if not HOUSE_INFO_FILE.exists():  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return {}  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    details = {}  # 初始化details中间数据字典，用于承载接口返回或中间聚合结果。
    with HOUSE_INFO_FILE.open("r", encoding="utf-8-sig", newline="") as fh:  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
        reader = csv.DictReader(fh, delimiter="\t")  # 计算或更新reader中间数据，作为后续业务判断、统计或响应组装的输入。
        for row in reader:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            url = _clean_text(row.get("link"))  # 计算或更新url中间数据，作为后续业务判断、统计或响应组装的输入。
            if not url:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            item = {  # 初始化单条数据字典，用于承载接口返回或中间聚合结果。
                target: _clean_text(row.get(source))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                for source, target in DETAIL_FIELDS.items()  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            if any(item.values()):  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                details[url] = item  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return details  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def get_property_details(source_url):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Return extended detail fields for a listing source URL."""
    if not source_url:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return {}  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return _details_by_url().get(source_url, {})  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def clean_detail_dict(data):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Remove empty values from a transaction/detail mapping."""
    return {k: v for k, v in (data or {}).items() if _clean_text(v)}  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def get_property_transaction_details(prop):  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Return admin-maintained transaction fields, falling back to raw TSV details."""
    raw = get_property_details(prop.source_url)  # 从请求或外部输入提取raw中间数据，用于后续校验、查询或写入。
    manual = prop.transaction.to_dict() if getattr(prop, "transaction", None) else {}  # 计算或更新manual中间数据，作为后续业务判断、统计或响应组装的输入。
    return {**clean_detail_dict(raw), **clean_detail_dict(manual)}  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
