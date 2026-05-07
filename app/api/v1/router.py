from fastapi import APIRouter

from app.api.v1.routes import auth, chat, health, merchant_items, recommendations

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(recommendations.router, tags=["recommendations"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(merchant_items.router, tags=["merchant-items"])
