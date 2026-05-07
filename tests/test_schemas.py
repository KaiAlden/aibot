from app.schemas import Constitution, SessionContext


def test_session_context_serializes_constitution() -> None:
    context = SessionContext(constitution=Constitution.qixu)

    assert context.model_dump(mode="json")["constitution"] == "气虚质"
