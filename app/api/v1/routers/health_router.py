"""
Health check and system status endpoints.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
import asyncpg

from app.api.deps import get_db_connection
from app.core.config import settings
from app.core.db_init import db_initializer

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "trading-journal-api",
        "version": settings.api.version
    }


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> Dict[str, Any]:
    """Detailed health check with database connectivity."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "trading-journal-api",
        "version": settings.api.version,
        "checks": {}
    }

    # Database connectivity check
    try:
        result = await conn.fetchval("SELECT 1")

        # Get schema status
        schema_status = await db_initializer.get_schema_status()

        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": 0,  # Could add timing if needed
            "connection_test": "passed",
            "schema_status": schema_status
        }

        # If schema is not ready, mark overall status as degraded
        if not schema_status.get("schema_ready", False):
            health_status["status"] = "degraded"
            health_status["checks"]["database"]["status"] = "degraded"
            health_status["checks"]["database"]["warning"] = "Database schema not initialized"

    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "connection_test": "failed"
        }
        health_status["status"] = "unhealthy"

    # Configuration check
    try:
        health_status["checks"]["configuration"] = {
            "status": "healthy",
            "database_url_configured": bool(settings.effective_database_url),
            "migrations_enabled": settings.run_migrations_on_startup,
            "debug_mode": settings.api.debug
        }
    except Exception as e:
        health_status["checks"]["configuration"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"

    return health_status


@router.get("/health/schema", response_model=Dict[str, Any])
async def schema_status(
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> Dict[str, Any]:
    """Check database schema status."""
    try:
        schema_status = await db_initializer.get_schema_status()

        return {
            "status": "healthy" if schema_status.get("schema_ready", False) else "degraded",
            "schema_status": schema_status,
            "migration_info": {
                "migration_files": db_initializer.migration_files,
                "migration_directory": str(db_initializer.migrations_dir),
                "migrations_enabled": settings.run_migrations_on_startup
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "schema_status": {
                "trades_table_exists": False,
                "total_tables": 0,
                "trades_columns": 0,
                "schema_ready": False,
                "error": str(e)
            },
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/status", response_model=Dict[str, Any])
async def system_status() -> Dict[str, Any]:
    """System status and configuration information."""
    return {
        "api": {
            "title": settings.api.title,
            "version": settings.api.version,
            "prefix": settings.api.prefix,
            "debug": settings.api.debug
        },
        "database": {
            "host": settings.database.host,
            "port": settings.database.port,
            "name": settings.database.name,
            "user": settings.database.user,
            "url_configured": bool(settings.effective_database_url)
        },
        "application": {
            "log_level": settings.log_level,
            "migrations_on_startup": settings.run_migrations_on_startup
        },
        "timestamp": datetime.utcnow().isoformat()
    }
