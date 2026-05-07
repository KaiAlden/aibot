import argparse
from pathlib import Path

from app.ingestion.constitution_parser import parse_constitution_symptom_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    parsed = parse_constitution_symptom_file(Path(args.path))
    for constitution, text in parsed.items():
        print(f"{constitution.value}: {len(text)} chars")


if __name__ == "__main__":
    main()
