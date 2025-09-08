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

    @field_validator("run_migrations_on_startup")
    @classmethod
    def validate_run_migrations(cls, v: bool) -> bool:
        """Validate run migrations setting."""
        return bool(v)


# Global settings instance
settings = Settings()


def print_config_summary() -> None:
    """Print a summary of current configuration for debugging."""
    import os

    print("=== Configuration Summary ===")
    print(f"Environment file (.env) exists: {os.path.exists('.env')}")
    print(f"Current working directory: {os.getcwd()}")
    print()
    print("Database Configuration:")
    print(f"  Host: {settings.database.host}")
    print(f"  Port: {settings.database.port}")
    print(f"  Name: {settings.database.name}")
    print(f"  User: {settings.database.user}")
    print(f"  Password: {'*' * len(settings.database.password)}")
    print(f"  URL: {settings.effective_database_url}")
    print()
    print("API Configuration:")
    print(f"  Title: {settings.api.title}")
    print(f"  Version: {settings.api.version}")
    print(f"  Prefix: {settings.api.prefix}")
    print(f"  Debug: {settings.api.debug}")
    print()
    print("Application Configuration:")
    print(f"  Log Level: {settings.log_level}")
    print(f"  Run Migrations: {settings.run_migrations_on_startup}")
    print("=============================")


def debug_env_variables() -> None:
    """Debug function to show all relevant environment variables."""
    import os

    print("=== Environment Variables Debug ===")
    env_vars = [
        'DATABASE__HOST', 'DATABASE__PORT', 'DATABASE__NAME',
        'DATABASE__USER', 'DATABASE__PASSWORD', 'DATABASE_URL',
        'API__TITLE', 'API__VERSION', 'API__PREFIX', 'API__DEBUG',
        'LOG_LEVEL', 'RUN_MIGRATIONS_ON_STARTUP'
    ]

    for var in env_vars:
        value = os.getenv(var, 'NOT SET')
        if 'PASSWORD' in var and value != 'NOT SET':
            value = '*' * len(value)
        print(f"{var}: {value}")

    print("\n=== .env File Contents ===")
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            # Mask passwords in output
            lines = content.split('\n')
            for line in lines:
                if 'PASSWORD' in line and '=' in line:
                    key, value = line.split('=', 1)
                    print(f"{key}=***")
                else:
                    print(line)
    else:
        print(".env file not found!")
    print("================================")


if __name__ == "__main__":
    # Allow running this file directly to test configuration
    print_config_summary()
    print()
    debug_env_variables()

