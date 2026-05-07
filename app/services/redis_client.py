import json
from typing import Any

from redis import Redis

from app.config.settings import settings


class RedisClient:
    def __init__(self, redis_url: str = settings.redis_url) -> None:
        self._client = Redis.from_url(redis_url, decode_responses=True)

    def get_json(self, key: str) -> dict[str, Any] | None:
        raw = self._client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> None:
        self._client.set(key, json.dumps(value, ensure_ascii=False), ex=ttl_seconds)

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def hget_float(self, key: str, field: str, default: float = 0.0) -> float:
        value = self._client.hget(key, field)
        if value is None:
            return default
        return float(value)
