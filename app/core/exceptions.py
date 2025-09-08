"""
Custom exceptions for the Trading Journal application.
"""

from typing import Any, Dict, Optional


class TradingJournalException(Exception):
    """Base exception for Trading Journal application."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(TradingJournalException):
    """Database-related exceptions."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details
        )


class TradeException(TradingJournalException):
    """Trade-related exceptions."""

    def __init__(self, message: str, trade_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        self.trade_id = trade_id
        trade_details = details or {}
        if trade_id:
            trade_details["trade_id"] = trade_id

        super().__init__(
            message=message,
            error_code="TRADE_ERROR",
            details=trade_details
        )


class ValidationException(TradingJournalException):
    """Data validation exceptions."""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.field = field
        validation_details = details or {}
        if field:
            validation_details["field"] = field

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=validation_details
        )


class ConfigurationException(TradingJournalException):
    """Configuration-related exceptions."""

    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.config_key = config_key
        config_details = details or {}
        if config_key:
            config_details["config_key"] = config_key

        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=config_details
        )


class MigrationException(TradingJournalException):
    """Database migration exceptions."""

    def __init__(self, message: str, migration_file: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.migration_file = migration_file
        migration_details = details or {}
        if migration_file:
            migration_details["migration_file"] = migration_file

        super().__init__(
            message=message,
            error_code="MIGRATION_ERROR",
            details=migration_details
        )

