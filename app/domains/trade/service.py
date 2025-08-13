from __future__ import annotations

from typing import Optional, Sequence

from app.domains.trade.models import Trade, TradeCreate, TradeUpdate, TradeSide
from app.domains.trade import repository


def _compute_pnl(
  *,
  side: TradeSide,
  quantity: float,
  entry_price: float,
  exit_price: Optional[float],
  fees: float,
) -> Optional[float]:
  if exit_price is None:
    return None
  if side == TradeSide.buy:
    gross = (exit_price - entry_price) * quantity
  else:
    gross = (entry_price - exit_price) * quantity
  return gross - fees


import asyncpg


async def create_trade(conn: asyncpg.Connection, trade_in: TradeCreate) -> Trade:
  pnl = _compute_pnl(
    side=trade_in.side,
    quantity=trade_in.quantity,
    entry_price=trade_in.entry_price,
    exit_price=trade_in.exit_price,
    fees=trade_in.fees,
  )
  return await repository.create(conn, trade_in, pnl)


async def get_trade(conn: asyncpg.Connection, trade_id: int) -> Optional[Trade]:
  return await repository.get_by_id(conn, trade_id)


async def list_trades(
  conn: asyncpg.Connection,
  *,
  symbol: Optional[str],
  limit: int,
  offset: int,
) -> Sequence[Trade]:
  symbol_norm = symbol.upper() if symbol else None
  return await repository.list(conn, symbol=symbol_norm, limit=limit, offset=offset)


async def update_trade(
  conn: asyncpg.Connection,
  trade_id: int,
  trade_in: TradeUpdate,
) -> Optional[Trade]:
  # We need existing trade to fill missing fields for pnl calc
  existing = await repository.get_by_id(conn, trade_id)
  if existing is None:
    return None

  side_eff = trade_in.side or existing.side
  entry_price_eff = trade_in.entry_price if trade_in.entry_price is not None else existing.entry_price
  quantity_eff = trade_in.quantity if trade_in.quantity is not None else existing.quantity
  exit_price_eff = trade_in.exit_price if trade_in.exit_price is not None else existing.exit_price
  fees_eff = trade_in.fees if trade_in.fees is not None else existing.fees

  pnl = _compute_pnl(
    side=side_eff,
    quantity=quantity_eff,
    entry_price=entry_price_eff,
    exit_price=exit_price_eff,
    fees=fees_eff,
  )

  return await repository.update(conn, trade_id, trade_in, pnl)


async def delete_trade(conn: asyncpg.Connection, trade_id: int) -> bool:
  return await repository.delete(conn, trade_id)

