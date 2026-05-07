from app.schemas import Constitution, SessionContext
from app.services.session_manager import SessionManager


class BrokenRedis:
    def get_json(self, key: str):
        raise ConnectionError("redis down")

    def set_json(self, key: str, value: dict, ttl_seconds: int | None = None) -> None:
        raise ConnectionError("redis down")


def test_session_manager_falls_back_to_memory_when_redis_down() -> None:
    manager = SessionManager(redis_client=BrokenRedis())
    context = SessionContext(constitution=Constitution.qixu)

    manager.save_context(1, "s1", context)

    assert manager.get_context(1, "s1").constitution == Constitution.qixu
