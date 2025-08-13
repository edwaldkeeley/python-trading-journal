from __future__ import annotations

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

from app.domains.trade.models import Trade

# Generic type for response data
T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response model."""

    success: bool = Field(True, description="Operation success status")
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Success message")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""

    items: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class TradeResponse(Trade):
    """Trade response model with additional computed fields."""

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 100.0,
                "entry_price": 150.50,
                "entry_time": "2024-01-15T10:30:00Z",
                "exit_price": 155.75,
                "exit_time": "2024-01-16T14:45:00Z",
                "fees": 1.50,
                "notes": "Long position in Apple",
                "pnl": 475.00,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-16T14:45:00Z"
            }
        }


class TradeCreateResponse(BaseModel):
    """Response model for trade creation."""

    trade: TradeResponse = Field(..., description="Created trade")
    message: str = Field(default="Trade created successfully", description="Success message")


class TradeUpdateResponse(BaseModel):
    """Response model for trade updates."""

    trade: TradeResponse = Field(..., description="Updated trade")
    message: str = Field(default="Trade updated successfully", description="Success message")


class TradeListResponse(BaseModel):
    """Response model for trade listing."""

    trades: list[TradeResponse] = Field(..., description="List of trades")
    pagination: dict = Field(..., description="Pagination information")
    filters: dict = Field(..., description="Applied filters")
