"""Every emitted error code agrees with its HTTP status and the approved catalogue.

Each test asserts status AND code together (never one alone), plus request-ID equality.
"""

import pytest

from app.core.config import Settings
from app.core.errors import ERROR_STATUS, ErrorCode
from tests.api.conftest import PROBE, Probe, assert_envelope

C = ErrorCode


@pytest.mark.parametrize("code", list(ErrorCode), ids=lambda c: c.value)
def test_every_catalogue_code_is_emitted_with_its_catalogue_status(probe: Probe, code: C) -> None:
    """Known application errors keep their specific code; nothing is replaced by a generic one."""
    response = probe.client.get(f"{PROBE}/app-error/{code.value}")
    assert_envelope(response, ERROR_STATUS[code], code)


@pytest.mark.parametrize(
    ("raised_status", "expected_status", "expected_code"),
    [
        (400, 400, C.BAD_REQUEST),
        (401, 401, C.UNAUTHENTICATED),
        (403, 403, C.FORBIDDEN),
        (404, 404, C.NOT_FOUND),
        (405, 405, C.METHOD_NOT_ALLOWED),
        (422, 422, C.VALIDATION_ERROR),
        (429, 429, C.RATE_LIMITED),
        # Unmapped framework 4xx: normalised to a consistent 400 BAD_REQUEST.
        (402, 400, C.BAD_REQUEST),
        (409, 400, C.BAD_REQUEST),
        (413, 400, C.BAD_REQUEST),
        (418, 400, C.BAD_REQUEST),
        # Framework 5xx, including 503: INTERNAL_ERROR. NOT_READY is reserved for readiness.
        (500, 500, C.INTERNAL_ERROR),
        (501, 500, C.INTERNAL_ERROR),
        (502, 500, C.INTERNAL_ERROR),
        (503, 500, C.INTERNAL_ERROR),
        (504, 500, C.INTERNAL_ERROR),
    ],
)
def test_framework_http_errors_use_a_consistent_documented_mapping(
    probe: Probe, raised_status: int, expected_status: int, expected_code: C
) -> None:
    response = probe.client.get(f"{PROBE}/status/{raised_status}")
    assert_envelope(response, expected_status, expected_code)
    assert response.headers["x-probe"] == "kept"  # framework-supplied headers are preserved


def test_no_framework_status_yields_a_contradictory_code_and_status(probe: Probe) -> None:
    for raised in range(400, 600):
        response = probe.client.get(f"{PROBE}/status/{raised}")
        error = response.json()["error"]
        code = ErrorCode(error["code"])
        assert response.status_code == ERROR_STATUS[code], (raised, error["code"])
        assert code is not C.NOT_READY, f"{raised} must never produce NOT_READY"
        assert error["request_id"] == response.headers["x-request-id"]


def test_not_ready_is_only_emitted_by_the_readiness_contract(
    probe: Probe, unreachable_settings: Settings
) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    framework_503 = probe.client.get(f"{PROBE}/status/503")
    assert framework_503.json()["error"]["code"] != "NOT_READY"
    readiness = TestClient(create_app(unreachable_settings)).get("/health/ready")
    assert_envelope(readiness, 503, C.NOT_READY)


def test_unknown_route_is_404_not_found(probe: Probe) -> None:
    assert_envelope(probe.client.get("/api/v1/nothing-here"), 404, C.NOT_FOUND)


@pytest.mark.parametrize(
    ("method", "path"),
    [("POST", "/health/live"), ("DELETE", f"{PROBE}/items"), ("PUT", "/health/ready")],
)
def test_unsupported_methods_are_405_method_not_allowed(
    probe: Probe, method: str, path: str
) -> None:
    response = probe.client.request(method, path)
    assert_envelope(response, 405, C.METHOD_NOT_ALLOWED)
    assert "GET" in response.headers["allow"]


@pytest.mark.parametrize("path", [f"{PROBE}/boom", f"{PROBE}/bad-response", f"{PROBE}/leak"])
def test_unexpected_exceptions_are_generic_500_internal_error(probe: Probe, path: str) -> None:
    response = probe.client.get(path)
    error = assert_envelope(response, 500, C.INTERNAL_ERROR)
    assert error["message"] == "An unexpected error occurred."
    assert error["details"] == []
    for leaked in ("internal-detail", "Traceback", "RuntimeError", "not-an-integer", "seed-"):
        assert leaked not in response.text


def test_validation_errors_include_the_input_location(probe: Probe) -> None:
    cases = [
        (probe.client.get(f"{PROBE}/items?page_size=0"), "query.page_size"),
        (probe.client.get(f"{PROBE}/items/not-a-number"), "path.item_id"),
        (probe.client.post(f"{PROBE}/body", json={"quantity": 0}), "body.quantity"),
    ]
    for response, field in cases:
        error = assert_envelope(response, 422, C.VALIDATION_ERROR)
        assert field in {item["field"] for item in error["details"]}, (field, error["details"])
