"""Fixtures for API convention tests: an app with probe routes exercising each contract."""

import io
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx
import pytest
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine

from app.api.pagination import Page, PaginationDep, build_page
from app.core.config import Settings
from app.core.errors import ERROR_STATUS, AppError, ErrorCode, ErrorEnvelope
from app.core.observability.structured_logging import configure_logging
from app.main import create_app

TOTAL_ITEMS = 30
PROBE = "/api/v1/_probe"

# Deliberately seeded dummy secrets: none of these may reach a response body or a log line.
SEEDED_SECRETS = {
    "password": "seed-password-A1",
    "token": "seed-token-B2",
    "access_token": "seed-access-C3",
    "refresh_token": "seed-refresh-D4",
    "client_secret": "seed-clientsecret-E5",
    "bearer": "seed-bearer-F6",
    "cookie": "seed-cookie-G7",
    "csrf": "seed-csrf-H8",
    "query_token": "seed-querytoken-I9",
    "jwt": "eyJhbGciOiJIUzI1NiJ9.eyJzZWVkIjoiSiJ9.seed-jwt-J10",
    "db_password": "seed-dbpass-K11",
}
DB_URL_WITH_SEEDED_PASSWORD = (
    f"postgresql+psycopg://nexacart:{SEEDED_SECRETS['db_password']}@db:5432/nexacart"
)


def assert_envelope(response: httpx.Response, status: int, code: ErrorCode) -> dict[str, Any]:
    """Check status AND code together, the envelope shape, and header/body request-ID equality."""
    assert response.status_code == status, f"expected {status}, got {response.status_code}"
    error: dict[str, Any] = response.json()["error"]
    assert set(error) == {"code", "message", "details", "request_id"}
    assert error["code"] == code.value, f"expected {code.value}, got {error['code']}"
    assert ERROR_STATUS[code] == status, "test expectation contradicts the catalogue"
    assert error["request_id"] == response.headers["x-request-id"]
    return error


class Item(BaseModel):
    id: int


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: int = Field(ge=1)
    password: str | None = None


def _error(*codes: int) -> dict[int | str, dict[str, Any]]:
    return {code: {"model": ErrorEnvelope} for code in codes}


def _leak() -> None:
    secrets = SEEDED_SECRETS
    try:
        raise ConnectionError(f"could not connect using {DB_URL_WITH_SEEDED_PASSWORD}")
    except ConnectionError as cause:
        raise RuntimeError(
            f"upstream call failed: GET /api/v1/x?token={secrets['query_token']}&page=2 "
            f"password={secrets['password']} token={secrets['token']} "
            f"access_token={secrets['access_token']} refresh_token={secrets['refresh_token']} "
            f"client_secret={secrets['client_secret']} "
            f"Authorization: Bearer {secrets['bearer']} "
            f"Cookie: sid={secrets['cookie']}; csrf_token={secrets['csrf']} "
            f"jwt {secrets['jwt']} "
            f"body={{'password': '{secrets['password']}'}}"
        ) from cause


def _probe_router() -> APIRouter:
    router = APIRouter(prefix=PROBE)

    @router.get("/items")
    def items(pagination: PaginationDep) -> Page[Item]:
        first = pagination.offset + 1
        last = min(pagination.offset + pagination.limit, TOTAL_ITEMS)
        return build_page([Item(id=i) for i in range(first, last + 1)], pagination, TOTAL_ITEMS)

    @router.get("/items/{item_id}", responses=_error(404))
    def item(item_id: int) -> Item:
        if item_id > TOTAL_ITEMS:
            raise AppError(ErrorCode.NOT_FOUND, "Item not found.")
        return Item(id=item_id)

    @router.post("/body")
    def body(payload: Payload) -> dict[str, int]:
        return {"quantity": payload.quantity}

    @router.get("/conflict", responses=_error(409))
    def conflict() -> None:
        raise AppError(
            ErrorCode.INSUFFICIENT_STOCK,
            "Only 2 units available.",
            details=[{"field": "quantity", "available": 2}],
        )

    @router.get("/app-error/{code}")
    def app_error(code: str) -> None:
        raise AppError(ErrorCode(code), "Probe error.")

    @router.get("/status/{code}")
    def status(code: int) -> None:
        raise HTTPException(status_code=code, headers={"X-Probe": "kept"})

    @router.get("/boom")
    def boom() -> None:
        raise RuntimeError("internal-detail-do-not-expose")

    @router.get("/bad-response", response_model=Item)
    def bad_response() -> Any:
        return {"id": "not-an-integer"}

    @router.get("/leak")
    def leak() -> None:
        _leak()

    return router


@dataclass
class Probe:
    app: FastAPI
    client: TestClient
    logs: io.StringIO

    def log_lines(self) -> list[dict[str, Any]]:
        return [json.loads(line) for line in self.logs.getvalue().splitlines() if line]


ProbeFactory = Callable[..., Probe]


@pytest.fixture
def probe_factory(settings_factory: Callable[..., Settings]) -> ProbeFactory:
    """Create a probe app; keyword overrides are applied to Settings (e.g. page_size_max=20)."""

    def make(**overrides: Any) -> Probe:
        settings = settings_factory(**overrides)
        app = create_app(settings, engine=create_engine("sqlite://"))
        app.include_router(_probe_router())
        logs = io.StringIO()
        configure_logging(settings, stream=logs)  # re-point the JSON handler at a buffer
        # Unhandled errors must produce a 500 response, not re-raise into the test.
        return Probe(app, TestClient(app, raise_server_exceptions=False), logs)

    return make


@pytest.fixture
def probe(probe_factory: ProbeFactory) -> Probe:
    return probe_factory()
