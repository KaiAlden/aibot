from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.schemas import Constitution, RecommendedProduct
from app.repositories.tenants import get_tenant_by_code
from app.services.constitution_precheck import precheck_constitution
from app.services.intent import classify_intent
from app.services.recommendation import recommend_products
from app.services.recommendation import MerchantNotFoundError
from app.services.session_manager import SessionManager
from app.services.symptom_matcher import match_constitution
from app.services.tcm_retrieval import build_tcm_answer, retrieve_tcm


class ChatRequest(BaseModel):
    merchant_code: str
    query: str
    session_id: str


class ChatResponse(BaseModel):
    intent: str
    constitution: Constitution | None = None
    message: str
    recommendations: list[RecommendedProduct] = Field(default_factory=list)
    need_followup: bool = False


def handle_chat(
    db: Session,
    request: ChatRequest,
    session_manager: SessionManager | None = None,
) -> ChatResponse:
    session_manager = session_manager or SessionManager()
    tenant = get_tenant_by_code(db, request.merchant_code)
    if tenant is None:
        raise MerchantNotFoundError(f"invalid merchant_code: {request.merchant_code}")
    tenant_id = tenant.id
    context = session_manager.get_context(tenant_id, request.session_id)

    constitution = precheck_constitution(request.query, context)
    intent = classify_intent(request.query)

    symptom_result = None
    if constitution is None:
        symptom_result = match_constitution(request.query)
        if symptom_result.constitution is not None and not symptom_result.need_followup:
            constitution = symptom_result.constitution

    if constitution is not None and context.constitution != constitution:
        context.constitution = constitution

    if intent.intent == "product":
        if constitution is None:
            context.chat_history.append({"role": "user", "content": request.query})
            session_manager.save_context(tenant_id, request.session_id, context)
            return ChatResponse(
                intent="product",
                message=(
                    symptom_result.followup_question
                    if symptom_result and symptom_result.followup_question
                    else "请先告诉我您的体质，或描述怕冷、乏力、口干等主要感受，我再帮您推荐合适商品。"
                ),
                need_followup=True,
            )

        recommendations = recommend_products(
            db,
            merchant_code=request.merchant_code,
            constitution=constitution,
            query=request.query,
            form=intent.constraints.get("form"),
            price_max=intent.constraints.get("price_max"),
            top_n=5,
        )
        context.chat_history.append({"role": "user", "content": request.query})
        context.chat_history.append(
            {
                "role": "assistant",
                "content": f"为{constitution.value}推荐了{len(recommendations)}个商品。",
            }
        )
        session_manager.save_context(tenant_id, request.session_id, context)
        return ChatResponse(
            intent="product",
            constitution=constitution,
            message=f"根据您的{constitution.value}，为您推荐以下商品。",
            recommendations=recommendations,
        )

    if intent.intent == "tcm":
        chunks = retrieve_tcm(db, request.query, top_k=5)
        answer = build_tcm_answer(request.query, chunks)
        context.chat_history.append({"role": "user", "content": request.query})
        context.chat_history.append({"role": "assistant", "content": answer})
        session_manager.save_context(tenant_id, request.session_id, context)
        return ChatResponse(
            intent="tcm",
            constitution=constitution,
            message=answer,
        )

    context.chat_history.append({"role": "user", "content": request.query})
    session_manager.save_context(tenant_id, request.session_id, context)
    return ChatResponse(
        intent="unknown",
        constitution=constitution,
        message="我还需要更多信息：您是想了解中医调理知识，还是想让我推荐适合的商品？",
        need_followup=True,
    )
