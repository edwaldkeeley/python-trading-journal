from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.v1.api_v1 import api_router
from app.core.config import settings
from app.core.db import init_db_pool, close_db_pool
from app.core.db_init import db_initializer
from app.core.logger import configure_logging
from app.core.exceptions import TradingJournalException
from app.core.error_handlers import (
    trading_journal_exception_handler,
    http_exception_handler,
    general_exception_handler
)

# Configure logging first
configure_logging(level=settings.log_level)
logger = logging.getLogger(__name__)


async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    try:
        logger.info("=== Trading Journal API Startup ===")
        logger.info("Starting up application...")

        # Debug: Log configuration details
        logger.info("Configuration loaded:")
        logger.info(f"  API Title: {settings.api.title}")
        logger.info(f"  API Version: {settings.api.version}")
        logger.info(f"  API Prefix: {settings.api.prefix}")
        logger.info(f"  Debug Mode: {settings.api.debug}")
        logger.info(f"  Log Level: {settings.log_level}")
        logger.info(f"  Run Migrations: {settings.run_migrations_on_startup}")

        logger.info("Database configuration:")
        logger.info(f"  Host: {settings.database.host}")
        logger.info(f"  Port: {settings.database.port}")
        logger.info(f"  Name: {settings.database.name}")
        logger.info(f"  User: {settings.database.user}")
        logger.info(f"  Database URL: {settings.effective_database_url}")

        # Initialize database pool
        logger.info("Initializing database connection pool...")
        await init_db_pool(settings.effective_database_url)
        logger.info("✅ Database pool initialized successfully")

        # Run migrations if enabled
        if settings.run_migrations_on_startup:
            logger.info("🔄 Running startup migrations...")
            await db_initializer.run_migrations()
            logger.info("✅ Startup migrations completed")
        else:
            logger.info("⏭️ Skipping migrations (disabled in config)")

        logger.info("✅ Application startup completed successfully")
        logger.info("=== Ready to serve requests ===")

    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception details: {str(e)}")
        # Don't raise here - let the app start but log the error
        # This prevents uvicorn from exiting immediately

    yield

    # Shutdown
    try:
        logger.info("Shutting down application...")
        await close_db_pool()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.api.title,
    version=settings.api.version,
    debug=settings.api.debug,
    lifespan=lifespan
)

# Add exception handlers
app.add_exception_handler(TradingJournalException, trading_journal_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include API router
try:
    app.include_router(api_router, prefix=settings.api.prefix)
    logger.info("API router included successfully")
except Exception as e:
    logger.error(f"Failed to include API router: {e}")
    # Don't fail here - let the app start without the router

