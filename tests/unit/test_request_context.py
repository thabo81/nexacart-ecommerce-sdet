"""Request-ID middleware at the ASGI level: injection attempts and request scoping."""

import asyncio
import io
import uuid
from typing import Any

import pytest

from app.core.config import Settings
from app.core.observability.request_context import RequestContextMiddleware, request_id_var
from app.core.observability.structured_logging import configure_logging


async def _ok_app(scope: dict[str, Any], receive: Any, send: Any) -> None:
    await send(
        {"type": "http.response.start", "status": 200, "headers": [(b"x-request-id", b"app-set")]}
    )
    await send({"type": "http.response.body", "body": b"ok"})


async def _call(request_id_header: bytes | None) -> tuple[dict[str, Any], dict[str, Any]]:
    headers = [(b"x-request-id", request_id_header)] if request_id_header is not None else []
    scope: dict[str, Any] = {"type": "http", "method": "GET", "path": "/x", "headers": headers}
    sent: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        return {"type": "http.request"}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await RequestContextMiddleware(_ok_app)(scope, receive, send)  # type: ignore[arg-type]
    return sent[0], scope


@pytest.mark.parametrize(
    "malicious",
    [
        b"abcd1234\r\nSet-Cookie: session=hijacked",
        b"abcd1234\nX-Injected: 1",
        b"abcd1234\rX-Injected: 1",
        b"abcd1234\x00nul-byte",
        b"id with spaces 1234",
        b'{"json":"injection-attempt"}',
    ],
)
def test_header_and_log_injection_attempts_are_replaced(malicious: bytes) -> None:
    start, scope = asyncio.run(_call(malicious))
    values = [v for k, v in start["headers"] if k == b"x-request-id"]
    assert len(values) == 1  # the app's own header was replaced, nothing was duplicated
    assert b"\r" not in values[0] and b"\n" not in values[0] and b"\x00" not in values[0]
    assert uuid.UUID(values[0].decode())
    assert scope["state"]["request_id"] == values[0].decode()


def test_context_variable_is_request_scoped_and_reset(settings: Settings) -> None:
    buffer = io.StringIO()
    configure_logging(settings, stream=buffer)
    assert request_id_var.get() is None
    asyncio.run(_call(b"scoped-id-0001"))
    assert request_id_var.get() is None  # nothing leaks into the next request or the process


def test_concurrent_requests_do_not_share_ids() -> None:
    async def run_all() -> list[tuple[dict[str, Any], dict[str, Any]]]:
        return list(
            await asyncio.gather(*[_call(f"concurrent-id-{i:04d}".encode()) for i in range(20)])
        )

    ids = [dict(start["headers"])[b"x-request-id"].decode() for start, _ in asyncio.run(run_all())]
    assert ids == [f"concurrent-id-{i:04d}" for i in range(20)]
