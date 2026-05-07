FORM_ALIASES: dict[str, set[str]] = {
    "茶饮": {"茶", "茶饮", "花茶", "袋泡茶", "养生茶"},
    "冲饮": {"粉", "冲饮", "固体饮料", "颗粒"},
    "糕点": {"糕", "糕点", "饼", "点心"},
    "膏滋": {"膏", "膏滋", "滋膏"},
    "汤包": {"汤包", "煲汤料", "汤料"},
    "丸剂": {"丸", "丸剂"},
    "零食": {"零食", "蜜饯", "糖"},
    "食材": {"食材", "干货", "药食同源"},
    "日用品": {"日用品", "洗护", "外用"},
}


def normalize_form(raw_value: str | None) -> str | None:
    if not raw_value:
        return None
    raw = raw_value.strip()
    for standard, aliases in FORM_ALIASES.items():
        if raw in aliases:
            return standard
        if any(alias in raw for alias in aliases):
            return standard
    return raw
