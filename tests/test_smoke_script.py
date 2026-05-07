from scripts.smoke_test_chat import MemorySessionManager
from app.schemas import Constitution, SessionContext


def test_memory_session_manager_roundtrip() -> None:
    manager = MemorySessionManager()
    context = SessionContext(constitution=Constitution.qixu)

    manager.save_context(7, "s1", context)

    assert manager.get_context(7, "s1").constitution == Constitution.qixu
