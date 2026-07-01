"""全国二手房数据服务（基于真实 province_data.csv）。

数据列：省份, 城市, 二手房, 新房, 租房（均为挂牌量）。
为与地图（DataV GeoJSON）的区域名匹配，名称统一做规范化处理。
"""
import csv  # 导入 csv 模块，为当前文件提供所需功能。
from functools import lru_cache  # 从 functools 导入 lru_cache，供本文件后续逻辑调用。
from pathlib import Path  # 从 pathlib 导入 Path，供本文件后续逻辑调用。

from sqlalchemy import func  # 从 sqlalchemy 导入 func，供本文件后续逻辑调用。

from extensions import db  # 从 extensions 导入 db，供本文件后续逻辑调用。
from models import City, District, Property  # 从 models 导入 City, District, Property，供本文件后续逻辑调用。

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "province_data.csv"  # 设置 DATA_FILE 的值，供后续业务判断、查询或响应组装使用。
HOUSE_INFO_FILE = Path(__file__).resolve().parent.parent / "data" / "raw" / "house_info.tsv"  # 设置 HOUSE_INFO_FILE 的值，供后续业务判断、查询或响应组装使用。

# 长名 -> 短名（自治区/特别行政区），其余按后缀裁剪。
_SPECIAL = {  # 设置 _SPECIAL 的值，供后续业务判断、查询或响应组装使用。
    "内蒙古自治区": "内蒙古",  # 保留字符串内容，作为说明文本或页面展示文案。
    "广西壮族自治区": "广西",  # 保留字符串内容，作为说明文本或页面展示文案。
    "宁夏回族自治区": "宁夏",  # 保留字符串内容，作为说明文本或页面展示文案。
    "新疆维吾尔自治区": "新疆",  # 保留字符串内容，作为说明文本或页面展示文案。
    "西藏自治区": "西藏",  # 保留字符串内容，作为说明文本或页面展示文案。
    "香港特别行政区": "香港",  # 保留字符串内容，作为说明文本或页面展示文案。
    "澳门特别行政区": "澳门",  # 保留字符串内容，作为说明文本或页面展示文案。
}  # 结束当前多行数据结构或函数调用。


def normalize_name(name: str) -> str:  # 定义 normalize_name 函数，集中处理这一段业务逻辑。
    """北京市->北京、山东省->山东、崂山区->崂山、内蒙古自治区->内蒙古。幂等。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    if not name:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return ""  # 返回处理后的结果给调用方继续使用。
    name = name.strip()  # 设置 name 的值，供后续业务判断、查询或响应组装使用。
    if name in _SPECIAL:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return _SPECIAL[name]  # 返回处理后的结果给调用方继续使用。
    for suffix in ("特别行政区", "自治区", "省", "市", "区", "县"):  # 遍历当前数据集合，逐项完成处理。
        if name.endswith(suffix) and len(name) - len(suffix) >= 2:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            return name[: -len(suffix)]  # 返回处理后的结果给调用方继续使用。
    return name  # 返回处理后的结果给调用方继续使用。


def _num(value: str) -> int:  # 定义 _num 函数，集中处理这一段业务逻辑。
    """将输入值安全转换为浮点数，失败时返回零。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    value = (value or "").strip().replace(",", "")  # 设置 value 的值，供后续业务判断、查询或响应组装使用。
    return int(value) if value.isdigit() else 0  # 返回处理后的结果给调用方继续使用。


@lru_cache(maxsize=1)  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def _rows() -> list[dict]:  # 定义 _rows 函数，集中处理这一段业务逻辑。
    """从全国静态 CSV 数据中读取并缓存原始行。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    rows = []  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
    with open(DATA_FILE, encoding="utf-8-sig") as f:  # 进入上下文管理流程，自动处理资源打开和释放。
        for r in csv.DictReader(f):  # 遍历当前数据集合，逐项完成处理。
            rows.append(  # 执行当前代码行对应的业务处理步骤。
                {  # 执行当前代码行对应的业务处理步骤。
                    "province": normalize_name(r.get("省份", "")),  # 保留字符串内容，作为说明文本或页面展示文案。
                    "city": normalize_name(r.get("城市", "")),  # 保留字符串内容，作为说明文本或页面展示文案。
                    "ershou": _num(r.get("二手房")),  # 保留字符串内容，作为说明文本或页面展示文案。
                    "xinfang": _num(r.get("新房")),  # 保留字符串内容，作为说明文本或页面展示文案。
                    "zufang": _num(r.get("租房")),  # 保留字符串内容，作为说明文本或页面展示文案。
                }  # 结束当前多行数据结构或函数调用。
            )  # 结束当前多行数据结构或函数调用。
    return rows  # 返回处理后的结果给调用方继续使用。


def summary() -> dict:  # 定义 summary 函数，集中处理这一段业务逻辑。
    """返回全国或真实数据模式的总览统计信息。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    rows = _rows()  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
    top_cities = sorted(  # 设置 top_cities 的值，供后续业务判断、查询或响应组装使用。
        ({"name": r["city"], "value": r["ershou"]} for r in rows),  # 执行当前代码行对应的业务处理步骤。
        key=lambda x: x["value"],  # 设置 key 的值，供后续业务判断、查询或响应组装使用。
        reverse=True,  # 设置 reverse 的值，供后续业务判断、查询或响应组装使用。
    )[:10]  # 执行当前代码行对应的业务处理步骤。
    return {  # 返回处理后的结果给调用方继续使用。
        "ershou_total": sum(r["ershou"] for r in rows),  # 保留字符串内容，作为说明文本或页面展示文案。
        "xinfang_total": sum(r["xinfang"] for r in rows),  # 保留字符串内容，作为说明文本或页面展示文案。
        "zufang_total": sum(r["zufang"] for r in rows),  # 保留字符串内容，作为说明文本或页面展示文案。
        "province_count": len({r["province"] for r in rows}),  # 保留字符串内容，作为说明文本或页面展示文案。
        "city_count": len(rows),  # 保留字符串内容，作为说明文本或页面展示文案。
        "top_cities": top_cities,  # 保留字符串内容，作为说明文本或页面展示文案。
    }  # 结束当前多行数据结构或函数调用。


def provinces() -> list[dict]:  # 定义 provinces 函数，集中处理这一段业务逻辑。
    """各省聚合（二手房/新房/租房合计 + 城市数），按二手房降序。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    agg: dict[str, dict] = {}  # 设置 agg: dict[str, dict 的值，供后续业务判断、查询或响应组装使用。
    for r in _rows():  # 遍历当前数据集合，逐项完成处理。
        a = agg.setdefault(  # 设置 a 的值，供后续业务判断、查询或响应组装使用。
            r["province"],  # 执行当前代码行对应的业务处理步骤。
            {"name": r["province"], "ershou": 0, "xinfang": 0, "zufang": 0, "city_count": 0},  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        a["ershou"] += r["ershou"]  # 设置 a["ershou"] + 的值，供后续业务判断、查询或响应组装使用。
        a["xinfang"] += r["xinfang"]  # 设置 a["xinfang"] + 的值，供后续业务判断、查询或响应组装使用。
        a["zufang"] += r["zufang"]  # 设置 a["zufang"] + 的值，供后续业务判断、查询或响应组装使用。
        a["city_count"] += 1  # 设置 a["city_count"] + 的值，供后续业务判断、查询或响应组装使用。
    rows = sorted(agg.values(), key=lambda x: x["ershou"], reverse=True)  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
    for i, r in enumerate(rows, 1):  # 遍历当前数据集合，逐项完成处理。
        r["rank"] = i  # 设置 r["rank" 的值，供后续业务判断、查询或响应组装使用。
    return rows  # 返回处理后的结果给调用方继续使用。


def cities(province: str) -> list[dict]:  # 定义 cities 函数，集中处理这一段业务逻辑。
    """某省下属城市列表，按二手房降序。province 可传长名或短名。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    key = normalize_name(province)  # 设置 key 的值，供后续业务判断、查询或响应组装使用。
    rows = [  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        {"name": r["city"], "ershou": r["ershou"], "xinfang": r["xinfang"], "zufang": r["zufang"]}  # 执行当前代码行对应的业务处理步骤。
        for r in _rows()  # 遍历当前数据集合，逐项完成处理。
        if r["province"] == key  # 判断当前条件是否成立，决定是否进入对应处理分支。
    ]  # 结束当前多行数据结构或函数调用。
    return sorted(rows, key=lambda x: x["ershou"], reverse=True)  # 返回处理后的结果给调用方继续使用。


# ===== 基于真实采集房源（Property 表）的聚合 —— 供大屏「真实数据」模式 =====
# 区域名沿用 normalize_name，与地图 GeoJSON（DataV）一致；City.province / City.name
# 入库时已是短名，可直接匹配。

def _rooms_bucket(rooms: int) -> str:  # 定义 _rooms_bucket 函数，集中处理这一段业务逻辑。
    """根据户型室数生成户型区间标签。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    r = rooms or 0  # 设置 r 的值，供后续业务判断、查询或响应组装使用。
    if r <= 1:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return "1室"  # 返回处理后的结果给调用方继续使用。
    if r == 2:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return "2室"  # 返回处理后的结果给调用方继续使用。
    if r == 3:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return "3室"  # 返回处理后的结果给调用方继续使用。
    return "4室+"  # 返回处理后的结果给调用方继续使用。


def _clean_text(value: str) -> str:  # 定义 _clean_text 函数，集中处理这一段业务逻辑。
    """清理输入文本，统一处理空值、空白和无效占位内容。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    value = (value or "").strip()  # 设置 value 的值，供后续业务判断、查询或响应组装使用。
    if value in {"None", "暂无数据", "未知"}:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return ""  # 返回处理后的结果给调用方继续使用。
    return value  # 返回处理后的结果给调用方继续使用。


_CHONGQING_AREA_ADMIN = {  # 设置 _CHONGQING_AREA_ADMIN 的值，供后续业务判断、查询或响应组装使用。
    "西永": "沙坪坝区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "大学城": "沙坪坝区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "陈家桥": "沙坪坝区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "天星桥": "沙坪坝区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "小龙坎": "沙坪坝区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "沙正街": "沙坪坝区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "龙洲湾": "巴南区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "李家沱": "巴南区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "鱼洞": "巴南区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "鹿角": "巴南区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "融汇半岛": "巴南区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "南坪": "南岸区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "融侨半岛": "南岸区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "茶园新区": "南岸区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "弹子石": "南岸区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "杨家坪": "九龙坡区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "石坪桥": "九龙坡区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "彩云湖": "九龙坡区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "马王乡": "九龙坡区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "黄桷坪": "九龙坡区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "九宫庙": "大渡口区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "双山": "大渡口区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "北滨路": "江北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "海尔路": "江北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "南桥寺": "江北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "石子山": "江北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "鱼嘴": "江北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "两路口": "渝中区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "大溪沟": "渝中区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "中央公园": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "中央公园东区": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "悦来": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "汽博中心": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "礼嘉": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "空港新城": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "黄泥磅": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "龙兴": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "龙溪": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "鸳鸯": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "大竹林": "渝北区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "蔡家": "北碚区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "璧山": "璧山区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "双福新区": "江津区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "周家坝": "万州区",  # 保留字符串内容，作为说明文本或页面展示文案。
    "桃花新城": "长寿区",  # 保留字符串内容，作为说明文本或页面展示文案。
}  # 结束当前多行数据结构或函数调用。


@lru_cache(maxsize=1)  # 把下方函数注册为框架回调、路由入口或权限装饰逻辑。
def _business_area_admin_map() -> dict[tuple[str, str], str]:  # 定义 _business_area_admin_map 函数，集中处理这一段业务逻辑。
    """Map (city, business area) to administrative district from raw TSV.

    The imported ``districts.name`` for Shandong data is mostly the business
    area column (``quyu``). The city-level DataV map, however, uses official
    administrative districts (``region``). This lookup lets the big screen roll
    business areas up to the matching map regions without changing property
    detail records.
    """
    mapping: dict[tuple[str, str], dict[str, int]] = {}  # 设置 mapping: dict[tuple[str, str], dict[str, int 的值，供后续业务判断、查询或响应组装使用。

    if HOUSE_INFO_FILE.exists():  # 判断当前条件是否成立，决定是否进入对应处理分支。
        with open(HOUSE_INFO_FILE, encoding="utf-8-sig", newline="") as f:  # 进入上下文管理流程，自动处理资源打开和释放。
            for row in csv.DictReader(f, delimiter="\t"):  # 遍历当前数据集合，逐项完成处理。
                city = normalize_name(_clean_text(row.get("city", "")))  # 设置 city 的值，供后续业务判断、查询或响应组装使用。
                business_area = normalize_name(_clean_text(row.get("quyu", "")))  # 设置 business_area 的值，供后续业务判断、查询或响应组装使用。
                admin = _clean_text(row.get("region", ""))  # 设置 admin 的值，供后续业务判断、查询或响应组装使用。
                if not city or not business_area or not admin:  # 判断当前条件是否成立，决定是否进入对应处理分支。
                    continue  # 跳过当前循环项，继续处理下一项。
                bucket = mapping.setdefault((city, business_area), {})  # 设置 bucket 的值，供后续业务判断、查询或响应组装使用。
                bucket[admin] = bucket.get(admin, 0) + 1  # 设置 bucket[admin 的值，供后续业务判断、查询或响应组装使用。

    result = {  # 设置 result 的值，供后续业务判断、查询或响应组装使用。
        key: max(counts.items(), key=lambda item: item[1])[0]  # 设置 key: max(counts.items(), key 的值，供后续业务判断、查询或响应组装使用。
        for key, counts in mapping.items()  # 遍历当前数据集合，逐项完成处理。
    }  # 结束当前多行数据结构或函数调用。
    result.update(  # 执行当前代码行对应的业务处理步骤。
        {  # 执行当前代码行对应的业务处理步骤。
            ("重庆", normalize_name(area)): admin  # 执行当前代码行对应的业务处理步骤。
            for area, admin in _CHONGQING_AREA_ADMIN.items()  # 遍历当前数据集合，逐项完成处理。
        }  # 结束当前多行数据结构或函数调用。
    )  # 结束当前多行数据结构或函数调用。
    return result  # 返回处理后的结果给调用方继续使用。


def real_summary() -> dict:  # 定义 real_summary 函数，集中处理这一段业务逻辑。
    """真实房源总量、覆盖省/市/商圈数、平均单价、城市 TOP10、户型分布。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    # 真实大屏的首页指标全部来自 Property 表，反映当前已采集入库的数据规模。
    total = db.session.query(func.count(Property.id)).scalar() or 0  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    avg_price = db.session.query(func.avg(Property.unit_price)).scalar() or 0  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    province_count = (  # 设置 province_count 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(func.count(func.distinct(City.province)))  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .filter(City.province.isnot(None))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .scalar()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
        or 0  # 执行当前代码行对应的业务处理步骤。
    )  # 结束当前多行数据结构或函数调用。
    city_count = db.session.query(func.count(func.distinct(District.city_id))).scalar() or 0  # 构造数据库查询，用于读取、筛选或聚合业务数据。
    district_count = db.session.query(func.count(func.distinct(Property.district_id))).scalar() or 0  # 构造数据库查询，用于读取、筛选或聚合业务数据。

    top = (  # 设置 top 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(City.name, func.count(Property.id).label("c"))  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .select_from(Property)  # 执行当前代码行对应的业务处理步骤。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .group_by(City.id)  # 按指定业务维度分组，生成聚合统计结果。
        .order_by(func.count(Property.id).desc())  # 按指定字段或统计值排序，保证返回顺序符合页面展示需要。
        .limit(10)  # 执行当前代码行对应的业务处理步骤。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    top_cities = [{"name": normalize_name(n), "value": int(c)} for n, c in top]  # 设置 top_cities 的值，供后续业务判断、查询或响应组装使用。

    order = ["1室", "2室", "3室", "4室+"]  # 设置 order 的值，供后续业务判断、查询或响应组装使用。
    buckets = {k: 0 for k in order}  # 设置 buckets 的值，供后续业务判断、查询或响应组装使用。
    for rooms, c in db.session.query(Property.rooms, func.count(Property.id)).group_by(Property.rooms).all():  # 遍历当前数据集合，逐项完成处理。
        buckets[_rooms_bucket(rooms)] += int(c)  # 设置 buckets[_rooms_bucket(rooms)] + 的值，供后续业务判断、查询或响应组装使用。
    room_dist = [{"name": k, "value": buckets[k]} for k in order if buckets[k]]  # 设置 room_dist 的值，供后续业务判断、查询或响应组装使用。

    return {  # 返回处理后的结果给调用方继续使用。
        "count": int(total),  # 保留字符串内容，作为说明文本或页面展示文案。
        "avg_price": round(avg_price or 0),  # 保留字符串内容，作为说明文本或页面展示文案。
        "province_count": int(province_count),  # 保留字符串内容，作为说明文本或页面展示文案。
        "city_count": int(city_count),  # 保留字符串内容，作为说明文本或页面展示文案。
        "district_count": int(district_count),  # 保留字符串内容，作为说明文本或页面展示文案。
        "top_cities": top_cities,  # 保留字符串内容，作为说明文本或页面展示文案。
        "room_dist": room_dist,  # 保留字符串内容，作为说明文本或页面展示文案。
    }  # 结束当前多行数据结构或函数调用。


def real_provinces() -> list[dict]:  # 定义 real_provinces 函数，集中处理这一段业务逻辑。
    """各省真实房源数 + 均价 + 城市数 + 商圈数，按房源数降序（全国地图着色 + 排行）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    # 全国地图用省份名作为 key，因此这里按 City.province 聚合房源量和均价。
    rows = (  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(  # 构造数据库查询，用于读取、筛选或聚合业务数据。
            City.province,  # 执行当前代码行对应的业务处理步骤。
            func.count(Property.id),  # 执行当前代码行对应的业务处理步骤。
            func.avg(Property.unit_price),  # 执行当前代码行对应的业务处理步骤。
            func.count(func.distinct(City.id)),  # 执行当前代码行对应的业务处理步骤。
            func.count(func.distinct(District.id)),  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        .select_from(Property)  # 执行当前代码行对应的业务处理步骤。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .filter(City.province.isnot(None))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .group_by(City.province)  # 按指定业务维度分组，生成聚合统计结果。
        .order_by(func.count(Property.id).desc())  # 按指定字段或统计值排序，保证返回顺序符合页面展示需要。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    return [  # 返回处理后的结果给调用方继续使用。
        {  # 执行当前代码行对应的业务处理步骤。
            "name": normalize_name(prov),  # 保留字符串内容，作为说明文本或页面展示文案。
            "count": int(cnt),  # 保留字符串内容，作为说明文本或页面展示文案。
            "avg_price": round(avg or 0),  # 保留字符串内容，作为说明文本或页面展示文案。
            "city_count": int(cc),  # 保留字符串内容，作为说明文本或页面展示文案。
            "district_count": int(dc),  # 保留字符串内容，作为说明文本或页面展示文案。
            "rank": i,  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
        for i, (prov, cnt, avg, cc, dc) in enumerate(rows, 1)  # 遍历当前数据集合，逐项完成处理。
    ]  # 结束当前多行数据结构或函数调用。


def real_cities(province: str) -> list[dict]:  # 定义 real_cities 函数，集中处理这一段业务逻辑。
    """某省下属城市真实房源数 + 均价 + 商圈数（省级地图着色 + 城市排行）。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    key = normalize_name(province)  # 设置 key 的值，供后续业务判断、查询或响应组装使用。
    # 直辖市没有“省 -> 市”的中间层，点击后直接展示行政区聚合。
    if key == "重庆":  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return real_districts("重庆")  # 返回处理后的结果给调用方继续使用。
    rows = (  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(  # 构造数据库查询，用于读取、筛选或聚合业务数据。
            City.name,  # 执行当前代码行对应的业务处理步骤。
            City.province,  # 执行当前代码行对应的业务处理步骤。
            func.count(Property.id),  # 执行当前代码行对应的业务处理步骤。
            func.avg(Property.unit_price),  # 执行当前代码行对应的业务处理步骤。
            func.count(func.distinct(District.id)),  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        .select_from(Property)  # 执行当前代码行对应的业务处理步骤。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .group_by(City.id)  # 按指定业务维度分组，生成聚合统计结果。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    out = [  # 设置 out 的值，供后续业务判断、查询或响应组装使用。
        {  # 执行当前代码行对应的业务处理步骤。
            "name": normalize_name(name),  # 保留字符串内容，作为说明文本或页面展示文案。
            "count": int(cnt),  # 保留字符串内容，作为说明文本或页面展示文案。
            "avg_price": round(avg or 0),  # 保留字符串内容，作为说明文本或页面展示文案。
            "district_count": int(dc),  # 保留字符串内容，作为说明文本或页面展示文案。
        }  # 结束当前多行数据结构或函数调用。
        for name, prov, cnt, avg, dc in rows  # 遍历当前数据集合，逐项完成处理。
        if normalize_name(prov) == key  # 判断当前条件是否成立，决定是否进入对应处理分支。
    ]  # 结束当前多行数据结构或函数调用。
    return sorted(out, key=lambda x: x["count"], reverse=True)  # 返回处理后的结果给调用方继续使用。


def real_districts(city: str) -> list[dict]:  # 定义 real_districts 函数，集中处理这一段业务逻辑。
    """某城市行政区真实房源数 + 均价（市级地图着色 + 行政区排行）。

    Shandong imported data stores business areas as ``District.name``. For city
    maps, aggregate those business areas back to administrative districts using
    the raw TSV's ``region`` column so labels match DataV boundaries.
    """
    key = normalize_name(city)  # 设置 key 的值，供后续业务判断、查询或响应组装使用。
    area_to_admin = _business_area_admin_map()  # 设置 area_to_admin 的值，供后续业务判断、查询或响应组装使用。
    # 先按导入时的 District.name 聚合，再用原始 TSV 映射把商圈归并到行政区，
    # 这样返回名称能和城市级 GeoJSON 边界对上。
    rows = (  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(  # 构造数据库查询，用于读取、筛选或聚合业务数据。
            District.name,  # 执行当前代码行对应的业务处理步骤。
            City.name,  # 执行当前代码行对应的业务处理步骤。
            func.count(Property.id),  # 执行当前代码行对应的业务处理步骤。
            func.avg(Property.unit_price),  # 执行当前代码行对应的业务处理步骤。
            func.sum(Property.unit_price),  # 执行当前代码行对应的业务处理步骤。
            func.count(func.distinct(District.id)),  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        .select_from(Property)  # 执行当前代码行对应的业务处理步骤。
        .join(District, Property.district_id == District.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .group_by(District.id)  # 按指定业务维度分组，生成聚合统计结果。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    agg: dict[str, dict] = {}  # 设置 agg: dict[str, dict 的值，供后续业务判断、查询或响应组装使用。
    for dname, cname, cnt, avg, price_sum, business_count in rows:  # 遍历当前数据集合，逐项完成处理。
        if normalize_name(cname) != key:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            continue  # 跳过当前循环项，继续处理下一项。
        admin = area_to_admin.get((key, normalize_name(dname)), dname)  # 设置 admin 的值，供后续业务判断、查询或响应组装使用。
        item = agg.setdefault(  # 设置 item 的值，供后续业务判断、查询或响应组装使用。
            admin,  # 执行当前代码行对应的业务处理步骤。
            {"name": admin, "count": 0, "price_sum": 0.0, "district_count": 0},  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        item["count"] += int(cnt)  # 设置 item["count"] + 的值，供后续业务判断、查询或响应组装使用。
        item["price_sum"] += float(price_sum or 0)  # 设置 item["price_sum"] + 的值，供后续业务判断、查询或响应组装使用。
        item["district_count"] += int(business_count or 0)  # 设置 item["district_count"] + 的值，供后续业务判断、查询或响应组装使用。

    out = []  # 设置 out 的值，供后续业务判断、查询或响应组装使用。
    for item in agg.values():  # 遍历当前数据集合，逐项完成处理。
        count = item["count"]  # 设置 count 的值，供后续业务判断、查询或响应组装使用。
        out.append({  # 执行当前代码行对应的业务处理步骤。
            "name": item["name"],  # 保留字符串内容，作为说明文本或页面展示文案。
            "count": count,  # 保留字符串内容，作为说明文本或页面展示文案。
            "avg_price": round(item["price_sum"] / count) if count else 0,  # 保留字符串内容，作为说明文本或页面展示文案。
            "district_count": item["district_count"],  # 保留字符串内容，作为说明文本或页面展示文案。
        })  # 结束当前多行数据结构或函数调用。
    return sorted(out, key=lambda x: x["count"], reverse=True)  # 返回处理后的结果给调用方继续使用。


def real_area_properties(city: str, area: str, limit: int = 800) -> dict:  # 定义 real_area_properties 函数，集中处理这一段业务逻辑。
    """Property points for a city-level administrative area on the big screen."""  # 保留字符串内容，作为说明文本或页面展示文案。
    city_key = normalize_name(city)  # 设置 city_key 的值，供后续业务判断、查询或响应组装使用。
    area_key = normalize_name(area)  # 设置 area_key 的值，供后续业务判断、查询或响应组装使用。
    limit = min(max(int(limit or 800), 1), 2000)  # 设置 limit 的值，供后续业务判断、查询或响应组装使用。
    area_to_admin = _business_area_admin_map()  # 设置 area_to_admin 的值，供后续业务判断、查询或响应组装使用。

    # 前端点击的是行政区名称，数据库里可能存的是商圈名；先找出属于该行政区的所有 District.id。
    district_rows = (  # 设置 district_rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(District.id, District.name, City.name)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .join(City, District.city_id == City.id)  # 把关联表纳入查询，获取跨表维度的数据。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    district_ids = []  # 设置 district_ids 的值，供后续业务判断、查询或响应组装使用。
    for district_id, district_name, city_name in district_rows:  # 遍历当前数据集合，逐项完成处理。
        if normalize_name(city_name) != city_key:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            continue  # 跳过当前循环项，继续处理下一项。
        admin = area_to_admin.get((city_key, normalize_name(district_name)), district_name)  # 设置 admin 的值，供后续业务判断、查询或响应组装使用。
        if normalize_name(admin) == area_key:  # 判断当前条件是否成立，决定是否进入对应处理分支。
            district_ids.append(district_id)  # 执行当前代码行对应的业务处理步骤。

    if not district_ids:  # 判断当前条件是否成立，决定是否进入对应处理分支。
        return _empty_area_payload(city, area)  # 返回处理后的结果给调用方继续使用。

    total = (  # 设置 total 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(func.count(Property.id))  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .filter(Property.district_id.in_(district_ids))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .scalar()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
        or 0  # 执行当前代码行对应的业务处理步骤。
    )  # 结束当前多行数据结构或函数调用。
    avg_price = (  # 设置 avg_price 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(func.avg(Property.unit_price))  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .filter(Property.district_id.in_(district_ids), Property.unit_price.isnot(None))  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
        .scalar()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
        or 0  # 执行当前代码行对应的业务处理步骤。
    )  # 结束当前多行数据结构或函数调用。
    coordinate_count = (  # 设置 coordinate_count 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(func.count(Property.id))  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .filter(  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
            Property.district_id.in_(district_ids),  # 执行当前代码行对应的业务处理步骤。
            Property.lng.isnot(None),  # 执行当前代码行对应的业务处理步骤。
            Property.lat.isnot(None),  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        .scalar()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
        or 0  # 执行当前代码行对应的业务处理步骤。
    )  # 结束当前多行数据结构或函数调用。
    center = (  # 设置 center 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(func.avg(Property.lng), func.avg(Property.lat))  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .filter(  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
            Property.district_id.in_(district_ids),  # 执行当前代码行对应的业务处理步骤。
            Property.lng.isnot(None),  # 执行当前代码行对应的业务处理步骤。
            Property.lat.isnot(None),  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        .first()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。
    # 百度地图只绘制有经纬度的房源点，列表按单价倒序取前 limit 条，避免一次返回过大。
    rows = (  # 设置 rows 的值，供后续业务判断、查询或响应组装使用。
        db.session.query(Property)  # 构造数据库查询，用于读取、筛选或聚合业务数据。
        .filter(  # 给数据库查询追加过滤条件，收窄本次处理的数据范围。
            Property.district_id.in_(district_ids),  # 执行当前代码行对应的业务处理步骤。
            Property.lng.isnot(None),  # 执行当前代码行对应的业务处理步骤。
            Property.lat.isnot(None),  # 执行当前代码行对应的业务处理步骤。
        )  # 结束当前多行数据结构或函数调用。
        .order_by(Property.unit_price.desc(), Property.id.asc())  # 按指定字段或统计值排序，保证返回顺序符合页面展示需要。
        .limit(limit)  # 执行当前代码行对应的业务处理步骤。
        .all()  # 执行查询并取回结果，作为后续转换或响应组装的输入。
    )  # 结束当前多行数据结构或函数调用。

    return {  # 返回处理后的结果给调用方继续使用。
        "city": normalize_name(city),  # 保留字符串内容，作为说明文本或页面展示文案。
        "area": area,  # 保留字符串内容，作为说明文本或页面展示文案。
        "property_count": int(total),  # 保留字符串内容，作为说明文本或页面展示文案。
        "coordinate_count": int(coordinate_count),  # 保留字符串内容，作为说明文本或页面展示文案。
        "returned_count": len(rows),  # 保留字符串内容，作为说明文本或页面展示文案。
        "avg_price": round(avg_price or 0),  # 保留字符串内容，作为说明文本或页面展示文案。
        "center": {  # 保留字符串内容，作为说明文本或页面展示文案。
            "lng": round(center[0], 6) if center and center[0] is not None else None,  # 保留字符串内容，作为说明文本或页面展示文案。
            "lat": round(center[1], 6) if center and center[1] is not None else None,  # 保留字符串内容，作为说明文本或页面展示文案。
        },  # 结束当前多行数据结构或函数调用。
        "items": [_property_point(p) for p in rows],  # 保留字符串内容，作为说明文本或页面展示文案。
    }  # 结束当前多行数据结构或函数调用。


def _empty_area_payload(city: str, area: str) -> dict:  # 定义 _empty_area_payload 函数，集中处理这一段业务逻辑。
    """生成空区域查询结果，保持接口返回结构稳定。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return {  # 返回处理后的结果给调用方继续使用。
        "city": normalize_name(city),  # 保留字符串内容，作为说明文本或页面展示文案。
        "area": area,  # 保留字符串内容，作为说明文本或页面展示文案。
        "property_count": 0,  # 保留字符串内容，作为说明文本或页面展示文案。
        "coordinate_count": 0,  # 保留字符串内容，作为说明文本或页面展示文案。
        "returned_count": 0,  # 保留字符串内容，作为说明文本或页面展示文案。
        "avg_price": 0,  # 保留字符串内容，作为说明文本或页面展示文案。
        "center": {"lng": None, "lat": None},  # 保留字符串内容，作为说明文本或页面展示文案。
        "items": [],  # 保留字符串内容，作为说明文本或页面展示文案。
    }  # 结束当前多行数据结构或函数调用。


def _property_point(prop: Property) -> dict:  # 定义 _property_point 函数，集中处理这一段业务逻辑。
    """将房源模型转换为地图点位和列表展示数据。"""  # 保留字符串内容，作为说明文本或页面展示文案。
    return {  # 返回处理后的结果给调用方继续使用。
        "id": prop.id,  # 保留字符串内容，作为说明文本或页面展示文案。
        "title": prop.title,  # 保留字符串内容，作为说明文本或页面展示文案。
        "district_name": prop.district.name if prop.district else None,  # 保留字符串内容，作为说明文本或页面展示文案。
        "total_price": prop.total_price,  # 保留字符串内容，作为说明文本或页面展示文案。
        "unit_price": prop.unit_price,  # 保留字符串内容，作为说明文本或页面展示文案。
        "area": prop.area,  # 保留字符串内容，作为说明文本或页面展示文案。
        "layout": prop.layout(),  # 保留字符串内容，作为说明文本或页面展示文案。
        "lng": prop.lng,  # 保留字符串内容，作为说明文本或页面展示文案。
        "lat": prop.lat,  # 保留字符串内容，作为说明文本或页面展示文案。
    }  # 结束当前多行数据结构或函数调用。
