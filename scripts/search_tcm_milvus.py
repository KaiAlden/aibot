import argparse
import sys

from app.services.milvus_tcm import search_tcm_milvus


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    chunks = search_tcm_milvus(args.query, top_k=args.top_k)
    for chunk in chunks:
        print(f"[{chunk.score:.4f}] {chunk.source}: {chunk.text[:200]}")


if __name__ == "__main__":
    main()
