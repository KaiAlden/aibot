import re
from pathlib import Path

from app.ingestion.text_loader import read_text_auto
from app.schemas import Constitution

NAME_MAP = {
    "平和体质": Constitution.pinghe,
    "气虚体质": Constitution.qixu,
    "阳虚体质": Constitution.yangxu,
    "阴虚体质": Constitution.yinxu,
    "痰湿体质": Constitution.tanshi,
    "湿热体质": Constitution.shire,
    "血瘀体质": Constitution.xueyu,
    "气郁体质": Constitution.qiyu,
    "特禀体质": Constitution.tebing,
}


def parse_constitution_symptom_file(path: Path) -> dict[Constitution, str]:
    text = read_text_auto(path)
    pattern = re.compile(r"(平和体质|气虚体质|阳虚体质|阴虚体质|痰湿体质|湿热体质|血瘀体质|气郁体质|特禀体质)")
    matches = list(pattern.finditer(text))
    parsed: dict[Constitution, str] = {}

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        parsed[NAME_MAP[match.group(1)]] = section

    return parsed
