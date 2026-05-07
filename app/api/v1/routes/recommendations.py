from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import Constitution, RecommendedProduct
from app.services.recommendation import MerchantNotFoundError, recommend_products

router = APIRouter(prefix="/recommendations")


class RecommendationRequest(BaseModel):
    merchant_code: str
    constitution: Constitution
    query: str
    form: str | None = None
    price_max: float | None = None
    top_n: int = 5


class RecommendationResponse(BaseModel):
    items: list[RecommendedProduct]


@router.post("", response_model=RecommendationResponse)
def create_recommendation(request: RecommendationRequest, db: Session = Depends(get_db)) -> RecommendationResponse:
    try:
        items = recommend_products(
            db,
            merchant_code=request.merchant_code,
            constitution=request.constitution,
            query=request.query,
            form=request.form,
            price_max=request.price_max,
            top_n=request.top_n,
        )
    except MerchantNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RecommendationResponse(items=items)
