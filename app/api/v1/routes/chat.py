from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.chat import ChatRequest, ChatResponse, handle_chat
from app.services.recommendation import MerchantNotFoundError

router = APIRouter(prefix="/chat")


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    try:
        return handle_chat(db, request)
    except MerchantNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
