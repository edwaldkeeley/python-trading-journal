from fastapi import FastAPI

from app.api.v1.api_v1 import api_router
from app.core.config import settings
from app.core.db import init_db_pool
from app.core.db_init import run_startup_migrations
from app.core.logger import configure_logging


async def lifespan(app: FastAPI):
    # Startup
    await init_db_pool(settings.effective_database_url)
    await run_startup_migrations()
    yield
    # Shutdown


# Configure logging
configure_logging(level=settings.log_level)

app = FastAPI(
    title=settings.api.title,
    version=settings.api.version,
    debug=settings.api.debug,
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.api.prefix)
