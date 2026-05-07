from app.schemas import Constitution, SessionContext
from app.services.constitution_precheck import precheck_constitution


def test_precheck_prefers_query_constitution() -> None:
    context = SessionContext(constitution=Constitution.qixu)

    assert precheck_constitution("我是阳虚质，想喝茶", context) == Constitution.yangxu


def test_precheck_uses_context_when_query_has_no_constitution() -> None:
    context = SessionContext(constitution=Constitution.qixu)

    assert precheck_constitution("适合喝什么", context) == Constitution.qixu
