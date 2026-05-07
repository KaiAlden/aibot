from app.config.settings import settings
from app.schemas.core import SessionContext
from app.services.redis_client import RedisClient


class SessionManager:
    def __init__(self, redis_client: RedisClient | None = None) -> None:
        self.redis = redis_client or RedisClient()
        self._memory_contexts: dict[str, dict] = {}

    @staticmethod
    def session_key(tenant_id: int, session_id: str) -> str:
        return f"session:{tenant_id}:{session_id}"

    @staticmethod
    def constitution_key(tenant_id: int, session_id: str) -> str:
        return f"constitution:{tenant_id}:{session_id}"

    def get_context(self, tenant_id: int, session_id: str) -> SessionContext:
        key = self.session_key(tenant_id, session_id)
        try:
            data = self.redis.get_json(key)
        except Exception:
            data = self._memory_contexts.get(key)
        return SessionContext.model_validate(data) if data else SessionContext()

    def save_context(self, tenant_id: int, session_id: str, context: SessionContext) -> None:
        trimmed = self.trim_context(context)
        key = self.session_key(tenant_id, session_id)
        data = trimmed.model_dump(mode="json")
        try:
            self.redis.set_json(key, data, ttl_seconds=settings.session_ttl_seconds)
        except Exception:
            self._memory_contexts[key] = data

    def trim_context(self, context: SessionContext) -> SessionContext:
        max_messages = max(1, settings.context_max_tokens // 256)
        if len(context.chat_history) <= max_messages:
            return context
        context.chat_history = context.chat_history[-max_messages:]
        return context
