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
                    "002_add_stop_loss_take_profit.sql",
        "003_add_exit_reason.sql",
        "004_add_checklist_fields.sql",
        "005_add_lot_size.sql",
        ]

    async def run_migrations(self) -> None:
        """Run database migrations on startup."""
        try:
            logger.info(f"📁 Migration directory: {self.migrations_dir}")
            logger.info(f"📋 Migration files to apply: {self.migration_files}")

            # Check if migration directory exists
            if not self.migrations_dir.exists():
                logger.warning(f"⚠️ Migration directory does not exist: {self.migrations_dir}")
                logger.warning("   No migrations will be applied")
                return

            # Check if there are any migration files
            if not self.migration_files:
                logger.info("📋 No migration files configured")
                logger.info("   Skipping migration process")
                return

            pool = get_pool()
            async with pool.acquire() as conn:
                logger.info("🔗 Database connection acquired for migrations")

                applied_count = 0
                skipped_count = 0

                for migration_file in self.migration_files:
                    result = await self._apply_migration(conn, migration_file)
                    if result == "applied":
                        applied_count += 1
                    elif result == "skipped":
                        skipped_count += 1

            if applied_count > 0:
                logger.info(f"✅ Applied {applied_count} migrations successfully")
            if skipped_count > 0:
                logger.info(f"⏭️ Skipped {skipped_count} migrations (files missing)")
            if applied_count == 0 and skipped_count == 0:
                logger.info("✅ No migrations to apply")

        except Exception as e:
            logger.error(f"❌ Failed to run migrations: {e}")
            logger.error(f"Migration error type: {type(e)}")
            raise

    async def _apply_migration(self, conn, migration_file: str) -> str:
        """Apply a single migration file. Returns 'applied', 'skipped', or raises exception."""
        migration_path = self.migrations_dir / migration_file

        if not migration_path.exists():
            logger.warning(f"⚠️ Migration file missing: {migration_file}")
            logger.warning(f"   Expected path: {migration_path}")
            return "skipped"

        try:
            sql = migration_path.read_text(encoding="utf-8")

            # Skip empty migration files
            if not sql.strip():
                logger.warning(f"⚠️ Migration file is empty: {migration_file}")
                return "skipped"

            logger.info(f"🔄 Applying migration: {migration_file}")
            logger.debug(f"   SQL content length: {len(sql)} characters")

            await conn.execute(sql)
            logger.info(f"✅ Migration {migration_file} applied successfully")
            return "applied"

        except Exception as e:
            logger.error(f"❌ Failed to apply migration {migration_file}: {e}")
            logger.error(f"   Migration path: {migration_path}")
            logger.error(f"   Error type: {type(e)}")
            raise

    async def init_schema(self) -> None:
        """Initialize database schema (alias for run_migrations)."""
        await self.run_migrations()

    async def check_schema_exists(self) -> bool:
        """Check if the main application schema exists."""
        try:
            pool = get_pool()
            async with pool.acquire() as conn:
                # Check if the trades table exists
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'trades'
                    )
                """)
                return bool(result)
        except Exception as e:
            logger.error(f"❌ Failed to check schema existence: {e}")
            return False

    async def get_schema_status(self) -> dict:
        """Get detailed schema status information."""
        try:
            pool = get_pool()
            async with pool.acquire() as conn:
                # Check if trades table exists
                trades_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'trades'
                    )
                """)

                # Get table count
                table_count = await conn.fetchval("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)

                # Get trades table column count
                column_count = 0
                if trades_exists:
                    column_count = await conn.fetchval("""
                        SELECT COUNT(*)
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                        AND table_name = 'trades'
                    """)

                return {
                    "trades_table_exists": bool(trades_exists),
                    "total_tables": table_count or 0,
                    "trades_columns": column_count or 0,
                    "schema_ready": bool(trades_exists)
                }
        except Exception as e:
            logger.error(f"❌ Failed to get schema status: {e}")
            return {
                "trades_table_exists": False,
                "total_tables": 0,
                "trades_columns": 0,
                "schema_ready": False,
                "error": str(e)
            }


# Global instance
db_initializer = DatabaseInitializer()



