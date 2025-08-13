from __future__ import annotations

from typing import Optional, Sequence

import asyncpg
from pypika import Query, Table, Order

from app.domains.trade.models import Trade, TradeCreate, TradeUpdate


trades = Table("trades")


def _record_to_trade(record: asyncpg.Record) -> Trade:
  return Trade(**dict(record))


async def create(conn: asyncpg.Connection, trade_in: TradeCreate, pnl: Optional[float]) -> Trade:
  sql = (
    "INSERT INTO trades (symbol, side, quantity, entry_price, entry_time, exit_price, exit_time, fees, notes, pnl) "
    "VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) "
    "RETURNING id, symbol, side, quantity, entry_price, entry_time, exit_price, exit_time, fees, notes, pnl, created_at, updated_at"
  )
  row = await conn.fetchrow(
    sql,
    trade_in.symbol,
    trade_in.side.value,
    trade_in.quantity,
    trade_in.entry_price,
    trade_in.entry_time,
    trade_in.exit_price,
    trade_in.exit_time,
    trade_in.fees,
    trade_in.notes,
    pnl,
  )
  assert row is not None
  return _record_to_trade(row)


async def get_by_id(conn: asyncpg.Connection, trade_id: int) -> Optional[Trade]:
  q = Query.from_(trades).select(
    trades.id,
    trades.symbol,
    trades.side,
    trades.quantity,
    trades.entry_price,
    trades.entry_time,
    trades.exit_price,
    trades.exit_time,
    trades.fees,
    trades.notes,
    trades.pnl,
    trades.created_at,
    trades.updated_at,
  ).where(trades.id == trade_id)
  # Replace inline value with placeholder for safe execution
  sql = str(q).replace(str(trades.id == trade_id), "id = $1")
  row = await conn.fetchrow(sql, trade_id)
  if row is None:
    return None
  return _record_to_trade(row)


async def list(
  conn: asyncpg.Connection,
  *,
  symbol: Optional[str],
  limit: int,
  offset: int,
) -> Sequence[Trade]:
  q = Query.from_(trades).select(
    trades.id,
    trades.symbol,
    trades.side,
    trades.quantity,
    trades.entry_price,
    trades.entry_time,
    trades.exit_price,
    trades.exit_time,
    trades.fees,
    trades.notes,
    trades.pnl,
    trades.created_at,
    trades.updated_at,
  )
  params = []
  if symbol is not None:
    q = q.where(trades.symbol == symbol)
    # We'll replace equality with placeholder $1 below
  q = q.orderby(trades.entry_time, order=Order.desc).orderby(trades.id, order=Order.desc)
  base_sql = str(q)
  if symbol is not None:
    base_sql = base_sql.replace(str(trades.symbol == symbol), "symbol = $1")
    params.append(symbol)
  # Add limit/offset placeholders
  placeholder_index = len(params) + 1
  sql = f"{base_sql} LIMIT ${placeholder_index} OFFSET ${placeholder_index+1}"
  params.extend([limit, offset])
  rows = await conn.fetch(sql, *params)
  return [_record_to_trade(r) for r in rows]


async def update(
  conn: asyncpg.Connection,
  trade_id: int,
  trade_in: TradeUpdate,
  pnl: Optional[float],
) -> Optional[Trade]:
  # Build dynamic update set using provided fields
  data = trade_in.model_dump(exclude_unset=True)
  assignments = []
  params = []
  if "symbol" in data:
    assignments.append("symbol = ${}".format(len(params) + 1))
    params.append(data["symbol"])
  if "side" in data and data["side"] is not None:
    assignments.append("side = ${}".format(len(params) + 1))
    params.append(data["side"].value)
  if "quantity" in data:
    assignments.append("quantity = ${}".format(len(params) + 1))
    params.append(data["quantity"])
  if "entry_price" in data:
    assignments.append("entry_price = ${}".format(len(params) + 1))
    params.append(data["entry_price"])
  if "entry_time" in data:
    assignments.append("entry_time = ${}".format(len(params) + 1))
    params.append(data["entry_time"])
  if "exit_price" in data:
    assignments.append("exit_price = ${}".format(len(params) + 1))
    params.append(data["exit_price"])
  if "exit_time" in data:
    assignments.append("exit_time = ${}".format(len(params) + 1))
    params.append(data["exit_time"])
  if "fees" in data:
    assignments.append("fees = ${}".format(len(params) + 1))
    params.append(data["fees"])
  if "notes" in data:
    assignments.append("notes = ${}".format(len(params) + 1))
    params.append(data["notes"])
  # pnl recomputed in service
  assignments.append("pnl = ${}".format(len(params) + 1))
  params.append(pnl)

  if not assignments:
    # nothing to update, return existing
    return await get_by_id(conn, trade_id)

  sql = (
    f"UPDATE trades SET {', '.join(assignments)}, updated_at = NOW() WHERE id = ${len(params)+1} "
    "RETURNING id, symbol, side, quantity, entry_price, entry_time, exit_price, exit_time, fees, notes, pnl, created_at, updated_at"
  )
  params.append(trade_id)
  row = await conn.fetchrow(sql, *params)
  return _record_to_trade(row) if row else None


async def delete(conn: asyncpg.Connection, trade_id: int) -> bool:
  status = await conn.execute("DELETE FROM trades WHERE id = $1", trade_id)
  return status.endswith(" 1")

