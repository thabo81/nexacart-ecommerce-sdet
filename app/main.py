"""API entry point. Run: uvicorn app.main:create_app --factory"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import Engine

from app.api.health import router as health_router
from app.api.v1 import router as v1_router
from app.core.config import Settings, get_settings
from app.persistence.session import create_db_engine


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    app.state.engine.dispose()


def create_app(settings: Settings | None = None, engine: Engine | None = None) -> FastAPI:
    """Build the app. One engine per app (lazy connections), disposed on shutdown."""
    settings = settings or get_settings()
    app = FastAPI(
        title="NexaCart API",
        version="0.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs" if settings.app_env != "production" else None,
        redoc_url=None,
        lifespan=_lifespan,
    )
    app.state.settings = settings
    app.state.engine = engine or create_db_engine(settings)
    app.include_router(health_router)
    app.include_router(v1_router, prefix="/api/v1")
    return app
