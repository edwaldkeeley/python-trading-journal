from __future__ import annotations

from decimal import Decimal
from typing import Optional, Sequence

import asyncpg
from pypika import Order, Query, Table

from app.domains.trade.models import Trade, TradeCreate, TradeUpdate


# Table definition
trades = Table("trades")


def _record_to_trade(record: asyncpg.Record) -> Trade:
    """Convert database record to Trade model."""
    data = dict(record)
    # Convert Decimal fields back to Decimal for Pydantic
    for field in ["quantity", "entry_price", "exit_price", "fees", "pnl"]:
        if field in data and data[field] is not None:
            data[field] = Decimal(str(data[field]))
    return Trade(**data)


class TradeRepository:
    """Repository for trade operations."""

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def create(self, trade_in: TradeCreate, pnl: Optional[Decimal]) -> Trade:
        """Create a new trade."""
        sql = """
            INSERT INTO trades (
                symbol, side, quantity, entry_price, entry_time,
                exit_price, exit_time, fees, notes, pnl
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id, symbol, side, quantity, entry_price, entry_time,
                      exit_price, exit_time, fees, notes, pnl, created_at, updated_at
        """

        row = await self.conn.fetchrow(
            sql,
            trade_in.symbol,
            trade_in.side.value,
            float(trade_in.quantity),
            float(trade_in.entry_price),
            trade_in.entry_time,
            float(trade_in.exit_price) if trade_in.exit_price else None,
            trade_in.exit_time,
            float(trade_in.fees),
            trade_in.notes,
            float(pnl) if pnl else None,
        )

        if not row:
            raise RuntimeError("Failed to create trade")

        return _record_to_trade(row)

    async def get_by_id(self, trade_id: int) -> Optional[Trade]:
        """Get trade by ID."""
        sql = """
            SELECT id, symbol, side, quantity, entry_price, entry_time,
                   exit_price, exit_time, fees, notes, pnl, created_at, updated_at
            FROM trades WHERE id = $1
        """

        row = await self.conn.fetchrow(sql, trade_id)
        return _record_to_trade(row) if row else None

    async def list(
        self,
        *,
        symbol: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        side: Optional[str] = None,
    ) -> Sequence[Trade]:
        """List trades with optional filtering."""
        # Build base query
        query = Query.from_(trades).select(
            trades.id, trades.symbol, trades.side, trades.quantity,
            trades.entry_price, trades.entry_time, trades.exit_price,
            trades.exit_time, trades.fees, trades.notes, trades.pnl,
            trades.created_at, trades.updated_at
        )

        # Apply filters
        params = []
        param_count = 1

        if symbol:
            query = query.where(trades.symbol == f"${param_count}")
            params.append(symbol.upper())
            param_count += 1

        if side:
            query = query.where(trades.side == f"${param_count}")
            params.append(side)
            param_count += 1

        # Apply ordering and pagination
        query = query.orderby(trades.entry_time, order=Order.desc)
        query = query.orderby(trades.id, order=Order.desc)

        sql = str(query)

        # Replace PyPika placeholders with PostgreSQL placeholders
        for i in range(len(params)):
            sql = sql.replace(f"${i+1}", f"${i+1}")

        # Add limit and offset
        sql += f" LIMIT ${param_count} OFFSET ${param_count + 1}"
        params.extend([limit, offset])

        rows = await self.conn.fetch(sql, *params)
        return [_record_to_trade(row) for row in rows]

    async def update(
        self,
        trade_id: int,
        trade_in: TradeUpdate,
        pnl: Optional[Decimal],
    ) -> Optional[Trade]:
        """Update an existing trade."""
        # Get current trade to check if it exists
        current_trade = await self.get_by_id(trade_id)
        if not current_trade:
            return None

        # Build dynamic update query
        update_fields = []
        params = []
        param_count = 1

        # Map model fields to database columns
        field_mapping = {
            "symbol": "symbol",
            "side": "side",
            "quantity": "quantity",
            "entry_price": "entry_price",
            "entry_time": "entry_time",
            "exit_price": "exit_price",
            "exit_time": "exit_time",
            "fees": "fees",
            "notes": "notes",
        }

        for field, column in field_mapping.items():
            if hasattr(trade_in, field) and getattr(trade_in, field) is not None:
                value = getattr(trade_in, field)
                if field == "side":
                    value = value.value
                elif field in ["quantity", "entry_price", "exit_price", "fees"]:
                    value = float(value)

                update_fields.append(f"{column} = ${param_count}")
                params.append(value)
                param_count += 1

        # Always update PnL and updated_at
        update_fields.append(f"pnl = ${param_count}")
        params.append(float(pnl) if pnl else None)
        param_count += 1

        update_fields.append("updated_at = NOW()")

        if not update_fields:
            return current_trade  # Nothing to update

        # Build and execute update query
        sql = f"""
            UPDATE trades
            SET {', '.join(update_fields)}
            WHERE id = ${param_count}
            RETURNING id, symbol, side, quantity, entry_price, entry_time,
                      exit_price, exit_time, fees, notes, pnl, created_at, updated_at
        """
        params.append(trade_id)

        row = await self.conn.fetchrow(sql, *params)
        return _record_to_trade(row) if row else None

    async def delete(self, trade_id: int) -> bool:
        """Delete a trade by ID."""
        result = await self.conn.execute(
            "DELETE FROM trades WHERE id = $1",
            trade_id
        )
        return result.endswith(" 1")


# Convenience functions for backward compatibility
async def create(conn: asyncpg.Connection, trade_in: TradeCreate, pnl: Optional[Decimal]) -> Trade:
    """Create a new trade (legacy function)."""
    repo = TradeRepository(conn)
    return await repo.create(trade_in, pnl)


async def get_by_id(conn: asyncpg.Connection, trade_id: int) -> Optional[Trade]:
    """Get trade by ID (legacy function)."""
    repo = TradeRepository(conn)
    return await repo.get_by_id(trade_id)


async def list(
    conn: asyncpg.Connection,
    *,
    symbol: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Trade]:
    """List trades (legacy function)."""
    repo = TradeRepository(conn)
    return await repo.list(symbol=symbol, limit=limit, offset=offset)


async def update(
    conn: asyncpg.Connection,
    trade_id: int,
    trade_in: TradeUpdate,
    pnl: Optional[Decimal],
) -> Optional[Trade]:
    """Update a trade (legacy function)."""
    repo = TradeRepository(conn)
    return await repo.update(trade_id, trade_in, pnl)


async def delete(conn: asyncpg.Connection, trade_id: int) -> bool:
    """Delete a trade (legacy function)."""
    repo = TradeRepository(conn)
    return await repo.delete(trade_id)