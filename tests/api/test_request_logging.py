"""One structured log line per request, correlated by request ID, with no sensitive content."""

import logging

import pytest

from tests.api.conftest import SEEDED_SECRETS, Probe, ProbeFactory


def _access_lines(probe: Probe) -> list[dict[str, object]]:
    return [line for line in probe.log_lines() if line["logger"] == "nexacart.access"]


def test_each_request_logs_one_correlated_line_with_route_and_status(probe: Probe) -> None:
    response = probe.client.get(
        "/api/v1/_probe/items?page=2", headers={"X-Request-ID": "log-req-0001"}
    )
    [line] = _access_lines(probe)
    assert line["request_id"] == response.headers["x-request-id"] == "log-req-0001"
    assert line["route"] == "/api/v1/_probe/items"  # the template, never the raw URL
    assert (line["method"], line["status"]) == ("GET", 200)
    assert isinstance(line["duration_ms"], float)
    assert {"timestamp", "level", "version", "build"} <= set(line)


def test_unmatched_routes_do_not_log_the_raw_path(probe: Probe) -> None:
    probe.client.get("/definitely/not/here")
    [line] = _access_lines(probe)
    assert line["route"] == "unmatched"
    assert line["status"] == 404
    assert "definitely" not in str(line)


def test_query_strings_headers_and_bodies_are_never_logged(probe: Probe) -> None:
    probe.client.get("/api/v1/_probe/items?page=1&token=query-secret-1")
    probe.client.get(
        "/health/live",
        headers={"Authorization": "Bearer header-secret-2", "Cookie": "sid=cookie-secret-3"},
    )
    probe.client.post("/api/v1/_probe/body", json={"quantity": 0, "password": "body-secret-4"})
    output = probe.logs.getvalue()
    for secret in ("query-secret-1", "header-secret-2", "cookie-secret-3", "body-secret-4"):
        assert secret not in output


def test_unhandled_exception_is_logged_once_with_request_id_and_no_response_leak(
    probe: Probe,
) -> None:
    response = probe.client.get("/api/v1/_probe/boom", headers={"X-Request-ID": "boom-log-0001"})
    errors = [line for line in probe.log_lines() if line["logger"] == "nexacart.errors"]
    assert len(errors) == 1
    assert errors[0]["request_id"] == "boom-log-0001"
    assert errors[0]["route"] == "/api/v1/_probe/boom"
    assert "RuntimeError" in str(errors[0]["exception"])
    assert "internal-detail" not in response.text
    [access] = _access_lines(probe)
    assert access["status"] == 500


def test_seeded_secrets_in_exception_text_reach_neither_the_client_nor_the_logs(
    probe: Probe,
) -> None:
    """A deliberately secret-laden exception chain: password, tokens, Bearer, Cookie, CSRF,
    query-string token, JWT, dict-style body and database URL credentials."""
    response = probe.client.get("/api/v1/_probe/leak", headers={"X-Request-ID": "leak-req-0001"})
    output = probe.logs.getvalue()
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    for name, secret in SEEDED_SECRETS.items():
        assert secret not in response.text, f"{name} leaked to the client"
        assert secret not in output, f"{name} leaked to the logs"


def test_exception_diagnostics_survive_redaction(probe: Probe) -> None:
    """Redaction must not destroy the information needed to diagnose a failure."""
    probe.client.get("/api/v1/_probe/leak", headers={"X-Request-ID": "leak-req-0002"})
    [error] = [line for line in probe.log_lines() if line["logger"] == "nexacart.errors"]
    assert error["request_id"] == "leak-req-0002"
    assert error["route"] == "/api/v1/_probe/leak"
    assert error["level"] == "ERROR"
    traceback = str(error["exception"])
    assert "RuntimeError: upstream call failed" in traceback
    assert "ConnectionError: could not connect using" in traceback  # chained cause is kept
    assert "[REDACTED]" in traceback
    [access] = _access_lines(probe)
    assert (access["method"], access["status"], access["request_id"]) == (
        "GET",
        500,
        "leak-req-0002",
    )
    assert access["route"] == "/api/v1/_probe/leak"
    assert isinstance(access["duration_ms"], float)


def test_no_raw_traceback_text_bypasses_sanitisation(probe: Probe) -> None:
    probe.client.get("/api/v1/_probe/leak")
    for line in probe.log_lines():
        for value in line.values():
            for secret in SEEDED_SECRETS.values():
                assert secret not in str(value)


def test_known_environment_secrets_are_scrubbed_even_without_a_recognisable_pattern(
    monkeypatch: pytest.MonkeyPatch, probe_factory: ProbeFactory
) -> None:
    monkeypatch.setenv("CLIENT_SECRET", "seed-envsecret-M13")
    probe = probe_factory()
    logging.getLogger("nexacart.test").error("startup used seed-envsecret-M13 for the client")
    assert "seed-envsecret-M13" not in probe.logs.getvalue()
    assert "startup used" in probe.logs.getvalue()
