from __future__ import annotations

from typing import Optional

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database-specific configuration."""

    host: str = Field(default="db", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    name: str = Field(default="app_db", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: str = Field(default="password", description="Database password")

    @computed_field
    @property
    def url(self) -> str:
        """Build database connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class APISettings(BaseSettings):
    """API-specific configuration."""

    title: str = Field(default="Trading Journal API", description="API title")
    version: str = Field(default="1.0.0", description="API version")
    prefix: str = Field(default="/api/v1", description="API prefix")
    debug: bool = Field(default=True, description="Debug mode")


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # API settings
    api: APISettings = Field(default_factory=APISettings)

    # Database settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # Override database URL if provided directly
    database_url: Optional[str] = Field(default=None, description="Direct database URL override")

    # Application settings
    log_level: str = Field(default="INFO", description="Logging level")
    run_migrations_on_startup: bool = Field(default=True, description="Run migrations on startup")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    @computed_field
    @property
    def effective_database_url(self) -> str:
        """Get the effective database URL, preferring direct override."""
        if self.database_url:
            # Remove asyncpg prefix if present
            if self.database_url.startswith("postgresql+asyncpg://"):
                return self.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
            return self.database_url

        return self.database.url

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {', '.join(valid_levels)}")
        return v.upper()


# Global settings instance
settings = Settings()

