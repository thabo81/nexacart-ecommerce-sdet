"""API entry point. Run: uvicorn app.main:create_app --factory"""

from fastapi import FastAPI

from app.api.v1 import router as v1_router
from app.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(
        title="NexaCart API",
        version="0.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs" if settings.app_env != "production" else None,
        redoc_url=None,
    )
    app.state.settings = settings
    app.include_router(v1_router, prefix="/api/v1")
    return app
