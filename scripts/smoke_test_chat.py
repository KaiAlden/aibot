import sys

from app.db.session import SessionLocal
from app.schemas import SessionContext
from app.services.chat import ChatRequest, handle_chat


class MemorySessionManager:
    def __init__(self) -> None:
        self.contexts: dict[tuple[int, str], SessionContext] = {}

    def get_context(self, tenant_id: int, session_id: str) -> SessionContext:
        return self.contexts.get((tenant_id, session_id), SessionContext())

    def save_context(self, tenant_id: int, session_id: str, context: SessionContext) -> None:
        self.contexts[(tenant_id, session_id)] = context


def print_response(title: str, response) -> None:
    print(f"\n=== {title} ===")
    print(f"intent: {response.intent}")
    print(f"constitution: {response.constitution.value if response.constitution else None}")
    print(f"need_followup: {response.need_followup}")
    print(f"message: {response.message}")
    if response.recommendations:
        print("recommendations:")
        for item in response.recommendations:
            print(f"- {item.product_id} {item.name} score={item.score} reason={item.reason}")


def run_smoke_tests() -> None:
    session_manager = MemorySessionManager()
    with SessionLocal() as db:
        cases = [
            (
                "商品推荐：显式体质",
                ChatRequest(
                    merchant_code="QCT001",
                    query="我是气虚质，想喝补气茶",
                    session_id="smoke_explicit",
                ),
            ),
            (
                "商品推荐：症状识别体质",
                ChatRequest(
                    merchant_code="QCT001",
                    query="我最近怕冷，手脚冰凉，腰膝发冷，推荐点茶",
                    session_id="smoke_symptom",
                ),
            ),
            (
                "中医问答：无命中兜底",
                ChatRequest(
                    merchant_code="QCT001",
                    query="阳虚质为什么怕冷",
                    session_id="smoke_tcm",
                ),
            ),
            (
                "中医问答：命中方药后合规兜底",
                ChatRequest(
                    merchant_code="QCT001",
                    query="白带",
                    session_id="smoke_tcm_compliance",
                ),
            ),
            (
                "多轮会话：第一轮记录体质",
                ChatRequest(
                    merchant_code="QCT001",
                    query="我是气虚质",
                    session_id="smoke_multi",
                ),
            ),
            (
                "多轮会话：第二轮复用体质推荐",
                ChatRequest(
                    merchant_code="QCT001",
                    query="推荐点茶",
                    session_id="smoke_multi",
                ),
            ),
        ]

        for title, request in cases:
            response = handle_chat(db, request, session_manager=session_manager)
            print_response(title, response)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    run_smoke_tests()
