import re

SENSITIVE_PATTERNS = [
    r"用水煎服",
    r"水煎服",
    r"服用[一二三四五六七八九十\d]+剂",
    r"再服用",
    r"煎汤",
    r"冲服",
    r"临服",
    r"方剂使用",
    r"配方[:：]",
    r"用药",
]

SAFE_MEDICAL_FALLBACK = "该问题涉及具体诊疗或方药服用建议，建议咨询专业中医师。"


def contains_medical_advice(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in SENSITIVE_PATTERNS)


def filter_medical_advice(text: str) -> str:
    if contains_medical_advice(text):
        return SAFE_MEDICAL_FALLBACK
    return text
