"""Public, minimal health endpoints (FR-103, AC-067). Unversioned, as specified by the PRD."""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sqlalchemy import Engine

from app.core.errors import AppError, ErrorCode, ErrorEnvelope
from app.core.observability.health import database_is_reachable

router = APIRouter(prefix="/health", tags=["health"])


class LiveResponse(BaseModel):
    status: str = "ok"


class ReadyResponse(BaseModel):
    status: str = "ready"


@router.get("/live", summary="Liveness: the API process is responding")
def live() -> LiveResponse:
    return LiveResponse()


@router.get(
    "/ready",
    summary="Readiness: PostgreSQL is reachable",
    responses={503: {"model": ErrorEnvelope, "description": "NOT_READY: a dependency is down"}},
)
def ready(request: Request) -> ReadyResponse:
    engine: Engine = request.app.state.engine
    if not database_is_reachable(engine):
        raise AppError(
            ErrorCode.NOT_READY,
            "The service is not ready.",
            headers={"Cache-Control": "no-store"},
        )
    return ReadyResponse()
