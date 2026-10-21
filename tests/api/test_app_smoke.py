"""FOUND-001 API smoke: the app factory builds and serves its OpenAPI document."""

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_openapi_is_served_under_api_v1(settings: Settings) -> None:
    client = TestClient(create_app(settings))
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "NexaCart API"


def test_api_docs_are_disabled_in_production(settings: Settings) -> None:
    prod = settings.model_copy(update={"app_env": "production"})
    client = TestClient(create_app(prod))
    assert client.get("/api/v1/docs").status_code == 404
