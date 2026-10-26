"""One structured log line per request, correlated by request ID, with no sensitive content."""

from tests.api.conftest import Probe


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


def test_secrets_in_an_exception_reach_neither_the_client_nor_the_logs(probe: Probe) -> None:
    response = probe.client.get("/api/v1/_probe/leak")
    secrets = ("placeholder", "postgresql", "leaked-jwt-value", "leaked-pw", "leaked-token")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    output = probe.logs.getvalue()
    for secret in secrets:
        assert secret not in response.text, f"{secret} leaked to the client"
        assert secret not in output, f"{secret} leaked to the logs"
    assert "connection failed for" in output  # the failure is still diagnosable
    assert "RuntimeError" in output
