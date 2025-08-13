from __future__ import annotations

import logging
import asyncio
from typing import Optional, AsyncIterator

import asyncpg


logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def init_db_pool(database_url: str, max_retries: int = 5, retry_delay: float = 2.0) -> None:
  """Initialize the global asyncpg connection pool with retry logic.

  Args:
    database_url: Postgres connection URL.
    max_retries: Maximum number of connection attempts.
    retry_delay: Delay between retries in seconds.
  """
  global _pool
  if _pool is not None:
    return

  for attempt in range(max_retries):
    try:
      logger.info(f"Attempting to create database pool (attempt {attempt + 1}/{max_retries})...")
      _pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=10)
      logger.info("Database pool created successfully")
      return
    except Exception as e:
      logger.warning(f"Failed to create database pool (attempt {attempt + 1}/{max_retries}): {e}")
      if attempt < max_retries - 1:
        logger.info(f"Retrying in {retry_delay} seconds...")
        await asyncio.sleep(retry_delay)
      else:
        logger.error("Failed to create database pool after all retries")
        raise


async def close_db_pool() -> None:
  """Close the global asyncpg pool."""
  global _pool
  if _pool is not None:
    await _pool.close()
    _pool = None
    logger.info("Database pool closed")


def get_pool() -> asyncpg.Pool:
  """Return the active connection pool or raise if not initialized."""
  if _pool is None:
    raise RuntimeError("Database pool is not initialized")
  return _pool


async def get_connection() -> AsyncIterator[asyncpg.Connection]:
  """FastAPI dependency to acquire/release a DB connection from the pool."""
  pool = get_pool()
  conn = await pool.acquire()
  try:
    yield conn
  finally:
    await pool.release(conn)

