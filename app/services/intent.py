import re

from app.ingestion.forms import normalize_form
from app.schemas import IntentResult

PRODUCT_KEYWORDS = {"推荐", "适合", "喝", "买", "商品", "产品", "茶", "汤包", "膏", "多少钱"}
TCM_KEYWORDS = {
    "为什么",
    "怎么调理",
    "症状",
    "体质",
    "中医",
    "养生",
    "原因",
    "白带",
    "带下",
    "月经",
    "经期",
    "崩漏",
    "痛经",
}


def extract_price_max(query: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*元以内", query)
    return float(match.group(1)) if match else None


def extract_form(query: str) -> str | None:
    for token in ["茶饮", "袋泡茶", "茶", "汤包", "膏滋", "糕点", "丸剂", "零食", "食材", "日用品", "冲饮"]:
        if token in query:
            return normalize_form(token)
    return None


def classify_intent(query: str) -> IntentResult:
    constraints = {}
    form = extract_form(query)
    price_max = extract_price_max(query)
    if form:
        constraints["form"] = form
    if price_max is not None:
        constraints["price_max"] = price_max

    if any(keyword in query for keyword in PRODUCT_KEYWORDS):
        return IntentResult(intent="product", constraints=constraints)
    if any(keyword in query for keyword in TCM_KEYWORDS):
        return IntentResult(intent="tcm", constraints=constraints)
    return IntentResult(intent="unknown", constraints=constraints)
