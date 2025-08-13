from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, computed_field, Field, field_validator


class TradeSide(str, Enum):
    """Trading side enumeration."""
    BUY = "buy"
    SELL = "sell"


class TradeBase(BaseModel):
    """Base trade model with common fields."""

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Trading symbol (e.g., AAPL, BTCUSD)",
        examples=["AAPL", "BTCUSD", "TSLA"]
    )
    side: TradeSide = Field(..., description="Trade side (buy/sell)")
    quantity: Decimal = Field(..., gt=0, description="Trade quantity")
    entry_price: Decimal = Field(..., gt=0, description="Entry price")
    entry_time: datetime = Field(..., description="Entry timestamp")
    fees: Decimal = Field(default=0, ge=0, description="Trading fees")
    notes: Optional[str] = Field(None, max_length=2000, description="Trade notes")

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        """Normalize symbol to uppercase."""
        return v.upper().strip()

    @field_validator("quantity", "entry_price", "fees")
    @classmethod
    def validate_decimal(cls, v: float | Decimal) -> Decimal:
        """Convert float to Decimal and validate."""
        if isinstance(v, float):
            return Decimal(str(v))
        return v


class TradeCreate(TradeBase):
    """Model for creating a new trade."""

    exit_price: Optional[Decimal] = Field(None, gt=0, description="Exit price")
    exit_time: Optional[datetime] = Field(None, description="Exit timestamp")

    @field_validator("exit_price")
    @classmethod
    def validate_exit_price(cls, v: Optional[float | Decimal]) -> Optional[Decimal]:
        """Validate exit price if provided."""
        if v is None:
            return None
        if isinstance(v, float):
            return Decimal(str(v))
        return v


class TradeUpdate(BaseModel):
    """Model for updating an existing trade."""

    symbol: Optional[str] = Field(None, min_length=1, max_length=20)
    side: Optional[TradeSide] = None
    quantity: Optional[Decimal] = Field(None, gt=0)
    entry_price: Optional[Decimal] = Field(None, gt=0)
    entry_time: Optional[datetime] = None
    exit_price: Optional[Decimal] = Field(None, gt=0)
    exit_time: Optional[datetime] = None
    fees: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: Optional[str]) -> Optional[str]:
        """Normalize symbol to uppercase if provided."""
        if v is None:
            return None
        return v.upper().strip()

    @field_validator("quantity", "entry_price", "exit_price", "fees")
    @classmethod
    def validate_decimal(cls, v: Optional[float | Decimal]) -> Optional[Decimal]:
        """Convert float to Decimal and validate if provided."""
        if v is None:
            return None
        if isinstance(v, float):
            return Decimal(str(v))
        return v


class Trade(TradeBase):
    """Complete trade model with computed fields."""

    id: int = Field(..., description="Unique trade identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    exit_price: Optional[Decimal] = None
    exit_time: Optional[datetime] = None
    pnl: Optional[Decimal] = Field(None, description="Profit/Loss")

    @computed_field
    @property
    def is_closed(self) -> bool:
        """Check if trade is closed."""
        return self.exit_price is not None and self.exit_time is not None

    @computed_field
    @property
    def duration(self) -> Optional[float]:
        """Calculate trade duration in seconds if closed."""
        if not self.is_closed:
            return None
        return (self.exit_time - self.entry_time).total_seconds()

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }

