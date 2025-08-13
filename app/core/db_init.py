from __future__ import annotations

import logging
from pathlib import Path

from app.core.db import get_pool


logger = logging.getLogger(__name__)


MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


async def run_startup_migrations() -> None:
  """Run basic SQL migrations on startup (idempotent)."""
  sql_files = [
    MIGRATIONS_DIR / "001_create_trade.sql",
  ]
  pool = get_pool()
  async with pool.acquire() as conn:  # type: ignore[attr-defined]
    for sql_path in sql_files:
      if not sql_path.exists():
        logger.warning("Migration file missing: %s", sql_path)
        continue
      sql = sql_path.read_text(encoding="utf-8")
      logger.info("Applying migration %s", sql_path.name)
      await conn.execute(sql)
  logger.info("Migrations applied")

