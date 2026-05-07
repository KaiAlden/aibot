from pathlib import Path

from app.ingestion.constitution_parser import parse_constitution_symptom_file
from app.ingestion.constitution_seed import CONSTITUTION_SYMPTOMS
from app.services.embedding import DeterministicEmbeddingClient, EmbeddingClient
from app.utils.milvus_init import get_client


def build_symptom_rows(embedding_client: EmbeddingClient, symptom_file: Path | None = None) -> list[dict]:
    if symptom_file is None:
        items = [(item.constitution, item.symptom_text) for item in CONSTITUTION_SYMPTOMS]
    else:
        parsed = parse_constitution_symptom_file(symptom_file)
        items = list(parsed.items())

    texts = [text for _, text in items]
    vectors = embedding_client.embed_texts(texts)
    return [
        {
            "id": index + 1,
            "constitution_name": constitution.value,
            "symptom_text": text,
            "vector": vectors[index],
        }
        for index, (constitution, text) in enumerate(items)
    ]


def seed_symptoms(dry_run: bool = False, symptom_file: Path | None = None) -> list[dict]:
    rows = build_symptom_rows(DeterministicEmbeddingClient(), symptom_file=symptom_file)
    if dry_run:
        return rows

    client = get_client()
    client.upsert(collection_name="symptom_constitution", data=rows)
    return rows


if __name__ == "__main__":
    inserted = seed_symptoms()
    print(f"Seeded {len(inserted)} constitution symptom rows")
