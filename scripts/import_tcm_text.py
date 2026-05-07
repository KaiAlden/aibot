import argparse
from pathlib import Path

from app.db.session import SessionLocal
from app.ingestion.tcm_documents import load_document_chunks
from app.models.knowledge import TCMKnowledge


def import_tcm_text(path: Path, source: str | None = None, document_type: str = "classic") -> int:
    chunks = load_document_chunks(path)
    source_name = source or path.stem

    with SessionLocal() as db:
        for chunk in chunks:
            db.add(
                TCMKnowledge(
                    source=source_name,
                    original_text=chunk,
                    translated_text=chunk,
                    document_type=document_type,
                    tags=path.name,
                )
            )
        db.commit()

    return len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--source")
    parser.add_argument("--document-type", default="classic")
    args = parser.parse_args()

    count = import_tcm_text(Path(args.path), source=args.source, document_type=args.document_type)
    print(f"Imported {count} TCM chunks from {args.path}")


if __name__ == "__main__":
    main()
