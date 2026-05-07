from pathlib import Path

from app.ingestion.text_loader import read_text_auto


def test_read_text_auto_supports_gb18030() -> None:
    path = Path("tests/runtime_gb18030_classic.txt")
    path.write_bytes("傅青主女科".encode("gb18030"))
    try:
        assert read_text_auto(path) == "傅青主女科"
    finally:
        path.unlink(missing_ok=True)
