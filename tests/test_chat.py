from app.schemas import Constitution, RecommendedProduct, SessionContext
from app.services import chat as chat_service
from app.services.chat import ChatRequest, handle_chat
from app.models.tenant import Tenant


class FakeSessionManager:
    def __init__(self) -> None:
        self.context = SessionContext()
        self.saved = None

    def get_context(self, tenant_id: int, session_id: str) -> SessionContext:
        return self.context

    def save_context(self, tenant_id: int, session_id: str, context: SessionContext) -> None:
        self.saved = context
        self.tenant_id = tenant_id


class FakeDb:
    pass


def test_handle_chat_product_recommendation(monkeypatch) -> None:
    monkeypatch.setattr(chat_service, "get_tenant_by_code", lambda db, merchant_code: Tenant(id=7, merchant_code=merchant_code, name="青春塘"))
    monkeypatch.setattr(
        chat_service,
        "recommend_products",
        lambda *args, **kwargs: [RecommendedProduct(product_id=1, name="黄芪茶", score=0.8, reason="补气")],
    )
    manager = FakeSessionManager()

    response = handle_chat(
        FakeDb(),
        ChatRequest(merchant_code="QCT001", query="我是气虚质，推荐补气茶", session_id="s1"),
        session_manager=manager,
    )

    assert response.intent == "product"
    assert response.constitution == Constitution.qixu
    assert response.recommendations[0].name == "黄芪茶"
    assert manager.saved.constitution == Constitution.qixu
    assert manager.tenant_id == 7


def test_handle_chat_product_requires_constitution(monkeypatch) -> None:
    monkeypatch.setattr(chat_service, "get_tenant_by_code", lambda db, merchant_code: Tenant(id=7, merchant_code=merchant_code, name="青春塘"))

    response = handle_chat(
        FakeDb(),
        ChatRequest(merchant_code="QCT001", query="推荐点茶", session_id="s1"),
        session_manager=FakeSessionManager(),
    )

    assert response.need_followup is True
    assert response.recommendations == []


def test_handle_chat_product_uses_symptom_match(monkeypatch) -> None:
    monkeypatch.setattr(chat_service, "get_tenant_by_code", lambda db, merchant_code: Tenant(id=7, merchant_code=merchant_code, name="青春塘"))
    monkeypatch.setattr(
        chat_service,
        "recommend_products",
        lambda *args, **kwargs: [RecommendedProduct(product_id=2, name="姜枣茶", score=0.7, reason="温阳")],
    )

    response = handle_chat(
        FakeDb(),
        ChatRequest(merchant_code="QCT001", query="我怕冷，手脚冰凉，腰膝发冷，推荐点茶", session_id="s1"),
        session_manager=FakeSessionManager(),
    )

    assert response.constitution == Constitution.yangxu
    assert response.recommendations[0].name == "姜枣茶"


def test_handle_chat_tcm_retrieval(monkeypatch) -> None:
    monkeypatch.setattr(chat_service, "get_tenant_by_code", lambda db, merchant_code: Tenant(id=7, merchant_code=merchant_code, name="青春塘"))
    monkeypatch.setattr(chat_service, "retrieve_tcm", lambda db, query, top_k=5: [])

    response = handle_chat(
        FakeDb(),
        ChatRequest(merchant_code="QCT001", query="阳虚质为什么怕冷", session_id="s1"),
        session_manager=FakeSessionManager(),
    )

    assert response.intent == "tcm"
    assert response.constitution == Constitution.yangxu
    assert "暂未" in response.message
