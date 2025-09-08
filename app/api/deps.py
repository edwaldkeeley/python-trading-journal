from __future__ import annotations

from typing import AsyncIterator

import asyncpg

from app.core.db import get_connection


async def get_db_connection() -> AsyncIterator[asyncpg.Connection]:
    """FastAPI dependency to acquire/release a DB connection from the pool."""
    async for conn in get_connection():
        yield conn


