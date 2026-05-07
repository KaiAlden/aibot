from pathlib import Path

from pypdf import PdfReader

from app.ingestion.chunker import split_by_heading_or_size
from app.ingestion.text_loader import read_text_auto


def read_text_file(path: Path) -> str:
    return read_text_auto(path)


def read_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def load_document_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return read_text_file(path)
    if suffix == ".pdf":
        return read_pdf_text(path)
    raise ValueError(f"unsupported document type: {suffix}")


def load_document_chunks(path: Path, chunk_size: int = 400, overlap: int = 60) -> list[str]:
    return split_by_heading_or_size(load_document_text(path), chunk_size=chunk_size, overlap=overlap)
