import pytest

from app.services.embedding import (
    EmbeddingError,
    MissingEmbeddingConfigError,
    RemoteEmbeddingClient,
    extract_embedding_vectors,
)


def test_extract_embedding_vectors_openai_format() -> None:
    vectors = extract_embedding_vectors({"data": [{"embedding": [1, 2.5]}]})

    assert vectors == [[1.0, 2.5]]


def test_extract_embedding_vectors_rejects_bad_format() -> None:
    with pytest.raises(EmbeddingError):
        extract_embedding_vectors({"bad": []})


def test_remote_embedding_client_requires_config() -> None:
    client = RemoteEmbeddingClient(endpoint=None, api_key=None, model_name=None)

    with pytest.raises(MissingEmbeddingConfigError):
        client.embed_texts(["test"])
