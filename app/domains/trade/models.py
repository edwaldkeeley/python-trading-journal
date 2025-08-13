from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TradeSide(str, Enum):
  buy = "buy"
  sell = "sell"


class TradeBase(BaseModel):
  symbol: str = Field(..., examples=["AAPL", "BTCUSD"], min_length=1, max_length=20)
  side: TradeSide
  quantity: float = Field(..., gt=0)
  entry_price: float = Field(..., gt=0)
  entry_time: datetime
  fees: float = Field(0, ge=0)
  notes: Optional[str] = Field(None, max_length=2000)

  @field_validator("symbol")
  @classmethod
  def normalize_symbol(cls, v: str) -> str:
    return v.upper()


class TradeCreate(TradeBase):
  exit_price: Optional[float] = Field(None, gt=0)
  exit_time: Optional[datetime] = None


class TradeUpdate(BaseModel):
  symbol: Optional[str] = Field(None, min_length=1, max_length=20)
  side: Optional[TradeSide] = None
  quantity: Optional[float] = Field(None, gt=0)
  entry_price: Optional[float] = Field(None, gt=0)
  entry_time: Optional[datetime] = None
  exit_price: Optional[float] = Field(None, gt=0)
  exit_time: Optional[datetime] = None
  fees: Optional[float] = Field(None, ge=0)
  notes: Optional[str] = Field(None, max_length=2000)

  @field_validator("symbol")
  @classmethod
  def normalize_symbol(cls, v: str) -> str:
    return v.upper()


class Trade(TradeBase):
  id: int
  created_at: datetime
  updated_at: datetime
  exit_price: Optional[float] = None
  exit_time: Optional[datetime] = None
  pnl: Optional[float] = None

  class Config:
    from_attributes = True

