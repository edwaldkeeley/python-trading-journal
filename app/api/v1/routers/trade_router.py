from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Response
import asyncpg

from app.api.deps import get_connection_dependency
from app.domains.trade.models import Trade, TradeCreate, TradeUpdate
from app.domains.trade import service as trade_service


router = APIRouter()


@router.post("/", response_model=Trade, status_code=201)
async def create_trade(
  trade_in: TradeCreate,
  conn: asyncpg.Connection = get_connection_dependency(),
) -> Trade:
  trade = await trade_service.create_trade(conn, trade_in)
  return trade


@router.get("/{trade_id}", response_model=Trade)
async def get_trade(
  trade_id: int,
  conn: asyncpg.Connection = get_connection_dependency(),
) -> Trade:
  trade = await trade_service.get_trade(conn, trade_id)
  if not trade:
    raise HTTPException(status_code=404, detail="Trade not found")
  return trade


@router.get("/", response_model=List[Trade])
async def list_trades(
  symbol: Optional[str] = None,
  limit: int = Query(50, ge=1, le=500),
  offset: int = Query(0, ge=0),
  conn: asyncpg.Connection = get_connection_dependency(),
) -> list[Trade]:
  trades = await trade_service.list_trades(conn, symbol=symbol, limit=limit, offset=offset)
  return trades


@router.put("/{trade_id}", response_model=Trade)
async def update_trade(
  trade_id: int,
  trade_in: TradeUpdate,
  conn: asyncpg.Connection = get_connection_dependency(),
) -> Trade:
  trade = await trade_service.update_trade(conn, trade_id, trade_in)
  if not trade:
    raise HTTPException(status_code=404, detail="Trade not found")
  return trade


@router.delete("/{trade_id}", status_code=204)
async def delete_trade(
  trade_id: int,
  conn: asyncpg.Connection = get_connection_dependency(),
) -> Response:
  deleted = await trade_service.delete_trade(conn, trade_id)
  if not deleted:
    raise HTTPException(status_code=404, detail="Trade not found")
  return Response(status_code=204)

