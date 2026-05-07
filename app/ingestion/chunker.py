import re


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 60) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunks.append(normalized[start:end])
        if end == len(normalized):
            break
        start = end - overlap

    return chunks


def split_by_heading_or_size(text: str, chunk_size: int = 400, overlap: int = 60) -> list[str]:
    sections = re.split(r"(?m)^(第[一二三四五六七八九十百千0-9]+[章节卷].*)$", text)
    if len(sections) <= 1:
        return chunk_text(text, chunk_size=chunk_size, overlap=overlap)

    merged_sections: list[str] = []
    current_heading = ""
    for part in sections:
        if not part.strip():
            continue
        if re.match(r"^第[一二三四五六七八九十百千0-9]+[章节卷]", part.strip()):
            current_heading = part.strip()
            continue
        merged_sections.append(f"{current_heading}\n{part}".strip())

    chunks: list[str] = []
    for section in merged_sections:
        chunks.extend(chunk_text(section, chunk_size=chunk_size, overlap=overlap))
    return chunks
