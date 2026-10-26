"""Fixtures for API convention tests: an app with probe routes exercising each contract."""

import io
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine

from app.api.pagination import Page, PaginationDep, build_page
from app.core.config import Settings
from app.core.errors import AppError, ErrorCode
from app.core.observability.structured_logging import configure_logging
from app.main import create_app

TOTAL_ITEMS = 30


class Item(BaseModel):
    id: int


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: int = Field(ge=1)
    password: str | None = None


def _probe_router(secret_url: str) -> APIRouter:
    router = APIRouter(prefix="/api/v1/_probe")

    @router.get("/items")
    def items(pagination: PaginationDep) -> Page[Item]:
        first = pagination.offset + 1
        last = min(pagination.offset + pagination.limit, TOTAL_ITEMS)
        return build_page([Item(id=i) for i in range(first, last + 1)], pagination, TOTAL_ITEMS)

    @router.post("/body")
    def body(payload: Payload) -> dict[str, int]:
        return {"quantity": payload.quantity}

    @router.get("/conflict")
    def conflict() -> None:
        raise AppError(
            ErrorCode.INSUFFICIENT_STOCK,
            "Only 2 units available.",
            details=[{"field": "quantity", "available": 2}],
        )

    @router.get("/boom")
    def boom() -> None:
        raise RuntimeError("internal-detail-do-not-expose")

    @router.get("/leak")
    def leak() -> None:
        raise RuntimeError(
            f"connection failed for {secret_url} Authorization: Bearer leaked-jwt-value "
            "password=leaked-pw token=leaked-token"
        )

    return router


@dataclass
class Probe:
    app: FastAPI
    client: TestClient
    logs: io.StringIO

    def log_lines(self) -> list[dict[str, object]]:
        import json

        return [json.loads(line) for line in self.logs.getvalue().splitlines() if line]


@pytest.fixture
def probe(settings: Settings) -> Iterator[Probe]:
    app = create_app(settings, engine=create_engine("sqlite://"))
    app.include_router(_probe_router(settings.database_url.get_secret_value()))
    logs = io.StringIO()
    configure_logging(settings, stream=logs)  # re-point the JSON handler at a buffer
    # Unhandled errors must produce a 500 response, not re-raise into the test.
    yield Probe(app, TestClient(app, raise_server_exceptions=False), logs)
