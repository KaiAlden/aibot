import argparse

from app.db.session import SessionLocal
from app.services.milvus_tcm import upsert_translated_tcm_to_milvus
from app.utils.milvus_init import ensure_collections


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    with SessionLocal() as db:
        try:
            if not args.dry_run:
                ensure_collections()
            count = upsert_translated_tcm_to_milvus(db, limit=args.limit, dry_run=args.dry_run)
        except Exception as exc:
            raise SystemExit(
                "Milvus is unavailable. Please start Milvus and verify MILVUS_URI in .env. "
                f"Original error: {type(exc).__name__}: {exc}"
            ) from exc

    mode = "Prepared" if args.dry_run else "Upserted"
    print(f"{mode} {count} translated TCM rows for Milvus")


if __name__ == "__main__":
    main()
