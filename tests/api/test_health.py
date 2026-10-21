"""FR-103 / AC-067: liveness answers while the process runs; readiness needs the database."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app import main as main_module
from app.core.config import Settings
from app.main import create_app


def test_liveness_is_200_even_when_database_is_unreachable(unreachable_settings: Settings) -> None:
    client = TestClient(create_app(unreachable_settings))
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_is_503_not_ready_when_database_is_unreachable(
    unreachable_settings: Settings,
) -> None:
    client = TestClient(create_app(unreachable_settings))
    response = client.get("/health/ready")
    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "NOT_READY"
    assert set(error) == {"code", "message", "details", "request_id"}
    assert response.headers["cache-control"] == "no-store"


def test_readiness_failure_does_not_leak_connection_details(
    unreachable_settings: Settings,
) -> None:
    body = TestClient(create_app(unreachable_settings)).get("/health/ready").text
    for secret in ("placeholder", "127.0.0.1", "postgresql", "psycopg"):
        assert secret not in body


def test_readiness_is_200_when_database_answers(settings: Settings) -> None:
    app = create_app(settings, engine=create_engine("sqlite://"))
    response = TestClient(app).get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_one_engine_is_created_and_reused_across_requests(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    created: list[Any] = []

    def fake_create(_settings: Settings) -> Any:
        created.append(create_engine("sqlite://"))
        return created[-1]

    monkeypatch.setattr(main_module, "create_db_engine", fake_create)
    client = TestClient(create_app(settings))
    for _ in range(3):
        assert client.get("/health/ready").status_code == 200
    assert len(created) == 1


def test_health_routes_are_documented_in_openapi(settings: Settings) -> None:
    paths = TestClient(create_app(settings)).get("/api/v1/openapi.json").json()["paths"]
    assert "/health/live" in paths
    assert "503" in paths["/health/ready"]["get"]["responses"]
