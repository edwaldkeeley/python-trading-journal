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
    lot_size: Decimal = Field(default=1, gt=0, description="Lot size multiplier (e.g., 100 for standard lots)")
    entry_price: Decimal = Field(..., gt=0, description="Entry price")
    entry_time: datetime = Field(..., description="Entry timestamp")
    stop_loss: Decimal = Field(..., gt=0, description="Stop loss price for risk management")
    take_profit: Decimal = Field(..., gt=0, description="Take profit target price")
    fees: Decimal = Field(default=0, ge=0, description="Trading fees")
    notes: Optional[str] = Field(None, max_length=2000, description="Trade notes")
    checklist_grade: Optional[str] = Field(None, max_length=3, description="Trade quality grade (A+, A, B+, B, C+, C, D+, D, F)")
    checklist_score: Optional[int] = Field(None, ge=0, le=100, description="Trade quality score (0-100)")

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        """Normalize symbol to uppercase."""
        return v.upper().strip()

    @field_validator("quantity", "lot_size", "entry_price", "stop_loss", "take_profit", "fees")
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
    lot_size: Optional[Decimal] = Field(None, gt=0)
    entry_price: Optional[Decimal] = Field(None, gt=0)
    entry_time: Optional[datetime] = None
    stop_loss: Optional[Decimal] = Field(None, gt=0)
    take_profit: Optional[Decimal] = Field(None, gt=0)
    exit_price: Optional[Decimal] = Field(None, gt=0)
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = Field(None, description="Reason for trade exit (manual, take_profit, stop_loss)")
    fees: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)
    pnl: Optional[Decimal] = Field(None, description="Profit/Loss")
    checklist_grade: Optional[str] = Field(None, max_length=3, description="Trade quality grade (A+, A, B+, B, C+, C, D+, D, F)")
    checklist_score: Optional[int] = Field(None, ge=0, le=100, description="Trade quality score (0-100)")

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: Optional[str]) -> Optional[str]:
        """Normalize symbol to uppercase if provided."""
        if v is None:
            return None
        return v.upper().strip()

    @field_validator("lot_size")
    @classmethod
    def validate_lot_size(cls, v: Optional[float | Decimal]) -> Optional[Decimal]:
        """Validate lot size is within reasonable limits."""
        if v is None:
            return None
        if isinstance(v, float):
            v = Decimal(str(v))
        if v <= 0:
            raise ValueError("Lot size must be greater than 0")
        if v > 100:
            raise ValueError("Lot size cannot exceed 100")
        return v

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
    exit_reason: Optional[str] = Field(None, description="Reason for trade exit (manual, take_profit, stop_loss)")
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

