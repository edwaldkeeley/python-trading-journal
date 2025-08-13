from __future__ import annotations

import os
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  """Application settings loaded from environment variables and .env file."""

  app_name: str = "Trading Journal API"
  version: str = "1.0.0"
  debug: bool = True
  log_level: str = "INFO"

  api_v1_prefix: str = "/api/v1"

  # Database connection info
  database_url: str | None = None
  postgres_host: str = "db"  # Changed from localhost to match docker-compose service name
  postgres_port: int = 5432
  postgres_db: str = "app_db"  # Changed from trading_journal to match docker-compose
  postgres_user: str = "postgres"
  postgres_password: str = "password"  # Changed from postgres to match docker-compose

  # Migrations
  run_migrations_on_startup: bool = True

  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
    case_sensitive=False,
  )

  @computed_field  # type: ignore[misc]
  @property
  def effective_database_url(self) -> str:
    """Compute the effective Postgres URL for asyncpg (no +asyncpg prefix)."""
    if self.database_url:
      if self.database_url.startswith("postgresql+asyncpg://"):
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
      return self.database_url
    host = os.getenv("POSTGRES_HOST", self.postgres_host)
    port = int(os.getenv("POSTGRES_PORT", str(self.postgres_port)))
    db = os.getenv("POSTGRES_DB", self.postgres_db)
    user = os.getenv("POSTGRES_USER", self.postgres_user)
    password = os.getenv("POSTGRES_PASSWORD", self.postgres_password)
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


settings = Settings()

