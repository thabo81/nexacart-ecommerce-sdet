"""FOUND-003: request IDs, error envelope, status mapping and pagination over HTTP."""

import re
import uuid
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.errors import ERROR_STATUS, ErrorCode
from app.main import create_app
from tests.api.conftest import TOTAL_ITEMS, Probe

UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
PROBE = "/api/v1/_probe"


def assert_envelope(response: httpx.Response, status: int, code: ErrorCode) -> dict[str, Any]:
    assert response.status_code == status
    error: dict[str, Any] = response.json()["error"]
    assert set(error) == {"code", "message", "details", "request_id"}
    assert error["code"] == code.value
    assert error["request_id"] == response.headers["x-request-id"]
    return error


def test_every_response_has_a_generated_request_id(probe: Probe) -> None:
    for path in ("/health/live", "/health/ready", f"{PROBE}/items", "/nope"):
        response = probe.client.get(path)
        assert UUID_RE.fullmatch(response.headers["x-request-id"]), path


def test_request_ids_are_unique_per_request(probe: Probe) -> None:
    ids = {probe.client.get("/health/live").headers["x-request-id"] for _ in range(5)}
    assert len(ids) == 5


def test_valid_client_request_id_is_echoed(probe: Probe) -> None:
    client_id = "qa-run-0001.step_7"
    response = probe.client.get("/health/live", headers={"X-Request-ID": client_id})
    assert response.headers["x-request-id"] == client_id


@pytest.mark.parametrize(
    "bad_id",
    [
        b"short",
        b"x" * 65,
        b"has space in it",
        b"<script>alert(1)</script>",
        "ünïcode-id-123".encode("latin-1"),  # raw bytes, as received on the wire
    ],
)
def test_invalid_client_request_id_is_replaced(probe: Probe, bad_id: bytes) -> None:
    response = probe.client.get("/health/live", headers={"X-Request-ID": bad_id})
    generated = response.headers["x-request-id"]
    assert generated.encode("latin-1") != bad_id
    assert uuid.UUID(generated)


def test_error_echoes_the_same_request_id_in_header_and_body(probe: Probe) -> None:
    response = probe.client.get("/nope", headers={"X-Request-ID": "trace-me-12345"})
    error = assert_envelope(response, 404, ErrorCode.NOT_FOUND)
    assert error["request_id"] == "trace-me-12345"


def test_unknown_route_is_404_not_found(probe: Probe) -> None:
    assert_envelope(probe.client.get("/api/v1/does-not-exist"), 404, ErrorCode.NOT_FOUND)


def test_wrong_method_is_405_with_envelope_and_allow_header(probe: Probe) -> None:
    response = probe.client.post("/health/live")
    assert_envelope(response, 405, ErrorCode.METHOD_NOT_ALLOWED)
    assert "GET" in response.headers["allow"]


def test_app_error_uses_catalogue_status_and_safe_details(probe: Probe) -> None:
    response = probe.client.get(f"{PROBE}/conflict")
    error = assert_envelope(
        response, ERROR_STATUS[ErrorCode.INSUFFICIENT_STOCK], ErrorCode.INSUFFICIENT_STOCK
    )
    assert error["details"] == [{"field": "quantity", "available": 2}]


def test_validation_error_lists_field_paths_and_omits_input(probe: Probe) -> None:
    response = probe.client.post(
        f"{PROBE}/body", json={"quantity": 0, "password": "hunter2-must-not-echo", "role": "admin"}
    )
    error = assert_envelope(response, 422, ErrorCode.VALIDATION_ERROR)
    fields = {item["field"] for item in error["details"]}
    assert {"body.quantity", "body.role"} <= fields
    assert "hunter2" not in response.text


def test_rejected_input_values_are_never_echoed_back(probe: Probe) -> None:
    response = probe.client.post(
        f"{PROBE}/body", json={"quantity": "bad-value-hunter2", "role": "admin-secret-value"}
    )
    error = assert_envelope(response, 422, ErrorCode.VALIDATION_ERROR)
    assert {"body.quantity", "body.role"} <= {item["field"] for item in error["details"]}
    for item in error["details"]:
        assert set(item) == {"field", "message", "type"}
    assert "hunter2" not in response.text
    assert "admin-secret-value" not in response.text


def test_malformed_json_is_422_validation_error(probe: Probe) -> None:
    response = probe.client.post(
        f"{PROBE}/body", content=b"{not json", headers={"content-type": "application/json"}
    )
    assert_envelope(response, 422, ErrorCode.VALIDATION_ERROR)


def test_unhandled_exception_is_generic_500_with_request_id(probe: Probe) -> None:
    response = probe.client.get(f"{PROBE}/boom", headers={"X-Request-ID": "boom-req-0001"})
    error = assert_envelope(response, 500, ErrorCode.INTERNAL_ERROR)
    assert error["request_id"] == "boom-req-0001"
    assert "internal-detail" not in response.text
    assert "Traceback" not in response.text


def test_readiness_503_now_carries_a_real_request_id(unreachable_settings: Settings) -> None:
    response = TestClient(create_app(unreachable_settings)).get("/health/ready")
    error = assert_envelope(response, 503, ErrorCode.NOT_READY)
    assert UUID_RE.fullmatch(error["request_id"])


class TestPagination:
    def test_defaults(self, probe: Probe) -> None:
        body = probe.client.get(f"{PROBE}/items").json()
        assert (body["page"], body["page_size"]) == (1, 12)
        assert len(body["items"]) == 12
        assert body["total_items"] == TOTAL_ITEMS
        assert body["total_pages"] == 3

    def test_last_partial_page(self, probe: Probe) -> None:
        body = probe.client.get(f"{PROBE}/items?page=3").json()
        assert [i["id"] for i in body["items"]] == list(range(25, 31))

    def test_page_beyond_last_is_200_with_empty_items_and_correct_metadata(
        self, probe: Probe
    ) -> None:
        response = probe.client.get(f"{PROBE}/items?page=99")
        assert response.status_code == 200
        body = response.json()
        assert body["items"] == []
        assert (body["page"], body["total_items"], body["total_pages"]) == (99, 30, 3)

    def test_max_page_size_is_accepted(self, probe: Probe) -> None:
        assert probe.client.get(f"{PROBE}/items?page_size=48").status_code == 200

    @pytest.mark.parametrize(
        ("query", "field"),
        [
            ("page=0", "query.page"),
            ("page=-1", "query.page"),
            ("page=abc", "query.page"),
            ("page_size=0", "query.page_size"),
            ("page_size=49", "query.page_size"),
            ("page_size=x", "query.page_size"),
        ],
    )
    def test_invalid_values_are_422_with_field_path(
        self, probe: Probe, query: str, field: str
    ) -> None:
        response = probe.client.get(f"{PROBE}/items?{query}")
        error = assert_envelope(response, 422, ErrorCode.VALIDATION_ERROR)
        assert field in {item["field"] for item in error["details"]}
