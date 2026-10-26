"""NFR-024: the OpenAPI document is valid and truthful about the shared error contract."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate

from app.core.config import Settings
from app.main import create_app
from tests.api.conftest import Probe

HTTP_METHODS = {"get", "put", "post", "delete", "patch"}


@pytest.fixture
def spec(probe: Probe) -> dict[str, Any]:
    response = probe.client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    return response.json()  # type: ignore[no-any-return]


def test_document_is_valid_openapi(spec: dict[str, Any]) -> None:
    validate(spec)
    assert spec["openapi"].startswith("3.")


def test_fastapi_default_validation_schemas_are_replaced(spec: dict[str, Any]) -> None:
    schemas = spec["components"]["schemas"]
    assert "HTTPValidationError" not in schemas
    assert "ValidationError" not in schemas
    assert {"ErrorEnvelope", "ErrorBody"} <= set(schemas)


def test_422_responses_reference_the_error_envelope(spec: dict[str, Any]) -> None:
    seen = 0
    for path_item in spec["paths"].values():
        for method, operation in path_item.items():
            if method in HTTP_METHODS and "422" in operation["responses"]:
                schema = operation["responses"]["422"]["content"]["application/json"]["schema"]
                assert schema == {"$ref": "#/components/schemas/ErrorEnvelope"}
                seen += 1
    assert seen >= 2


def test_readiness_documents_503_with_the_error_envelope(spec: dict[str, Any]) -> None:
    response = spec["paths"]["/health/ready"]["get"]["responses"]["503"]
    assert response["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ErrorEnvelope"
    }


def test_every_response_declares_x_request_id(spec: dict[str, Any]) -> None:
    for path, path_item in spec["paths"].items():
        for method, operation in path_item.items():
            if method in HTTP_METHODS:
                for status, response in operation["responses"].items():
                    assert "X-Request-ID" in response["headers"], f"{method} {path} {status}"


def test_pagination_parameters_are_documented_with_limits(spec: dict[str, Any]) -> None:
    params = {p["name"]: p for p in spec["paths"]["/api/v1/_probe/items"]["get"]["parameters"]}
    assert params["page"]["schema"]["minimum"] == 1
    assert params["page_size"]["schema"]["maximum"] == 48
    assert params["page_size"]["schema"]["default"] == 12


def test_real_error_responses_validate_against_the_documented_schema(
    probe: Probe, spec: dict[str, Any]
) -> None:
    schema = {"$ref": "#/components/schemas/ErrorEnvelope", "components": spec["components"]}
    validator = Draft202012Validator(schema)
    responses = [
        probe.client.get("/nope"),
        probe.client.post("/health/live"),
        probe.client.get("/api/v1/_probe/items?page=0"),
        probe.client.get("/api/v1/_probe/conflict"),
        probe.client.get("/api/v1/_probe/boom"),
    ]
    assert {r.status_code for r in responses} == {404, 405, 422, 409, 500}
    for response in responses:
        validator.validate(response.json())


def _validate_against_spec(spec: dict[str, Any], path: str, method: str, response: Any) -> None:
    """Validate a real response body against the schema the OpenAPI document publishes for it."""
    documented = spec["paths"][path][method]["responses"]
    assert str(response.status_code) in documented, f"{method} {path} {response.status_code}"
    schema = documented[str(response.status_code)]["content"]["application/json"]["schema"]
    Draft202012Validator({**schema, "components": spec["components"]}).validate(response.json())


def test_success_responses_validate_against_published_schemas(
    probe: Probe, spec: dict[str, Any]
) -> None:
    """AC-071: responses of implemented endpoints validate against the OpenAPI schemas."""
    cases = [
        ("/health/live", "get", probe.client.get("/health/live")),
        ("/health/ready", "get", probe.client.get("/health/ready")),
        ("/api/v1/_probe/items", "get", probe.client.get("/api/v1/_probe/items")),
        ("/api/v1/_probe/items", "get", probe.client.get("/api/v1/_probe/items?page=99")),
        (
            "/api/v1/_probe/body",
            "post",
            probe.client.post("/api/v1/_probe/body", json={"quantity": 2}),
        ),
    ]
    for path, method, response in cases:
        assert response.status_code == 200, (path, response.text)
        _validate_against_spec(spec, path, method, response)


def test_readiness_503_validates_against_its_published_schema(
    unreachable_settings: Settings,
) -> None:
    app = create_app(unreachable_settings)
    client = TestClient(app)
    response = client.get("/health/ready")
    assert response.status_code == 503
    _validate_against_spec(
        client.get("/api/v1/openapi.json").json(), "/health/ready", "get", response
    )
