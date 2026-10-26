"""Structured JSON logging with redaction (NFR-015, SEC-015, Architecture 13.1).

Each line has timestamp, level, logger, message, request_id, route, app version and build.
Request/response bodies and headers are never logged by the application.

Redaction is layered and applies equally to ordinary fields, messages, exception text and
tracebacks, and to non-string values (they are converted to text before being scrubbed):

1. Known secret values (SecretStr settings, the database password, sensitive-named environment
   variables) are replaced wherever they appear, including in the final serialised line.
2. Recognised patterns are redacted: URL credentials, JWTs, Authorization/Cookie header lines,
   Bearer/Basic credentials, and key=value / "key": "value" pairs whose key contains password,
   secret, token, cookie, csrf, api key, credential, authorization or jwt (so access_token=...,
   refresh_token=..., client_secret=... and query-string tokens are covered).
3. Extra fields with sensitive-looking names are redacted wholesale.

This is practical coverage of recognised patterns. It cannot find an arbitrary unknown secret
embedded in free text; never put secrets in log messages or exception text.
"""

import contextlib
import json
import logging
import os
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
_WORDS = r"password|passwd|pwd|secret|token|authorization|cookie|csrf|api[_-]?key|credential|jwt"
_SENSITIVE_KEY = re.compile(_WORDS, re.IGNORECASE)
_URL_CREDENTIALS = re.compile(r"(?<=://)([^:/@\s]+):([^@\s]+)@")
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]*")
_HEADER_LINE = re.compile(
    r"\b(authorization|proxy-authorization|cookie|set-cookie|x-csrf-token|x-xsrf-token)"
    r"\s*:\s*[^\r\n]+",
    re.IGNORECASE,
)
_AUTH_SCHEME = re.compile(r"\b(Bearer|Basic)\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE)
_KEY_VALUE = re.compile(
    rf"""(?P<key>["']?[A-Za-z0-9_.-]*(?:{_WORDS})[A-Za-z0-9_.-]*["']?)"""
    r"""(?P<sep>\s*[=:]\s*)"""
    r"""(?!\[REDACTED\])(?P<value>"[^"]*"|'[^']*'|[^\s,;&)}\]"']+)""",
    re.IGNORECASE,
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
        self._secrets = sorted({s for s in secrets if len(s) >= 4}, key=len, reverse=True)

    def scrub(self, text: str) -> str:
        for secret in self._secrets:
            text = text.replace(secret, REDACTED)
        text = _JWT.sub(REDACTED, text)
        text = _URL_CREDENTIALS.sub(rf"\1:{REDACTED}@", text)
        text = _HEADER_LINE.sub(rf"\1: {REDACTED}", text)
        text = _AUTH_SCHEME.sub(rf"\1 {REDACTED}", text)
        return _KEY_VALUE.sub(rf"\g<key>\g<sep>{REDACTED}", text)

    def _redact(self, key: str, value: Any) -> Any:
        if _SENSITIVE_KEY.search(key):
            return REDACTED
        if value is None or isinstance(value, bool | int | float):
            return value
        if isinstance(value, dict):
            return {str(k): self._redact(str(k), v) for k, v in value.items()}
        if isinstance(value, list | tuple | set | frozenset):
            return [self._redact(key, item) for item in value]
        # Strings and arbitrary objects (e.g. an exception passed in `extra`): text is scrubbed
        # *before* serialisation, so json's default=str can never emit an unredacted value.
        if isinstance(value, BaseException):  # keep the type: it is the useful diagnostic
            value = f"{type(value).__name__}: {value}"
        return self.scrub(value if isinstance(value, str) else str(value))

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
        if record.stack_info:
            payload["stack"] = self.scrub(self.formatStack(record.stack_info))
        line = json.dumps(payload, default=str)
        # Last line of defence for known secrets, including their JSON-escaped form.
        for secret in self._secrets:
            line = line.replace(secret, REDACTED).replace(json.dumps(secret)[1:-1], REDACTED)
        return line


def _secret_values(settings: Settings) -> list[str]:
    # Values of sensitive-named environment variables (e.g. CLIENT_SECRET) are secrets too.
    values: list[str] = [v for k, v in os.environ.items() if _SENSITIVE_KEY.search(k)]
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
