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


SEEDED = [
    ("password", "login failed password=seed-pw-1 for user", "seed-pw-1"),
    ("token", "bad token=seed-tok-2 rejected", "seed-tok-2"),
    ("access_token", "got access_token=seed-acc-3&x=1", "seed-acc-3"),
    ("refresh_token", "refresh_token: seed-ref-4 expired", "seed-ref-4"),
    ("client_secret", "client_secret=seed-cs-5", "seed-cs-5"),
    ("bearer", "Authorization: Bearer seed-bearer-6", "seed-bearer-6"),
    ("basic", "Authorization: Basic c2VlZC1iYXNpYy03Ong=", "c2VlZC1iYXNpYy03Ong="),
    ("bare bearer", "rejected credential Bearer seed-bearer-26 from client", "seed-bearer-26"),
    ("bare basic", "client sent Basic c2VlZC1iYXNpYy0yNzo= value", "c2VlZC1iYXNpYy0yNzo="),
    ("cookie header", "Cookie: sid=seed-cookie-8; theme=dark", "seed-cookie-8"),
    ("set-cookie", "Set-Cookie: session=seed-setck-9; HttpOnly", "seed-setck-9"),
    (
        "cookie secret not first",
        "Cookie: theme=dark; sid=seed-cookie-24; lang=en",
        "seed-cookie-24",
    ),
    (
        "set-cookie secret not first",
        "Set-Cookie: a=b; session=seed-setck-25; Path=/",
        "seed-setck-25",
    ),
    ("csrf field", "csrf_token=seed-csrf-10", "seed-csrf-10"),
    ("csrf header", "X-CSRF-Token: seed-xcsrf-11", "seed-xcsrf-11"),
    ("query string", "failed GET /api/v1/x?token=seed-qs-12&page=2", "seed-qs-12"),
    ("query string url", "https://h/cb?access_token=seed-url-13", "seed-url-13"),
    ("database url", "connect postgresql+psycopg://u:seed-db-14@db:5432/x failed", "seed-db-14"),
    ("json", '{"password": "seed-json-15", "refresh_token": "seed-json-16"}', "seed-json-15"),
    ("json 2", '{"password": "seed-json-15", "refresh_token": "seed-json-16"}', "seed-json-16"),
    ("python dict", "{'client_secret': 'seed-dict-17', 'user': 'bob'}", "seed-dict-17"),
    ("jwt", "invalid eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.seed-jwt-18", "seed-jwt-18"),
]


@pytest.mark.parametrize(("name", "message", "secret"), SEEDED, ids=[c[0] for c in SEEDED])
def test_seeded_secret_never_survives_in_a_message(name: str, message: str, secret: str) -> None:
    assert secret not in _format(message)["message"], name


@pytest.mark.parametrize(("name", "message", "secret"), SEEDED, ids=[c[0] for c in SEEDED])
def test_seeded_secret_never_survives_in_exception_text_or_traceback(
    name: str, message: str, secret: str
) -> None:
    formatter = JsonFormatter(app_version="v", build="b", secrets=[])
    try:
        try:
            raise ValueError(message)
        except ValueError as cause:
            raise RuntimeError(f"wrapped: {message}") from cause
    except RuntimeError:
        import sys

        record = logging.LogRecord("t", logging.ERROR, __file__, 1, "failed", None, sys.exc_info())
    output = formatter.format(record)
    assert secret not in output, name
    assert "RuntimeError" in output
    assert "ValueError" in output  # the chain and exception types remain diagnosable


def test_exception_objects_in_extra_fields_are_scrubbed_before_serialisation() -> None:
    line = _format(error=RuntimeError("failed password=seed-extra-19"), detail=ValueError("x"))
    assert "seed-extra-19" not in json.dumps(line)
    assert line["error"].startswith("RuntimeError: failed password=")
    assert line["detail"] == "ValueError: x"


def test_non_string_extra_values_are_scrubbed_after_conversion() -> None:
    class Carrier:
        def __repr__(self) -> str:
            return "Carrier(password=seed-obj-20)"

    assert "seed-obj-20" not in json.dumps(_format(obj=Carrier(), many=[Carrier()]))


def test_known_secret_values_are_scrubbed_in_the_serialised_line_too() -> None:
    secret = 'odd"secret\\value-21'
    out = JsonFormatter(app_version="v", build="b", secrets=[secret]).format(
        logging.LogRecord("t", logging.INFO, __file__, 1, f"x {secret} y", None, None)
    )
    assert "value-21" not in out
    json.loads(out)  # still valid JSON after replacement


def test_environment_secrets_are_scrubbed(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    monkeypatch.setenv("CLIENT_SECRET", "seed-env-22")
    monkeypatch.setenv("SOME_API_KEY", "seed-env-23")
    monkeypatch.setenv("LOG_FORMAT_NAME", "not-sensitive-value")
    buffer = io.StringIO()
    configure_logging(settings, stream=buffer)
    logging.getLogger("nexacart.test").error(
        "saw seed-env-22 and seed-env-23 and not-sensitive-value"
    )
    out = buffer.getvalue()
    assert "seed-env-22" not in out and "seed-env-23" not in out
    assert "not-sensitive-value" in out


def test_useful_non_sensitive_text_is_preserved() -> None:
    for message in [
        "request completed in 12ms for route /api/v1/items status 200",
        "Order 42 created for user 7",
        "database check failed: OperationalError",
    ]:
        assert _format(message)["message"] == message
