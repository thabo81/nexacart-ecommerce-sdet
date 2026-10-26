"""Request correlation: X-Request-ID on every response and one structured access-log line.

Pure ASGI middleware (not BaseHTTPMiddleware) so it also wraps responses produced by exception
handlers. A client-supplied ID is used only if it is short and made of safe characters;
otherwise a new one is generated (NFR-016, Architecture 13.1).
"""

import logging
import re
import time
import uuid
from contextvars import ContextVar

from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-ID"
_VALID_REQUEST_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{7,63}")

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
access_logger = logging.getLogger("nexacart.access")


def new_request_id() -> str:
    return str(uuid.uuid4())


def request_id_from_scope(scope: Scope) -> str | None:
    state = scope.get("state")
    value = state.get("request_id") if isinstance(state, dict) else None
    return value if isinstance(value, str) else None


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = next(
            (
                value.decode("latin-1")
                for name, value in scope["headers"]
                if name == b"x-request-id"
            ),
            None,
        )
        request_id = (
            incoming if incoming and _VALID_REQUEST_ID.fullmatch(incoming) else new_request_id()
        )
        scope.setdefault("state", {})["request_id"] = request_id
        token = request_id_var.set(request_id)
        status = 500  # stays 500 if the app raises before a response starts
        started = time.perf_counter()

        async def send_with_request_id(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                headers = [
                    (name, value)
                    for name, value in message.get("headers", [])
                    if name.lower() != b"x-request-id"
                ]
                headers.append((b"x-request-id", request_id.encode("latin-1")))
                message = {**message, "headers": headers}
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            route = getattr(scope.get("route"), "path", None)
            # Route template only: raw paths and query strings can carry sensitive values.
            access_logger.info(
                "request completed",
                extra={
                    "method": scope["method"],
                    "route": route or "unmatched",
                    "status": status,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            request_id_var.reset(token)
