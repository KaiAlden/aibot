from typing import Any, Protocol

import httpx

from app.config.settings import settings


class EmbeddingError(Exception):
    pass


class MissingEmbeddingConfigError(EmbeddingError):
    pass


class EmbeddingClient(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...


class DeterministicEmbeddingClient:
    """Development-only embedding client for tests and dry-run ingestion."""

    def __init__(self, dimension: int = 1024) -> None:
        self.dimension = dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            seed = sum(ord(char) for char in text) or 1
            vectors.append([((seed + index * 31) % 1000) / 1000 for index in range(self.dimension)])
        return vectors


class RemoteEmbeddingClient:
    """OpenAI-compatible embeddings client."""

    def __init__(
        self,
        endpoint: str | None = settings.embedding_api_endpoint,
        api_key: str | None = settings.embedding_api_key,
        model_name: str | None = settings.embedding_model_name,
        dimension: int = settings.embedding_dimension,
        timeout_seconds: float = 60,
    ) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.model_name = model_name
        self.dimension = dimension
        self.timeout_seconds = timeout_seconds

    def _validate_config(self) -> None:
        if not self.endpoint or not self.api_key or not self.model_name:
            raise MissingEmbeddingConfigError(
                "EMBEDDING_API_ENDPOINT, EMBEDDING_API_KEY and EMBEDDING_MODEL_NAME must be configured."
            )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self._validate_config()
        if not texts:
            return []

        payload = {"model": self.model_name, "input": texts}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        vectors = extract_embedding_vectors(data)
        for vector in vectors:
            if len(vector) != self.dimension:
                raise EmbeddingError(f"Expected embedding dimension {self.dimension}, got {len(vector)}")
        return vectors


def extract_embedding_vectors(data: dict[str, Any]) -> list[list[float]]:
    items = data.get("data")
    if not isinstance(items, list):
        raise EmbeddingError("Unexpected embedding response format: missing data list")

    vectors: list[list[float]] = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("embedding"), list):
            raise EmbeddingError("Unexpected embedding response format: missing embedding")
        vectors.append([float(value) for value in item["embedding"]])
    return vectors
