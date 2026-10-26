"""NFR-015 / SEC-015: JSON fields, redaction and secret scrubbing."""

import io
import json
import logging
from typing import Any

import pytest

from app.core.config import Settings
from app.core.observability.request_context import request_id_var
from app.core.observability.structured_logging import REDACTED, JsonFormatter, configure_logging


def _format(
    message: str = "hello", *, secrets: list[str] | None = None, **extra: Any
) -> dict[str, Any]:
    formatter = JsonFormatter(app_version="1.2.3", build="abc123", secrets=secrets or [])
    record = logging.LogRecord("nexacart.test", logging.WARNING, __file__, 1, message, None, None)
    record.__dict__.update(extra)
    parsed: dict[str, Any] = json.loads(formatter.format(record))
    return parsed


def test_required_fields_are_present() -> None:
    line = _format(request_id="req-12345678", route="/api/v1/x")
    assert line["level"] == "WARNING"
    assert line["message"] == "hello"
    assert line["request_id"] == "req-12345678"
    assert line["route"] == "/api/v1/x"
    assert line["version"] == "1.2.3"
    assert line["build"] == "abc123"
    assert line["timestamp"].endswith("+00:00")


def test_request_id_falls_back_to_the_context_variable() -> None:
    token = request_id_var.set("ctx-request-1")
    try:
        assert _format()["request_id"] == "ctx-request-1"
    finally:
        request_id_var.reset(token)


def test_non_request_logs_have_null_request_id_and_route() -> None:
    line = _format()
    assert line["request_id"] is None
    assert line["route"] is None


@pytest.mark.parametrize(
    "key",
    [
        "password",
        "new_password",
        "access_token",
        "Authorization",
        "cookie",
        "csrf_token",
        "api_key",
        "client_secret",
    ],
)
def test_sensitive_extra_fields_are_redacted(key: str) -> None:
    extra: dict[str, Any] = {key: "super-sensitive-value"}
    assert _format(**extra)[key] == REDACTED


def test_nested_sensitive_fields_are_redacted() -> None:
    line = _format(context={"user": "a", "password": "p4ss", "items": [{"token": "t0k"}]})
    assert line["context"] == {"user": "a", "password": REDACTED, "items": [{"token": REDACTED}]}


def test_non_sensitive_fields_are_kept() -> None:
    assert _format(order_id=42, status=200)["order_id"] == 42


@pytest.mark.parametrize(
    ("message", "leaked"),
    [
        ("connect to postgresql://nexacart:s3cretpw@db:5432/x failed", "s3cretpw"),
        ("header was Authorization: Bearer eyJhbGciOi.payload.sig", "eyJhbGciOi"),
        ("retrying with password=hunter2 now", "hunter2"),
        ("api_key: abc123def456", "abc123def456"),
    ],
)
def test_secrets_are_scrubbed_from_messages(message: str, leaked: str) -> None:
    assert leaked not in _format(message)["message"]


def test_configured_secret_values_are_scrubbed_anywhere() -> None:
    line = _format("value is Zq9-literal-secret here", secrets=["Zq9-literal-secret"])
    assert "Zq9-literal-secret" not in line["message"]
    assert REDACTED in line["message"]


def test_exception_text_is_scrubbed() -> None:
    formatter = JsonFormatter(app_version="v", build="b", secrets=["pw-in-traceback"])
    try:
        raise RuntimeError("boom pw-in-traceback")
    except RuntimeError:
        import sys

        record = logging.LogRecord("t", logging.ERROR, __file__, 1, "failed", None, sys.exc_info())
    out = formatter.format(record)
    assert "pw-in-traceback" not in out
    assert "RuntimeError" in out


def test_configure_logging_is_idempotent_and_keeps_foreign_handlers(settings: Settings) -> None:
    root = logging.getLogger()
    foreign = logging.NullHandler()
    root.addHandler(foreign)
    try:
        configure_logging(settings, stream=io.StringIO())
        configure_logging(settings, stream=io.StringIO())
        ours = [h for h in root.handlers if getattr(h, "_nexacart", False)]
        assert len(ours) == 1
        assert foreign in root.handlers
    finally:
        root.removeHandler(foreign)


def test_configured_database_password_never_appears_in_output(settings: Settings) -> None:
    buffer = io.StringIO()
    configure_logging(settings, stream=buffer)
    url = settings.database_url.get_secret_value()
    logging.getLogger("nexacart.test").error("cannot connect using %s", url)
    assert "placeholder" not in buffer.getvalue()
    assert url not in buffer.getvalue()
