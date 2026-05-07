from app.ingestion.chunker import chunk_text, split_by_heading_or_size


def test_chunk_text_uses_overlap() -> None:
    chunks = chunk_text("abcdefghij", chunk_size=6, overlap=2)

    assert chunks == ["abcdef", "efghij"]


def test_split_by_heading_or_size_keeps_heading() -> None:
    chunks = split_by_heading_or_size("第一章 总论\n气虚者，少气懒言。", chunk_size=20, overlap=2)

    assert chunks[0].startswith("第一章")
