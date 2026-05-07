from pathlib import Path

from app.ingestion.constitution_parser import parse_constitution_symptom_file
from app.schemas import Constitution


def test_parse_constitution_symptom_file() -> None:
    path = Path("tests/runtime_constitutions.txt")
    path.write_text(
        "平和体质\n总体特征：精力充沛。\n气虚体质\n总体特征：疲乏气短。",
        encoding="utf-8",
    )
    try:
        parsed = parse_constitution_symptom_file(path)
        assert parsed[Constitution.pinghe].startswith("平和体质")
        assert "疲乏" in parsed[Constitution.qixu]
    finally:
        path.unlink(missing_ok=True)
