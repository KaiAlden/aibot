from typing import Any

from pymilvus import MilvusClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge import TCMKnowledge
from app.schemas import TCMChunk
from app.config.settings import settings
from app.services.embedding import EmbeddingClient, RemoteEmbeddingClient
from app.utils.milvus_init import get_client

TCM_COLLECTION = "tcm_knowledge"


def build_tcm_milvus_rows(
    documents: list[TCMKnowledge],
    embedding_client: EmbeddingClient | None = None,
) -> list[dict[str, Any]]:
    embedding_client = embedding_client or RemoteEmbeddingClient()
    texts = [document.translated_text for document in documents]
    vectors = embedding_client.embed_texts(texts)

    return [
        {
            "id": document.id,
            "source": document.source,
            "original_text": document.original_text[:8192],
            "translated_text": document.translated_text[:8192],
            "document_type": document.document_type or "",
            "tags": document.tags or "",
            "vector": vectors[index],
        }
        for index, document in enumerate(documents)
    ]


def fetch_translated_documents(db: Session, limit: int | None = None) -> list[TCMKnowledge]:
    statement = select(TCMKnowledge).where(TCMKnowledge.translated_text != TCMKnowledge.original_text)
    if limit is not None:
        statement = statement.limit(limit)
    return list(db.scalars(statement))


def upsert_translated_tcm_to_milvus(
    db: Session,
    limit: int | None = None,
    client: MilvusClient | None = None,
    embedding_client: EmbeddingClient | None = None,
    dry_run: bool = False,
) -> int:
    documents = fetch_translated_documents(db, limit=limit)
    rows = build_tcm_milvus_rows(documents, embedding_client=embedding_client)
    if dry_run:
        return len(rows)

    client = client or get_client()
    if rows:
        client.upsert(collection_name=TCM_COLLECTION, data=rows, timeout=settings.milvus_timeout_seconds)
    return len(rows)


def search_tcm_milvus(
    query: str,
    top_k: int = 5,
    client: MilvusClient | None = None,
    embedding_client: EmbeddingClient | None = None,
) -> list[TCMChunk]:
    embedding_client = embedding_client or RemoteEmbeddingClient()
    client = client or get_client()
    vector = embedding_client.embed_texts([query])[0]
    results = client.search(
        collection_name=TCM_COLLECTION,
        data=[vector],
        limit=top_k,
        output_fields=["translated_text", "source"],
        timeout=settings.milvus_timeout_seconds,
    )

    chunks: list[TCMChunk] = []
    for hit in results[0] if results else []:
        entity = hit.get("entity", {})
        chunks.append(
            TCMChunk(
                text=entity.get("translated_text", ""),
                source=entity.get("source", ""),
                score=float(hit.get("distance", 0.0)),
            )
        )
    return chunks
