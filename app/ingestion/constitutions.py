import re

from app.schemas import Constitution

CONSTITUTION_KEYWORDS: dict[str, Constitution] = {
    "平和": Constitution.pinghe,
    "气虚": Constitution.qixu,
    "阳虚": Constitution.yangxu,
    "阴虚": Constitution.yinxu,
    "痰湿": Constitution.tanshi,
    "湿热": Constitution.shire,
    "血瘀": Constitution.xueyu,
    "气郁": Constitution.qiyu,
    "特禀": Constitution.tebing,
}


def extract_constitutions(value: object) -> tuple[list[str], list[str]]:
    if value is None:
        return [], []

    raw = str(value)
    normalized = re.sub(r"[✅\d\.\(\)（）/、,，;；:：\n\r\t]+", " ", raw)
    found: list[str] = []
    for keyword, constitution in CONSTITUTION_KEYWORDS.items():
        if keyword in normalized and constitution.value not in found:
            found.append(constitution.value)

    unknown: list[str] = []
    for token in normalized.split():
        token = token.strip()
        if not token:
            continue
        if any(keyword in token for keyword in CONSTITUTION_KEYWORDS):
            continue
        if "质" in token or "体质" in token or token.endswith("型"):
            unknown.append(token)

    return found, unknown
