from __future__ import annotations

from decimal import Decimal
from typing import Optional, Sequence

import asyncpg

from app.domains.trade.repository import TradeRepository
from app.domains.trade.models import Trade, TradeCreate, TradeUpdate
from app.core.exceptions import TradeException, DatabaseException, ValidationException
from app.core.error_handlers import validate_trade_data


def _compute_pnl(
    *,
    side: str,
    quantity: Decimal,
    lot_size: Decimal,
    entry_price: Decimal,
    exit_price: Optional[Decimal],
    fees: Decimal,
) -> Optional[Decimal]:
    if exit_price is None:
        return None
    if side == "buy":
        gross = (exit_price - entry_price) * quantity * lot_size
    else:
        gross = (entry_price - exit_price) * quantity * lot_size
    return gross - fees


async def create_trade(conn: asyncpg.Connection, trade_in: TradeCreate) -> Trade:
    """Create a new trade with validation and error handling."""
    try:
        # Validate trade data
        trade_data = trade_in.model_dump()
        validate_trade_data(trade_data)

        pnl = _compute_pnl(
            side=trade_in.side.value,
            quantity=trade_in.quantity,
            lot_size=trade_in.lot_size,
            entry_price=trade_in.entry_price,
            exit_price=trade_in.exit_price,
            fees=trade_in.fees,
        )

        repo = TradeRepository(conn)
        trade = await repo.create(trade_in, pnl)
        return trade

    except ValidationException:
        raise  # Re-raise validation errors
    except Exception as e:
        raise TradeException(
            message=f"Failed to create trade: {str(e)}",
            details={"operation": "create_trade", "error": str(e)}
        )


async def get_trade(conn: asyncpg.Connection, trade_id: int) -> Optional[Trade]:
    """Get a trade by ID with error handling."""
    try:
        if trade_id <= 0:
            raise ValidationException(
                message="Trade ID must be a positive integer",
                field="trade_id"
            )

        repo = TradeRepository(conn)
        trade = await repo.get_by_id(trade_id)
        return trade

    except ValidationException:
        raise  # Re-raise validation errors
    except Exception as e:
        raise TradeException(
            message=f"Failed to retrieve trade: {str(e)}",
            trade_id=trade_id,
            details={"operation": "get_trade", "error": str(e)}
        )


async def list_trades(
    conn: asyncpg.Connection,
    *,
    symbol: Optional[str],
    limit: int,
    offset: int,
) -> Sequence[Trade]:
    symbol_norm = symbol.upper() if symbol else None
    repo = TradeRepository(conn)
    return await repo.list(symbol=symbol_norm, limit=limit, offset=offset)


async def count_trades(
    conn: asyncpg.Connection,
    *,
    symbol: Optional[str],
) -> int:
    symbol_norm = symbol.upper() if symbol else None
    repo = TradeRepository(conn)
    return await repo.count(symbol=symbol_norm)


async def clear_all_trades(conn: asyncpg.Connection) -> None:
    """Clear all trades from the database."""
    try:
        repo = TradeRepository(conn)
        await repo.clear_all()
    except Exception as e:
        raise TradeException(
            message=f"Failed to clear all trades: {str(e)}",
            details={"operation": "clear_all_trades", "error": str(e)}
        )


async def update_trade(
    conn: asyncpg.Connection,
    trade_id: int,
    trade_in: TradeUpdate,
) -> Optional[Trade]:
    # We need existing trade to fill missing fields for pnl calc
    repo = TradeRepository(conn)
    existing = await repo.get_by_id(trade_id)
    if existing is None:
        return None

    side_eff = trade_in.side or existing.side
    entry_price_eff = trade_in.entry_price if trade_in.entry_price is not None else existing.entry_price
    quantity_eff = trade_in.quantity if trade_in.quantity is not None else existing.quantity
    lot_size_eff = trade_in.lot_size if trade_in.lot_size is not None else existing.lot_size
    exit_price_eff = trade_in.exit_price if trade_in.exit_price is not None else existing.exit_price
    fees_eff = trade_in.fees if trade_in.fees is not None else existing.fees

    # Use the P&L provided by the frontend if available, otherwise calculate it
    if trade_in.pnl is not None:
        pnl = trade_in.pnl
    else:
        pnl = _compute_pnl(
            side=side_eff.value if side_eff else existing.side.value,
            quantity=quantity_eff,
            lot_size=lot_size_eff,
            entry_price=entry_price_eff,
            exit_price=exit_price_eff,
            fees=fees_eff,
        )

    return await repo.update(trade_id, trade_in, pnl)


async def delete_trade(conn: asyncpg.Connection, trade_id: int) -> bool:
    repo = TradeRepository(conn)
    return await repo.delete(trade_id)

