import argparse

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.knowledge import TCMKnowledge
from app.services.llm_client import LLMClient, LLMError, RemoteLLMClient, build_classic_translation_messages


def fetch_untranslated_documents(limit: int | None = None) -> list[TCMKnowledge]:
    statement = select(TCMKnowledge).where(TCMKnowledge.translated_text == TCMKnowledge.original_text)
    if limit is not None:
        statement = statement.limit(limit)

    with SessionLocal() as db:
        return list(db.scalars(statement))


def translate_documents(
    limit: int | None = None,
    dry_run: bool = False,
    llm_client: LLMClient | None = None,
    continue_on_error: bool = True,
) -> int:
    llm_client = llm_client or RemoteLLMClient(timeout_seconds=120)
    translated_count = 0

    with SessionLocal() as db:
        statement = select(TCMKnowledge).where(TCMKnowledge.translated_text == TCMKnowledge.original_text)
        if limit is not None:
            statement = statement.limit(limit)
        documents = list(db.scalars(statement))

        for document in documents:
            messages = build_classic_translation_messages(document.original_text)
            if dry_run:
                print(f"[DRY-RUN] document_id={document.id} chars={len(document.original_text)}")
                continue

            try:
                document.translated_text = llm_client.chat(messages, temperature=0.2)
            except (LLMError, Exception) as exc:
                db.rollback()
                print(f"[ERROR] document_id={document.id} {type(exc).__name__}: {exc}")
                if continue_on_error:
                    continue
                raise

            translated_count += 1
            db.commit()
            print(f"[OK] document_id={document.id}")

    return translated_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    count = translate_documents(limit=args.limit, dry_run=args.dry_run, continue_on_error=not args.fail_fast)
    if args.dry_run:
        print("Dry-run completed")
    else:
        print(f"Translated {count} TCM documents")


if __name__ == "__main__":
    main()
