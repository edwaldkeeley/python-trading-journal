from fastapi import APIRouter

from app.api.v1.routers.trade_router import router as trade_router


api_router = APIRouter()
api_router.include_router(trade_router, prefix="/trades", tags=["trades"])

