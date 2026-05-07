from pymilvus import DataType, MilvusClient

from app.config.settings import settings

VECTOR_DIM = 1024


def get_client() -> MilvusClient:
    return MilvusClient(
        uri=settings.milvus_uri,
        token=settings.milvus_token or "",
        timeout=settings.milvus_timeout_seconds,
    )


def _create_tcm_knowledge(client: MilvusClient) -> None:
    schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=True)
    schema.add_field("id", DataType.INT64, is_primary=True)
    schema.add_field("source", DataType.VARCHAR, max_length=255)
    schema.add_field("original_text", DataType.VARCHAR, max_length=8192)
    schema.add_field("translated_text", DataType.VARCHAR, max_length=8192)
    schema.add_field("document_type", DataType.VARCHAR, max_length=64)
    schema.add_field("tags", DataType.VARCHAR, max_length=512)
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=VECTOR_DIM)

    index_params = client.prepare_index_params()
    index_params.add_index("vector", index_type="IVF_FLAT", metric_type="COSINE", params={"nlist": 1024})
    client.create_collection(
        "tcm_knowledge",
        schema=schema,
        index_params=index_params,
        timeout=settings.milvus_timeout_seconds,
    )


def _create_symptom_constitution(client: MilvusClient) -> None:
    schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=True)
    schema.add_field("id", DataType.INT64, is_primary=True)
    schema.add_field("constitution_name", DataType.VARCHAR, max_length=16)
    schema.add_field("symptom_text", DataType.VARCHAR, max_length=4096)
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=VECTOR_DIM)

    index_params = client.prepare_index_params()
    index_params.add_index(
        "vector",
        index_type="HNSW",
        metric_type="COSINE",
        params={"M": 16, "efConstruction": 200},
    )
    client.create_collection(
        "symptom_constitution",
        schema=schema,
        index_params=index_params,
        timeout=settings.milvus_timeout_seconds,
    )


def ensure_collections(client: MilvusClient | None = None) -> None:
    client = client or get_client()
    if not client.has_collection("tcm_knowledge", timeout=settings.milvus_timeout_seconds):
        _create_tcm_knowledge(client)
    if not client.has_collection("symptom_constitution", timeout=settings.milvus_timeout_seconds):
        _create_symptom_constitution(client)


if __name__ == "__main__":
    ensure_collections()
