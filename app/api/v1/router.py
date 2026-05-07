from fastapi import APIRouter

from app.api.v1.routes import chat, health, recommendations

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(recommendations.router, tags=["recommendations"])
api_router.include_router(chat.router, tags=["chat"])
