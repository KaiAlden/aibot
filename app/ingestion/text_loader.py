from pathlib import Path


def read_text_auto(path: Path) -> str:
    data = path.read_bytes()
    last_error: Exception | None = None
    for encoding in ("utf-8", "gb18030", "gbk", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise UnicodeDecodeError("unknown", data, 0, len(data), str(last_error))
