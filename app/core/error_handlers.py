"""
Error handling utilities and HTTP exception handlers.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    TradingJournalException,
    DatabaseException,
    TradeException,
    ValidationException,
    ConfigurationException,
    MigrationException
)

logger = logging.getLogger(__name__)


def create_error_response(
    message: str,
    error_code: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized error response."""
    error_data = {
        "error": {
            "message": message,
            "code": error_code,
            "status_code": status_code,
            "details": details or {}
        },
        "success": False,
        "timestamp": None  # Will be set by middleware
    }

    return JSONResponse(
        status_code=status_code,
        content=error_data
    )


async def trading_journal_exception_handler(request: Request, exc: TradingJournalException) -> JSONResponse:
    """Handle TradingJournalException instances."""
    logger.error(f"TradingJournalException: {exc.message}", extra={
        "error_code": exc.error_code,
        "details": exc.details,
        "path": str(request.url),
        "method": request.method
    })

    # Map error codes to HTTP status codes
    status_mapping = {
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "TRADE_ERROR": status.HTTP_400_BAD_REQUEST,
        "DATABASE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "CONFIGURATION_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "MIGRATION_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    status_code = status_mapping.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    return create_error_response(
        message=exc.message,
        error_code=exc.error_code,
        status_code=status_code,
        details=exc.details
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException instances."""
    logger.warning(f"HTTPException: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": str(request.url),
        "method": request.method
    })

    return create_error_response(
        message=str(exc.detail),
        error_code="HTTP_ERROR",
        status_code=exc.status_code
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", extra={
        "exception_type": type(exc).__name__,
        "path": str(request.url),
        "method": request.method
    }, exc_info=True)

    return create_error_response(
        message="An unexpected error occurred. Please try again later.",
        error_code="INTERNAL_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"exception_type": type(exc).__name__}
    )


def validate_trade_data(data: Dict[str, Any]) -> None:
    """Validate trade data and raise ValidationException if invalid."""
    required_fields = ["symbol", "side", "quantity", "entry_price", "stop_loss", "take_profit"]

    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValidationException(
                message=f"Missing required field: {field}",
                field=field
            )

    # Validate numeric fields
    numeric_fields = ["quantity", "entry_price", "stop_loss", "take_profit", "fees"]
    for field in numeric_fields:
        if field in data and data[field] is not None:
            try:
                float(data[field])
            except (ValueError, TypeError):
                raise ValidationException(
                    message=f"Invalid numeric value for field: {field}",
                    field=field
                )

    # Validate side
    if data.get("side") not in ["buy", "sell"]:
        raise ValidationException(
            message="Invalid trade side. Must be 'buy' or 'sell'",
            field="side"
        )

    # Validate price relationships
    entry_price = float(data["entry_price"])
    stop_loss = float(data["stop_loss"])
    take_profit = float(data["take_profit"])

    if data["side"] == "buy":
        if stop_loss >= entry_price:
            raise ValidationException(
                message="For buy trades, stop loss must be below entry price",
                field="stop_loss"
            )
        if take_profit <= entry_price:
            raise ValidationException(
                message="For buy trades, take profit must be above entry price",
                field="take_profit"
            )
    else:  # sell
        if stop_loss <= entry_price:
            raise ValidationException(
                message="For sell trades, stop loss must be above entry price",
                field="stop_loss"
            )
        if take_profit >= entry_price:
            raise ValidationException(
                message="For sell trades, take profit must be below entry price",
                field="take_profit"
            )

