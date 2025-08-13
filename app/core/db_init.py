from __future__ import annotations

import logging
from pathlib import Path

from app.core.db import get_pool


logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Handles database initialization and migrations."""

    def __init__(self):
        self.migrations_dir = Path(__file__).resolve().parent.parent / "migrations"
        self.migration_files = [
            "001_create_trade.sql",
        ]

    async def run_migrations(self) -> None:
        """Run database migrations on startup."""
        try:
            pool = get_pool()
            async with pool.acquire() as conn:
                for migration_file in self.migration_files:
                    await self._apply_migration(conn, migration_file)

            logger.info("All migrations applied successfully")

        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            raise

    async def _apply_migration(self, conn, migration_file: str) -> None:
        """Apply a single migration file."""
        migration_path = self.migrations_dir / migration_file

        if not migration_path.exists():
            logger.warning(f"Migration file missing: {migration_file}")
            return

        try:
            sql = migration_path.read_text(encoding="utf-8")
            logger.info(f"Applying migration: {migration_file}")
            await conn.execute(sql)
            logger.info(f"Migration {migration_file} applied successfully")

        except Exception as e:
            logger.error(f"Failed to apply migration {migration_file}: {e}")
            raise

    async def init_schema(self) -> None:
        """Initialize database schema (alias for run_migrations)."""
        await self.run_migrations()


# Global instance
db_initializer = DatabaseInitializer()


# Convenience function for backward compatibility
async def run_startup_migrations() -> None:
    """Run startup migrations (legacy function)."""
    await db_initializer.run_migrations()


async def init_db_schema() -> None:
    """Initialize database schema (legacy function)."""
    await db_initializer.init_schema()

