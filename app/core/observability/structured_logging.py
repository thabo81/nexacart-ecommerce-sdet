"""Structured JSON logging with redaction (NFR-015, SEC-015, Architecture 13.1).

Each line has timestamp, level, logger, message, request_id, route, app version and build.
Request/response bodies and headers are never logged by the application. As a second line of
defence, sensitive-looking extra fields are redacted and known secret values, URL credentials
and bearer tokens are scrubbed from messages and tracebacks.
"""

import contextlib
import json
import logging
import re
import sys
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from typing import IO, Any

from pydantic import SecretStr
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

from app.core.config import Settings
from app.core.observability.request_context import request_id_var

REDACTED = "[REDACTED]"
_SENSITIVE_KEY = re.compile(
    r"password|passwd|secret|token|authorization|cookie|csrf|api[_-]?key|credential", re.IGNORECASE
)
_URL_CREDENTIALS = re.compile(r"(?<=://)([^:/@\s]+):([^@\s]+)@")
_AUTH_SCHEME = re.compile(r"\b(Bearer|Basic)\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE)
_KEY_VALUE_SECRET = re.compile(
    r"\b(password|passwd|secret|token|api[_-]?key)\s*[=:]\s*\S+", re.IGNORECASE
)
_RESERVED = set(logging.makeLogRecord({}).__dict__) | {
    "message",
    "asctime",
    "taskName",
    "color_message",
}
_OWN_FIELDS = {"request_id", "route"}


def _app_version() -> str:
    try:
        return version("nexacart")
    except PackageNotFoundError:
        return "unknown"


class JsonFormatter(logging.Formatter):
    def __init__(self, *, app_version: str, build: str, secrets: list[str]) -> None:
        super().__init__()
        self._app_version = app_version
        self._build = build
        self._secrets = sorted({s for s in secrets if s}, key=len, reverse=True)

    def scrub(self, text: str) -> str:
        for secret in self._secrets:
            text = text.replace(secret, REDACTED)
        text = _URL_CREDENTIALS.sub(rf"\1:{REDACTED}@", text)
        text = _AUTH_SCHEME.sub(rf"\1 {REDACTED}", text)
        return _KEY_VALUE_SECRET.sub(rf"\1={REDACTED}", text)

    def _redact(self, key: str, value: Any) -> Any:
        if _SENSITIVE_KEY.search(key):
            return REDACTED
        if isinstance(value, dict):
            return {str(k): self._redact(str(k), v) for k, v in value.items()}
        if isinstance(value, list | tuple):
            return [self._redact(key, item) for item in value]
        if isinstance(value, str):
            return self.scrub(value)
        return value

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=UTC)
        payload: dict[str, Any] = {
            "timestamp": timestamp.isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": self.scrub(record.getMessage()),
            "request_id": getattr(record, "request_id", None) or request_id_var.get(),
            "route": getattr(record, "route", None),
            "version": self._app_version,
            "build": self._build,
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and key not in _OWN_FIELDS:
                payload[key] = self._redact(key, value)
        if record.exc_info:
            payload["exception"] = self.scrub(self.formatException(record.exc_info))
        return json.dumps(payload, default=str)


def _secret_values(settings: Settings) -> list[str]:
    values: list[str] = []
    for field_value in settings.__dict__.values():
        if isinstance(field_value, SecretStr):
            secret = field_value.get_secret_value()
            values.append(secret)
            with contextlib.suppress(ArgumentError):
                values.append(make_url(secret).password or "")
    return values


def configure_logging(settings: Settings, *, stream: IO[str] | None = None) -> None:
    """Install one JSON handler on the root logger. Safe to call repeatedly."""
    root = logging.getLogger()
    for handler in list(root.handlers):
        if getattr(handler, "_nexacart", False):
            root.removeHandler(handler)
    handler = logging.StreamHandler(stream or sys.stdout)
    handler._nexacart = True  # type: ignore[attr-defined]
    handler.setFormatter(
        JsonFormatter(
            app_version=_app_version(), build=settings.build_sha, secrets=_secret_values(settings)
        )
    )
    root.addHandler(handler)
    root.setLevel(settings.log_level)

    # uvicorn's own loggers flow through the JSON handler; its plain-text access log is replaced
    # by the request-context middleware's single structured line (no raw URLs or query strings).
    for name in ("uvicorn", "uvicorn.error"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True
    access = logging.getLogger("uvicorn.access")
    access.handlers.clear()
    access.propagate = False
    access.setLevel(logging.CRITICAL)
