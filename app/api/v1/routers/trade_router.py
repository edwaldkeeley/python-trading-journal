from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Query, Response, status
import asyncpg

from app.api.deps import get_connection_dependency
from app.api.models import (
    TradeResponse,
    TradeCreateResponse,
    TradeUpdateResponse,
    TradeListResponse,
    ErrorResponse
)
from app.domains.trade.models import TradeCreate, TradeUpdate
from app.domains.trade import service as trade_service


router = APIRouter()


@router.post(
    "/",
    response_model=TradeCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trade",
    description="Create a new trading entry with required details",
    responses={
        201: {"description": "Trade created successfully", "model": TradeCreateResponse},
        400: {"description": "Bad request", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def create_trade(
    trade_in: TradeCreate,
    conn: asyncpg.Connection = get_connection_dependency(),
) -> TradeCreateResponse:
    """Create a new trade entry."""
    try:
        trade = await trade_service.create_trade(conn, trade_in)
        return TradeCreateResponse(trade=TradeResponse.model_validate(trade))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trade: {str(e)}"
        )


@router.get(
    "/{trade_id}",
    response_model=TradeResponse,
    summary="Get trade by ID",
    description="Retrieve a specific trade by its unique identifier",
    responses={
        200: {"description": "Trade retrieved successfully", "model": TradeResponse},
        404: {"description": "Trade not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_trade(
    trade_id: int,
    conn: asyncpg.Connection = get_connection_dependency(),
) -> TradeResponse:
    """Get a specific trade by ID."""
    trade = await trade_service.get_trade(conn, trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade with ID {trade_id} not found"
        )
    return TradeResponse.model_validate(trade)


@router.get(
    "/",
    response_model=TradeListResponse,
    summary="List trades",
    description="Retrieve a paginated list of trades with optional filtering",
    responses={
        200: {"description": "Trades retrieved successfully", "model": TradeListResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def list_trades(
    symbol: str = Query(None, description="Filter by trading symbol"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of trades to return"),
    offset: int = Query(0, ge=0, description="Number of trades to skip"),
    conn: asyncpg.Connection = get_connection_dependency(),
) -> TradeListResponse:
    """List trades with optional filtering and pagination."""
    try:
        trades = await trade_service.list_trades(
            conn,
            symbol=symbol,
            limit=limit,
            offset=offset
        )

        # Calculate pagination info
        total = len(trades)  # In a real app, you'd get this from the database
        page = (offset // limit) + 1
        pages = (total + limit - 1) // limit

        return TradeListResponse(
            trades=[TradeResponse.model_validate(trade) for trade in trades],
            pagination={
                "total": total,
                "page": page,
                "size": limit,
                "pages": pages
            },
            filters={
                "symbol": symbol,
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trades: {str(e)}"
        )


@router.put(
    "/{trade_id}",
    response_model=TradeUpdateResponse,
    summary="Update trade",
    description="Update an existing trade with new information",
    responses={
        200: {"description": "Trade updated successfully", "model": TradeUpdateResponse},
        404: {"description": "Trade not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def update_trade(
    trade_id: int,
    trade_in: TradeUpdate,
    conn: asyncpg.Connection = get_connection_dependency(),
) -> TradeUpdateResponse:
    """Update an existing trade."""
    try:
        trade = await trade_service.update_trade(conn, trade_id, trade_in)
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trade with ID {trade_id} not found"
            )
        return TradeUpdateResponse(trade=TradeResponse.model_validate(trade))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update trade: {str(e)}"
        )


@router.delete(
    "/{trade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete trade",
    description="Permanently remove a trade from the system"
)
async def delete_trade(
    trade_id: int,
    conn: asyncpg.Connection = get_connection_dependency(),
) -> Response:
    """Delete a trade by ID."""
    try:
        deleted = await trade_service.delete_trade(conn, trade_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trade with ID {trade_id} not found"
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete trade: {str(e)}"
        )

