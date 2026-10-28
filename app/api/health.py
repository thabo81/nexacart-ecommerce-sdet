"""Public, minimal health endpoints (FR-103, AC-067). Unversioned, as specified by the PRD."""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import Engine

from app.core.observability.health import database_is_reachable

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", summary="Liveness: the API process is responding")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/ready",
    summary="Readiness: PostgreSQL is reachable",
    responses={503: {"description": "NOT_READY: a required dependency is unavailable"}},
)
def ready(request: Request) -> Any:
    engine: Engine = request.app.state.engine
    if database_is_reachable(engine):
        return {"status": "ready"}
    # PRD error envelope. request_id is populated once FOUND-003 adds request-ID middleware.
    return JSONResponse(
        status_code=503,
        headers={"Cache-Control": "no-store"},
        content={
            "error": {
                "code": "NOT_READY",
                "message": "The service is not ready.",
                "details": [],
                "request_id": None,
            }
        },
    )
