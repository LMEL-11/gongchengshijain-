"""Lookup extended Shandong listing fields from the raw TSV file."""
import csv
from functools import lru_cache
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
HOUSE_INFO_FILE = BASE_DIR / "data" / "raw" / "house_info.tsv"

DETAIL_FIELDS = {
    "shijian": "listing_date",
    "quanshu": "ownership_type",
    "chanquan": "property_right",
    "diya": "mortgage",
    "maidian": "selling_point",
    "jieshao": "community_intro",
    "huxingjieshao": "layout_intro",
    "jiaotong": "transport_intro",
}


def _clean_text(value):
    if value is None:
        return None
    text = str(value).replace("\u00a0", " ").strip()
    if not text or text in {"None", "暂无数据", "未知"}:
        return None
    return text


@lru_cache(maxsize=1)
def _details_by_url():
    if not HOUSE_INFO_FILE.exists():
        return {}

    details = {}
    with HOUSE_INFO_FILE.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            url = _clean_text(row.get("link"))
            if not url:
                continue
            item = {
                target: _clean_text(row.get(source))
                for source, target in DETAIL_FIELDS.items()
            }
            if any(item.values()):
                details[url] = item
    return details


def get_property_details(source_url):
    """Return extended detail fields for a listing source URL."""
    if not source_url:
        return {}
    return _details_by_url().get(source_url, {})


def clean_detail_dict(data):
    """Remove empty values from a transaction/detail mapping."""
    return {k: v for k, v in (data or {}).items() if _clean_text(v)}


def get_property_transaction_details(prop):
    """Return admin-maintained transaction fields, falling back to raw TSV details."""
    raw = get_property_details(prop.source_url)
    manual = prop.transaction.to_dict() if getattr(prop, "transaction", None) else {}
    return {**clean_detail_dict(raw), **clean_detail_dict(manual)}
