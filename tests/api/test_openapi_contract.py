"""Operation-level OpenAPI contract tests (NFR-024, AC-071, FR-106).

For each case the test fetches the published document, finds the operation, picks the documented
response for the ACTUAL status (or the operation's `default` when that status is not documented
explicitly), and validates the real body and headers against it. These tests are meant to be run
by CI later (TEST-001); nothing here claims they already run in GitHub Actions.
"""

from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate

from app.core.config import Settings
from app.main import create_app
from tests.api.conftest import PROBE, Probe

HTTP_METHODS = {"get", "put", "post", "delete", "patch", "options", "head", "trace"}


@pytest.fixture
def spec(probe: Probe) -> dict[str, Any]:
    response = probe.client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    document: dict[str, Any] = response.json()
    return document


def resolve(spec: dict[str, Any], obj: dict[str, Any]) -> dict[str, Any]:
    if "$ref" not in obj:
        return obj
    node: Any = spec
    for part in obj["$ref"].removeprefix("#/").split("/"):
        node = node[part]
    return resolve(spec, node)


def documented_response(
    spec: dict[str, Any], path: str, method: str, status: int
) -> tuple[str, dict[str, Any]]:
    responses = spec["paths"][path][method]["responses"]
    key = str(status) if str(status) in responses else "default"
    assert key in responses, f"{method.upper()} {path} documents neither {status} nor default"
    return key, resolve(spec, responses[key])


def assert_conforms(
    spec: dict[str, Any],
    documented: dict[str, Any],
    response: httpx.Response,
) -> None:
    """Validate the real body and headers against one documented response object."""
    assert response.headers["content-type"].startswith("application/json")
    schema = documented["content"]["application/json"]["schema"]
    Draft202012Validator({**schema, "components": spec["components"]}).validate(response.json())
    declared = {
        name.lower(): resolve(spec, header) for name, header in documented["headers"].items()
    }
    assert "x-request-id" in declared, "response must declare X-Request-ID"
    for name, header in declared.items():
        assert name in response.headers, f"documented header {name} missing from the response"
        Draft202012Validator(header["schema"]).validate(response.headers[name])


def assert_operation_contract(
    spec: dict[str, Any],
    path: str,
    method: str,
    response: httpx.Response,
    *,
    explicit: bool,
) -> dict[str, Any]:
    key, documented = documented_response(spec, path, method, response.status_code)
    if explicit:
        assert key == str(response.status_code), f"{response.status_code} should be documented"
    else:
        assert key == "default", f"{response.status_code} should fall back to the default"
    assert_conforms(spec, documented, response)
    return documented


ENVELOPE_REF = {"$ref": "#/components/schemas/ErrorEnvelope"}


def test_document_is_valid_openapi_and_has_no_fastapi_validation_schemas(
    spec: dict[str, Any],
) -> None:
    validate(spec)
    assert spec["openapi"].startswith("3.")
    schemas = spec["components"]["schemas"]
    assert "HTTPValidationError" not in schemas and "ValidationError" not in schemas
    assert {"ErrorEnvelope", "ErrorBody"} <= set(schemas)


def test_error_envelope_schema_declares_the_standard_fields(spec: dict[str, Any]) -> None:
    envelope = spec["components"]["schemas"]["ErrorEnvelope"]
    body = spec["components"]["schemas"]["ErrorBody"]
    assert envelope["required"] == ["error"]
    assert envelope["properties"]["error"] == {"$ref": "#/components/schemas/ErrorBody"}
    assert set(body["required"]) == {"code", "message", "details", "request_id"}
    assert "VALIDATION_ERROR" in spec["components"]["schemas"]["ErrorCode"]["enum"]


def test_health_routes_remain_unversioned(spec: dict[str, Any]) -> None:
    paths = set(spec["paths"])
    assert {"/health/live", "/health/ready"} <= paths
    assert not any(p.startswith("/api/v1/health") for p in paths)
    assert all(p.startswith("/api/v1/") for p in paths if "_probe" in p)


def test_every_operation_declares_request_id_and_a_default_error_response(
    spec: dict[str, Any],
) -> None:
    standard = spec["components"]["responses"]["StandardError"]
    assert standard["content"]["application/json"]["schema"] == ENVELOPE_REF
    assert "X-Request-ID" in standard["headers"]
    operations = 0
    for path, item in spec["paths"].items():
        for method, operation in item.items():
            if method not in HTTP_METHODS:
                continue
            operations += 1
            assert operation["responses"]["default"] == {
                "$ref": "#/components/responses/StandardError"
            }, f"{method.upper()} {path}"
            for status, response in operation["responses"].items():
                if "$ref" not in response:
                    assert "X-Request-ID" in response["headers"], f"{path} {status}"
    assert operations >= 8


@pytest.mark.parametrize(
    ("path", "method", "url"),
    [
        ("/health/live", "get", "/health/live"),
        ("/health/ready", "get", "/health/ready"),
        (f"{PROBE}/items", "get", f"{PROBE}/items"),
        (f"{PROBE}/items", "get", f"{PROBE}/items?page=99"),
        (f"{PROBE}/items/{{item_id}}", "get", f"{PROBE}/items/3"),
    ],
)
def test_success_responses_use_their_explicit_success_schema(
    probe: Probe, spec: dict[str, Any], path: str, method: str, url: str
) -> None:
    response = probe.client.get(url)
    assert response.status_code == 200
    documented = assert_operation_contract(spec, path, method, response, explicit=True)
    schema = documented["content"]["application/json"]["schema"]
    assert schema != ENVELOPE_REF, "a success response must not be described as an error"


def test_post_success_uses_its_explicit_success_schema(probe: Probe, spec: dict[str, Any]) -> None:
    response = probe.client.post(f"{PROBE}/body", json={"quantity": 2})
    documented = assert_operation_contract(spec, f"{PROBE}/body", "post", response, explicit=True)
    assert documented["content"]["application/json"]["schema"] != ENVELOPE_REF


def test_explicit_404_is_published_and_preserved(probe: Probe, spec: dict[str, Any]) -> None:
    response = probe.client.get(f"{PROBE}/items/999")
    assert response.status_code == 404
    documented = assert_operation_contract(
        spec, f"{PROBE}/items/{{item_id}}", "get", response, explicit=True
    )
    assert documented["content"]["application/json"]["schema"] == ENVELOPE_REF
    assert "X-Request-ID" in documented["headers"]
    # the success response of the same operation keeps its own schema
    success = spec["paths"][f"{PROBE}/items/{{item_id}}"]["get"]["responses"]["200"]
    assert success["content"]["application/json"]["schema"] != ENVELOPE_REF


def test_explicit_409_is_published_and_preserved(probe: Probe, spec: dict[str, Any]) -> None:
    response = probe.client.get(f"{PROBE}/conflict")
    assert response.status_code == 409
    assert_operation_contract(spec, f"{PROBE}/conflict", "get", response, explicit=True)


@pytest.mark.parametrize(
    ("method", "path", "url", "kwargs"),
    [
        ("get", f"{PROBE}/items", f"{PROBE}/items?page=0", {}),
        ("get", f"{PROBE}/items", f"{PROBE}/items?page_size=49", {}),
        ("get", f"{PROBE}/items/{{item_id}}", f"{PROBE}/items/abc", {}),
        ("post", f"{PROBE}/body", f"{PROBE}/body", {"json": {"quantity": 0}}),
    ],
)
def test_422_is_published_as_the_error_envelope_and_matches_real_responses(
    probe: Probe, spec: dict[str, Any], method: str, path: str, url: str, kwargs: dict[str, Any]
) -> None:
    response = probe.client.request(method.upper(), url, **kwargs)
    assert response.status_code == 422
    documented = assert_operation_contract(spec, path, method, response, explicit=True)
    assert documented["content"]["application/json"]["schema"] == ENVELOPE_REF
    assert "input location" in documented["description"]
    assert documented["content"]["application/json"]["example"]["error"]["code"] == (
        "VALIDATION_ERROR"
    )
    fields = {d["field"] for d in response.json()["error"]["details"]}
    assert all(f.split(".")[0] in {"query", "body", "path", "header"} for f in fields)


@pytest.mark.parametrize("url", [f"{PROBE}/boom", f"{PROBE}/bad-response"])
def test_unexpected_500_falls_back_to_the_documented_default_error(
    probe: Probe, spec: dict[str, Any], url: str
) -> None:
    response = probe.client.get(url)
    assert response.status_code == 500
    documented = assert_operation_contract(spec, url, "get", response, explicit=False)
    assert documented["content"]["application/json"]["schema"] == ENVELOPE_REF
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"


def test_readiness_503_is_published_explicitly_and_matches(unreachable_settings: Settings) -> None:
    client = TestClient(create_app(unreachable_settings))
    spec = client.get("/api/v1/openapi.json").json()
    response = client.get("/health/ready")
    assert response.status_code == 503
    documented = assert_operation_contract(spec, "/health/ready", "get", response, explicit=True)
    assert documented["content"]["application/json"]["schema"] == ENVELOPE_REF
    assert response.json()["error"]["code"] == "NOT_READY"
    # the explicit operation-level description was not overwritten by the shared default
    raw = spec["paths"]["/health/ready"]["get"]["responses"]["503"]
    assert "NOT_READY" in raw["description"]


@pytest.mark.parametrize(
    ("method", "url"),
    [("GET", "/api/v1/not-a-route"), ("POST", "/health/live"), ("DELETE", f"{PROBE}/items")],
)
def test_framework_level_404_and_405_match_the_shared_standard_error(
    probe: Probe, spec: dict[str, Any], method: str, url: str
) -> None:
    """No operation exists for these, so the shared StandardError response is the contract."""
    response = probe.client.request(method, url)
    assert response.status_code in {404, 405}
    standard = resolve(spec, {"$ref": "#/components/responses/StandardError"})
    assert_conforms(spec, standard, response)
