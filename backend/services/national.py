"""全国二手房数据服务（基于真实 province_data.csv）。

数据列：省份, 城市, 二手房, 新房, 租房（均为挂牌量）。
为与地图（DataV GeoJSON）的区域名匹配，名称统一做规范化处理。
"""
import csv  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from functools import lru_cache  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from pathlib import Path  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from sqlalchemy import func  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

from extensions import db  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。
from models import City, District, Property  # 引入当前模块需要的依赖，支撑数据库访问、接口处理或数据清洗流程。

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "province_data.csv"  # 计算或更新DATA_FILE中间数据，作为后续业务判断、统计或响应组装的输入。
HOUSE_INFO_FILE = Path(__file__).resolve().parent.parent / "data" / "raw" / "house_info.tsv"  # 计算或更新HOUSE_INFO_FILE中间数据，作为后续业务判断、统计或响应组装的输入。

# 长名 -> 短名（自治区/特别行政区），其余按后缀裁剪。
_SPECIAL = {  # 初始化_SPECIAL中间数据字典，用于承载接口返回或中间聚合结果。
    "内蒙古自治区": "内蒙古",  # 把内蒙古自治区字段写入响应数据，供前端页面、图表或后续接口读取。
    "广西壮族自治区": "广西",  # 把广西壮族自治区字段写入响应数据，供前端页面、图表或后续接口读取。
    "宁夏回族自治区": "宁夏",  # 把宁夏回族自治区字段写入响应数据，供前端页面、图表或后续接口读取。
    "新疆维吾尔自治区": "新疆",  # 把新疆维吾尔自治区字段写入响应数据，供前端页面、图表或后续接口读取。
    "西藏自治区": "西藏",  # 把西藏自治区字段写入响应数据，供前端页面、图表或后续接口读取。
    "香港特别行政区": "香港",  # 把香港特别行政区字段写入响应数据，供前端页面、图表或后续接口读取。
    "澳门特别行政区": "澳门",  # 把澳门特别行政区字段写入响应数据，供前端页面、图表或后续接口读取。
}  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def normalize_name(name: str) -> str:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """北京市->北京、山东省->山东、崂山区->崂山、内蒙古自治区->内蒙古。幂等。"""
    if not name:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return ""  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    name = name.strip()  # 计算或更新name中间数据，作为后续业务判断、统计或响应组装的输入。
    if name in _SPECIAL:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return _SPECIAL[name]  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    for suffix in ("特别行政区", "自治区", "省", "市", "区", "县"):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        if name.endswith(suffix) and len(name) - len(suffix) >= 2:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            return name[: -len(suffix)]  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return name  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _num(value: str) -> int:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """将输入值安全转换为浮点数，失败时返回零。"""
    value = (value or "").strip().replace(",", "")  # 计算或更新value中间数据，作为后续业务判断、统计或响应组装的输入。
    return int(value) if value.isdigit() else 0  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


@lru_cache(maxsize=1)  # 把下方函数注册为路由、权限校验或框架回调入口。
def _rows() -> list[dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """从全国静态 CSV 数据中读取并缓存原始行。"""
    rows = []  # 初始化查询结果集合列表，用于收集清洗后的多条业务数据。
    with open(DATA_FILE, encoding="utf-8-sig") as f:  # utf-8-sig 去除 BOM
        for r in csv.DictReader(f):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
            rows.append(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
                    "province": normalize_name(r.get("省份", "")),  # 把province字段写入响应数据，供前端页面、图表或后续接口读取。
                    "city": normalize_name(r.get("城市", "")),  # 把city字段写入响应数据，供前端页面、图表或后续接口读取。
                    "ershou": _num(r.get("二手房")),  # 把ershou字段写入响应数据，供前端页面、图表或后续接口读取。
                    "xinfang": _num(r.get("新房")),  # 把xinfang字段写入响应数据，供前端页面、图表或后续接口读取。
                    "zufang": _num(r.get("租房")),  # 把zufang字段写入响应数据，供前端页面、图表或后续接口读取。
                }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
            )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return rows  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def summary() -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """返回全国或真实数据模式的总览统计信息。"""
    rows = _rows()  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
    top_cities = sorted(  # 计算或更新top_cities中间数据，作为后续业务判断、统计或响应组装的输入。
        ({"name": r["city"], "value": r["ershou"]} for r in rows),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        key=lambda x: x["value"],  # 计算或更新key中间数据，作为后续业务判断、统计或响应组装的输入。
        reverse=True,  # 计算或更新reverse中间数据，作为后续业务判断、统计或响应组装的输入。
    )[:10]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        "ershou_total": sum(r["ershou"] for r in rows),  # 把ershou_total字段写入响应数据，供前端页面、图表或后续接口读取。
        "xinfang_total": sum(r["xinfang"] for r in rows),  # 把xinfang_total字段写入响应数据，供前端页面、图表或后续接口读取。
        "zufang_total": sum(r["zufang"] for r in rows),  # 把zufang_total字段写入响应数据，供前端页面、图表或后续接口读取。
        "province_count": len({r["province"] for r in rows}),  # 把province_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "city_count": len(rows),  # 把city_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "top_cities": top_cities,  # 把top_cities字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def provinces() -> list[dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """各省聚合（二手房/新房/租房合计 + 城市数），按二手房降序。"""
    agg: dict[str, dict] = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    for r in _rows():  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        a = agg.setdefault(  # 计算或更新a中间数据，作为后续业务判断、统计或响应组装的输入。
            r["province"],  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            {"name": r["province"], "ershou": 0, "xinfang": 0, "zufang": 0, "city_count": 0},  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        a["ershou"] += r["ershou"]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        a["xinfang"] += r["xinfang"]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        a["zufang"] += r["zufang"]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        a["city_count"] += 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    rows = sorted(agg.values(), key=lambda x: x["ershou"], reverse=True)  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
    for i, r in enumerate(rows, 1):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        r["rank"] = i  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return rows  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def cities(province: str) -> list[dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """某省下属城市列表，按二手房降序。province 可传长名或短名。"""
    key = normalize_name(province)  # 计算或更新key中间数据，作为后续业务判断、统计或响应组装的输入。
    rows = [  # 初始化查询结果集合列表，用于收集清洗后的多条业务数据。
        {"name": r["city"], "ershou": r["ershou"], "xinfang": r["xinfang"], "zufang": r["zufang"]}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        for r in _rows()  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        if r["province"] == key  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return sorted(rows, key=lambda x: x["ershou"], reverse=True)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


# ===== 基于真实采集房源（Property 表）的聚合 —— 供大屏「真实数据」模式 =====
# 区域名沿用 normalize_name，与地图 GeoJSON（DataV）一致；City.province / City.name
# 入库时已是短名，可直接匹配。

def _rooms_bucket(rooms: int) -> str:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """根据户型室数生成户型区间标签。"""
    r = rooms or 0  # 计算或更新r中间数据，作为后续业务判断、统计或响应组装的输入。
    if r <= 1:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return "1室"  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    if r == 2:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return "2室"  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    if r == 3:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return "3室"  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return "4室+"  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def _clean_text(value: str) -> str:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""
    value = (value or "").strip()  # 计算或更新value中间数据，作为后续业务判断、统计或响应组装的输入。
    if value in {"None", "暂无数据", "未知"}:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return ""  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    return value  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


_CHONGQING_AREA_ADMIN = {  # 初始化_CHONGQING_AREA_ADMIN中间数据字典，用于承载接口返回或中间聚合结果。
    "西永": "沙坪坝区",  # 把西永字段写入响应数据，供前端页面、图表或后续接口读取。
    "大学城": "沙坪坝区",  # 把大学城字段写入响应数据，供前端页面、图表或后续接口读取。
    "陈家桥": "沙坪坝区",  # 把陈家桥字段写入响应数据，供前端页面、图表或后续接口读取。
    "天星桥": "沙坪坝区",  # 把天星桥字段写入响应数据，供前端页面、图表或后续接口读取。
    "小龙坎": "沙坪坝区",  # 把小龙坎字段写入响应数据，供前端页面、图表或后续接口读取。
    "沙正街": "沙坪坝区",  # 把沙正街字段写入响应数据，供前端页面、图表或后续接口读取。
    "龙洲湾": "巴南区",  # 把龙洲湾字段写入响应数据，供前端页面、图表或后续接口读取。
    "李家沱": "巴南区",  # 把李家沱字段写入响应数据，供前端页面、图表或后续接口读取。
    "鱼洞": "巴南区",  # 把鱼洞字段写入响应数据，供前端页面、图表或后续接口读取。
    "鹿角": "巴南区",  # 把鹿角字段写入响应数据，供前端页面、图表或后续接口读取。
    "融汇半岛": "巴南区",  # 把融汇半岛字段写入响应数据，供前端页面、图表或后续接口读取。
    "南坪": "南岸区",  # 把南坪字段写入响应数据，供前端页面、图表或后续接口读取。
    "融侨半岛": "南岸区",  # 把融侨半岛字段写入响应数据，供前端页面、图表或后续接口读取。
    "茶园新区": "南岸区",  # 把茶园新区字段写入响应数据，供前端页面、图表或后续接口读取。
    "弹子石": "南岸区",  # 把弹子石字段写入响应数据，供前端页面、图表或后续接口读取。
    "杨家坪": "九龙坡区",  # 把杨家坪字段写入响应数据，供前端页面、图表或后续接口读取。
    "石坪桥": "九龙坡区",  # 把石坪桥字段写入响应数据，供前端页面、图表或后续接口读取。
    "彩云湖": "九龙坡区",  # 把彩云湖字段写入响应数据，供前端页面、图表或后续接口读取。
    "马王乡": "九龙坡区",  # 把马王乡字段写入响应数据，供前端页面、图表或后续接口读取。
    "黄桷坪": "九龙坡区",  # 把黄桷坪字段写入响应数据，供前端页面、图表或后续接口读取。
    "九宫庙": "大渡口区",  # 把九宫庙字段写入响应数据，供前端页面、图表或后续接口读取。
    "双山": "大渡口区",  # 把双山字段写入响应数据，供前端页面、图表或后续接口读取。
    "北滨路": "江北区",  # 把北滨路字段写入响应数据，供前端页面、图表或后续接口读取。
    "海尔路": "江北区",  # 把海尔路字段写入响应数据，供前端页面、图表或后续接口读取。
    "南桥寺": "江北区",  # 把南桥寺字段写入响应数据，供前端页面、图表或后续接口读取。
    "石子山": "江北区",  # 把石子山字段写入响应数据，供前端页面、图表或后续接口读取。
    "鱼嘴": "江北区",  # 把鱼嘴字段写入响应数据，供前端页面、图表或后续接口读取。
    "两路口": "渝中区",  # 把两路口字段写入响应数据，供前端页面、图表或后续接口读取。
    "大溪沟": "渝中区",  # 把大溪沟字段写入响应数据，供前端页面、图表或后续接口读取。
    "中央公园": "渝北区",  # 把中央公园字段写入响应数据，供前端页面、图表或后续接口读取。
    "中央公园东区": "渝北区",  # 把中央公园东区字段写入响应数据，供前端页面、图表或后续接口读取。
    "悦来": "渝北区",  # 把悦来字段写入响应数据，供前端页面、图表或后续接口读取。
    "汽博中心": "渝北区",  # 把汽博中心字段写入响应数据，供前端页面、图表或后续接口读取。
    "礼嘉": "渝北区",  # 把礼嘉字段写入响应数据，供前端页面、图表或后续接口读取。
    "空港新城": "渝北区",  # 把空港新城字段写入响应数据，供前端页面、图表或后续接口读取。
    "黄泥磅": "渝北区",  # 把黄泥磅字段写入响应数据，供前端页面、图表或后续接口读取。
    "龙兴": "渝北区",  # 把龙兴字段写入响应数据，供前端页面、图表或后续接口读取。
    "龙溪": "渝北区",  # 把龙溪字段写入响应数据，供前端页面、图表或后续接口读取。
    "鸳鸯": "渝北区",  # 把鸳鸯字段写入响应数据，供前端页面、图表或后续接口读取。
    "大竹林": "渝北区",  # 把大竹林字段写入响应数据，供前端页面、图表或后续接口读取。
    "蔡家": "北碚区",  # 把蔡家字段写入响应数据，供前端页面、图表或后续接口读取。
    "璧山": "璧山区",  # 把璧山字段写入响应数据，供前端页面、图表或后续接口读取。
    "双福新区": "江津区",  # 把双福新区字段写入响应数据，供前端页面、图表或后续接口读取。
    "周家坝": "万州区",  # 把周家坝字段写入响应数据，供前端页面、图表或后续接口读取。
    "桃花新城": "长寿区",  # 把桃花新城字段写入响应数据，供前端页面、图表或后续接口读取。
}  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


@lru_cache(maxsize=1)  # 把下方函数注册为路由、权限校验或框架回调入口。
def _business_area_admin_map() -> dict[tuple[str, str], str]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Map (city, business area) to administrative district from raw TSV.

    The imported ``districts.name`` for Shandong data is mostly the business
    area column (``quyu``). The city-level DataV map, however, uses official
    administrative districts (``region``). This lookup lets the big screen roll
    business areas up to the matching map regions without changing property
    detail records.
    """
    mapping: dict[tuple[str, str], dict[str, int]] = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    if HOUSE_INFO_FILE.exists():  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        with open(HOUSE_INFO_FILE, encoding="utf-8-sig", newline="") as f:  # 在受控上下文中处理文件、网络或数据库资源，避免资源泄漏。
            for row in csv.DictReader(f, delimiter="\t"):  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
                city = normalize_name(_clean_text(row.get("city", "")))  # 计算或更新city中间数据，作为后续业务判断、统计或响应组装的输入。
                business_area = normalize_name(_clean_text(row.get("quyu", "")))  # 计算或更新business_area中间数据，作为后续业务判断、统计或响应组装的输入。
                admin = _clean_text(row.get("region", ""))  # 计算或更新admin中间数据，作为后续业务判断、统计或响应组装的输入。
                if not city or not business_area or not admin:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
                    continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
                bucket = mapping.setdefault((city, business_area), {})  # 计算或更新bucket中间数据，作为后续业务判断、统计或响应组装的输入。
                bucket[admin] = bucket.get(admin, 0) + 1  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    result = {  # 初始化处理结果字典，用于承载接口返回或中间聚合结果。
        key: max(counts.items(), key=lambda item: item[1])[0]  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        for key, counts in mapping.items()  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    result.update(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
        {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            ("重庆", normalize_name(area)): admin  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            for area, admin in _CHONGQING_AREA_ADMIN.items()  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return result  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def real_summary() -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """真实房源总量、覆盖省/市/商圈数、平均单价、城市 TOP10、户型分布。"""
    # 真实大屏的首页指标全部来自 Property 表，反映当前已采集入库的数据规模。
    total = db.session.query(func.count(Property.id)).scalar() or 0  # 创建总数统计的数据库查询对象，用于继续叠加过滤和聚合条件。
    avg_price = db.session.query(func.avg(Property.unit_price)).scalar() or 0  # 创建avg_price中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
    province_count = (  # 计算或更新province_count中间数据，作为后续业务判断、统计或响应组装的输入。
        db.session.query(func.count(func.distinct(City.province)))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .filter(City.province.isnot(None))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .scalar()  # 执行查询并取回结果，作为后续数据转换的输入。
        or 0  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    city_count = db.session.query(func.count(func.distinct(District.city_id))).scalar() or 0  # 创建city_count中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。
    district_count = db.session.query(func.count(func.distinct(Property.district_id))).scalar() or 0  # 创建district_count中间数据的数据库查询对象，用于继续叠加过滤和聚合条件。

    top = (  # 计算或更新top中间数据，作为后续业务判断、统计或响应组装的输入。
        db.session.query(City.name, func.count(Property.id).label("c"))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .select_from(Property)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .group_by(City.id)  # 按业务维度分组聚合，生成排行榜或统计指标。
        .order_by(func.count(Property.id).desc())  # 按统计值或业务字段排序，保证返回数据符合展示顺序。
        .limit(10)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    top_cities = [{"name": normalize_name(n), "value": int(c)} for n, c in top]  # 初始化top_cities中间数据列表，用于收集清洗后的多条业务数据。

    order = ["1室", "2室", "3室", "4室+"]  # 初始化order中间数据列表，用于收集清洗后的多条业务数据。
    buckets = {k: 0 for k in order}  # 初始化buckets中间数据字典，用于承载接口返回或中间聚合结果。
    for rooms, c in db.session.query(Property.rooms, func.count(Property.id)).group_by(Property.rooms).all():  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        buckets[_rooms_bucket(rooms)] += int(c)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    room_dist = [{"name": k, "value": buckets[k]} for k in order if buckets[k]]  # 初始化room_dist中间数据列表，用于收集清洗后的多条业务数据。

    return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        "count": int(total),  # 把count字段写入响应数据，供前端页面、图表或后续接口读取。
        "avg_price": round(avg_price or 0),  # 把avg_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "province_count": int(province_count),  # 把province_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "city_count": int(city_count),  # 把city_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "district_count": int(district_count),  # 把district_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "top_cities": top_cities,  # 把top_cities字段写入响应数据，供前端页面、图表或后续接口读取。
        "room_dist": room_dist,  # 把room_dist字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def real_provinces() -> list[dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """各省真实房源数 + 均价 + 城市数 + 商圈数，按房源数降序（全国地图着色 + 排行）。"""
    # 全国地图用省份名作为 key，因此这里按 City.province 聚合房源量和均价。
    rows = (  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
        db.session.query(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            City.province,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.count(Property.id),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.avg(Property.unit_price),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.count(func.distinct(City.id)),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.count(func.distinct(District.id)),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        .select_from(Property)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .filter(City.province.isnot(None))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .group_by(City.province)  # 按业务维度分组聚合，生成排行榜或统计指标。
        .order_by(func.count(Property.id).desc())  # 按统计值或业务字段排序，保证返回数据符合展示顺序。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return [  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "name": normalize_name(prov),  # 把name字段写入响应数据，供前端页面、图表或后续接口读取。
            "count": int(cnt),  # 把count字段写入响应数据，供前端页面、图表或后续接口读取。
            "avg_price": round(avg or 0),  # 把avg_price字段写入响应数据，供前端页面、图表或后续接口读取。
            "city_count": int(cc),  # 把city_count字段写入响应数据，供前端页面、图表或后续接口读取。
            "district_count": int(dc),  # 把district_count字段写入响应数据，供前端页面、图表或后续接口读取。
            "rank": i,  # 把rank字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        for i, (prov, cnt, avg, cc, dc) in enumerate(rows, 1)  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def real_cities(province: str) -> list[dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """某省下属城市真实房源数 + 均价 + 商圈数（省级地图着色 + 城市排行）。"""
    key = normalize_name(province)  # 计算或更新key中间数据，作为后续业务判断、统计或响应组装的输入。
    # 直辖市没有“省 -> 市”的中间层，点击后直接展示行政区聚合。
    if key == "重庆":  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return real_districts("重庆")  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
    rows = (  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
        db.session.query(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            City.name,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            City.province,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.count(Property.id),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.avg(Property.unit_price),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.count(func.distinct(District.id)),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        .select_from(Property)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .group_by(City.id)  # 按业务维度分组聚合，生成排行榜或统计指标。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    out = [  # 初始化out中间数据列表，用于收集清洗后的多条业务数据。
        {  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "name": normalize_name(name),  # 把name字段写入响应数据，供前端页面、图表或后续接口读取。
            "count": int(cnt),  # 把count字段写入响应数据，供前端页面、图表或后续接口读取。
            "avg_price": round(avg or 0),  # 把avg_price字段写入响应数据，供前端页面、图表或后续接口读取。
            "district_count": int(dc),  # 把district_count字段写入响应数据，供前端页面、图表或后续接口读取。
        }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        for name, prov, cnt, avg, dc in rows  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        if normalize_name(prov) == key  # 根据当前输入、查询结果或数据状态选择对应处理分支。
    ]  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    return sorted(out, key=lambda x: x["count"], reverse=True)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def real_districts(city: str) -> list[dict]:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """某城市行政区真实房源数 + 均价（市级地图着色 + 行政区排行）。

    Shandong imported data stores business areas as ``District.name``. For city
    maps, aggregate those business areas back to administrative districts using
    the raw TSV's ``region`` column so labels match DataV boundaries.
    """
    key = normalize_name(city)  # 计算或更新key中间数据，作为后续业务判断、统计或响应组装的输入。
    area_to_admin = _business_area_admin_map()  # 计算或更新area_to_admin中间数据，作为后续业务判断、统计或响应组装的输入。
    # 先按导入时的 District.name 聚合，再用原始 TSV 映射把商圈归并到行政区，
    # 这样返回名称能和城市级 GeoJSON 边界对上。
    rows = (  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
        db.session.query(  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            District.name,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            City.name,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.count(Property.id),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.avg(Property.unit_price),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.sum(Property.unit_price),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            func.count(func.distinct(District.id)),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        .select_from(Property)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .group_by(District.id)  # 按业务维度分组聚合，生成排行榜或统计指标。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    agg: dict[str, dict] = {}  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    for dname, cname, cnt, avg, price_sum, business_count in rows:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        if normalize_name(cname) != key:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        admin = area_to_admin.get((key, normalize_name(dname)), dname)  # 计算或更新admin中间数据，作为后续业务判断、统计或响应组装的输入。
        item = agg.setdefault(  # 计算或更新单条数据，作为后续业务判断、统计或响应组装的输入。
            admin,  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            {"name": admin, "count": 0, "price_sum": 0.0, "district_count": 0},  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        item["count"] += int(cnt)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        item["price_sum"] += float(price_sum or 0)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        item["district_count"] += int(business_count or 0)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    out = []  # 初始化out中间数据列表，用于收集清洗后的多条业务数据。
    for item in agg.values():  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        count = item["count"]  # 计算或更新count中间数据，作为后续业务判断、统计或响应组装的输入。
        out.append({  # 展开当前业务处理块，继续组织查询条件、数据结构或控制流程。
            "name": item["name"],  # 把name字段写入响应数据，供前端页面、图表或后续接口读取。
            "count": count,  # 把count字段写入响应数据，供前端页面、图表或后续接口读取。
            "avg_price": round(item["price_sum"] / count) if count else 0,  # 把avg_price字段写入响应数据，供前端页面、图表或后续接口读取。
            "district_count": item["district_count"],  # 把district_count字段写入响应数据，供前端页面、图表或后续接口读取。
        })  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    return sorted(out, key=lambda x: x["count"], reverse=True)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。


def real_area_properties(city: str, area: str, limit: int = 800) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """Property points for a city-level administrative area on the big screen."""
    city_key = normalize_name(city)  # 计算或更新city_key中间数据，作为后续业务判断、统计或响应组装的输入。
    area_key = normalize_name(area)  # 计算或更新area_key中间数据，作为后续业务判断、统计或响应组装的输入。
    limit = min(max(int(limit or 800), 1), 2000)  # 计算或更新limit中间数据，作为后续业务判断、统计或响应组装的输入。
    area_to_admin = _business_area_admin_map()  # 计算或更新area_to_admin中间数据，作为后续业务判断、统计或响应组装的输入。

    # 前端点击的是行政区名称，数据库里可能存的是商圈名；先找出属于该行政区的所有 District.id。
    district_rows = (  # 计算或更新district_rows中间数据，作为后续业务判断、统计或响应组装的输入。
        db.session.query(District.id, District.name, City.name)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获得跨城市、区域或房源维度的数据。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    district_ids = []  # 初始化district_ids中间数据列表，用于收集清洗后的多条业务数据。
    for district_id, district_name, city_name in district_rows:  # 遍历当前数据集合，逐项完成清洗、聚合、入库或响应组装。
        if normalize_name(city_name) != city_key:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            continue  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        admin = area_to_admin.get((city_key, normalize_name(district_name)), district_name)  # 计算或更新admin中间数据，作为后续业务判断、统计或响应组装的输入。
        if normalize_name(admin) == area_key:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
            district_ids.append(district_id)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。

    if not district_ids:  # 根据当前输入、查询结果或数据状态选择对应处理分支。
        return _empty_area_payload(city, area)  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。

    total = (  # 计算或更新总数统计，作为后续业务判断、统计或响应组装的输入。
        db.session.query(func.count(Property.id))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .filter(Property.district_id.in_(district_ids))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .scalar()  # 执行查询并取回结果，作为后续数据转换的输入。
        or 0  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    avg_price = (  # 计算或更新avg_price中间数据，作为后续业务判断、统计或响应组装的输入。
        db.session.query(func.avg(Property.unit_price))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .filter(Property.district_id.in_(district_ids), Property.unit_price.isnot(None))  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
        .scalar()  # 执行查询并取回结果，作为后续数据转换的输入。
        or 0  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    coordinate_count = (  # 计算或更新coordinate_count中间数据，作为后续业务判断、统计或响应组装的输入。
        db.session.query(func.count(Property.id))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .filter(  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
            Property.district_id.in_(district_ids),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            Property.lng.isnot(None),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            Property.lat.isnot(None),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        .scalar()  # 执行查询并取回结果，作为后续数据转换的输入。
        or 0  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    center = (  # 计算或更新center中间数据，作为后续业务判断、统计或响应组装的输入。
        db.session.query(func.avg(Property.lng), func.avg(Property.lat))  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .filter(  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
            Property.district_id.in_(district_ids),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            Property.lng.isnot(None),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            Property.lat.isnot(None),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        .first()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
    # 百度地图只绘制有经纬度的房源点，列表按单价倒序取前 limit 条，避免一次返回过大。
    rows = (  # 计算或更新查询结果集合，作为后续业务判断、统计或响应组装的输入。
        db.session.query(Property)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .filter(  # 给数据库查询追加过滤条件，收窄本次统计或列表的数据范围。
            Property.district_id.in_(district_ids),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            Property.lng.isnot(None),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
            Property.lat.isnot(None),  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        .order_by(Property.unit_price.desc(), Property.id.asc())  # 按统计值或业务字段排序，保证返回数据符合展示顺序。
        .limit(limit)  # 执行当前业务步骤，推动数据从输入、处理到输出继续流转。
        .all()  # 执行查询并取回结果，作为后续数据转换的输入。
    )  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。

    return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        "city": normalize_name(city),  # 把city字段写入响应数据，供前端页面、图表或后续接口读取。
        "area": area,  # 把area字段写入响应数据，供前端页面、图表或后续接口读取。
        "property_count": int(total),  # 把property_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "coordinate_count": int(coordinate_count),  # 把coordinate_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "returned_count": len(rows),  # 把returned_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "avg_price": round(avg_price or 0),  # 把avg_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "center": {  # 把center字段写入响应数据，供前端页面、图表或后续接口读取。
            "lng": round(center[0], 6) if center and center[0] is not None else None,  # 把lng字段写入响应数据，供前端页面、图表或后续接口读取。
            "lat": round(center[1], 6) if center and center[1] is not None else None,  # 把lat字段写入响应数据，供前端页面、图表或后续接口读取。
        },  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
        "items": [_property_point(p) for p in rows],  # 把items字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def _empty_area_payload(city: str, area: str) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """生成空区域查询结果，保持接口返回结构稳定。"""
    return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        "city": normalize_name(city),  # 把city字段写入响应数据，供前端页面、图表或后续接口读取。
        "area": area,  # 把area字段写入响应数据，供前端页面、图表或后续接口读取。
        "property_count": 0,  # 把property_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "coordinate_count": 0,  # 把coordinate_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "returned_count": 0,  # 把returned_count字段写入响应数据，供前端页面、图表或后续接口读取。
        "avg_price": 0,  # 把avg_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "center": {"lng": None, "lat": None},  # 把center字段写入响应数据，供前端页面、图表或后续接口读取。
        "items": [],  # 把items字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。


def _property_point(prop: Property) -> dict:  # 定义函数入口，将输入参数转换为业务数据或接口响应。
    """将房源模型转换为地图点位和列表展示数据。"""
    return {  # 返回已经整理好的业务数据，交给接口调用方或上层逻辑继续使用。
        "id": prop.id,  # 把id字段写入响应数据，供前端页面、图表或后续接口读取。
        "title": prop.title,  # 把title字段写入响应数据，供前端页面、图表或后续接口读取。
        "district_name": prop.district.name if prop.district else None,  # 把district_name字段写入响应数据，供前端页面、图表或后续接口读取。
        "total_price": prop.total_price,  # 把total_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "unit_price": prop.unit_price,  # 把unit_price字段写入响应数据，供前端页面、图表或后续接口读取。
        "area": prop.area,  # 把area字段写入响应数据，供前端页面、图表或后续接口读取。
        "layout": prop.layout(),  # 把layout字段写入响应数据，供前端页面、图表或后续接口读取。
        "lng": prop.lng,  # 把lng字段写入响应数据，供前端页面、图表或后续接口读取。
        "lat": prop.lat,  # 把lat字段写入响应数据，供前端页面、图表或后续接口读取。
    }  # 完成当前查询、参数或数据结构的组装，使上层表达式可以继续执行。
