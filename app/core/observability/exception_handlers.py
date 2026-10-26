"""Maps every failure to the standard error envelope (FR-108, TR-011, SEC-015).

Never exposes stack traces, SQL, exception text or submitted values. Validation details carry
field paths, messages and error types only; the offending input is deliberately omitted.
"""

import logging
from collections.abc import Mapping, Sequence
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import ERROR_STATUS, AppError, ErrorCode
from app.core.observability.request_context import (
    REQUEST_ID_HEADER,
    new_request_id,
    request_id_from_scope,
)

logger = logging.getLogger("nexacart.errors")

_HTTP_ERRORS: dict[int, tuple[ErrorCode, str]] = {
    401: (ErrorCode.UNAUTHENTICATED, "Authentication is required."),
    403: (ErrorCode.FORBIDDEN, "You are not allowed to perform this action."),
    404: (ErrorCode.NOT_FOUND, "The requested resource was not found."),
    405: (ErrorCode.METHOD_NOT_ALLOWED, "This method is not allowed for the resource."),
    429: (ErrorCode.RATE_LIMITED, "Too many requests. Please try again later."),
}


def error_response(
    request: Request,
    code: ErrorCode,
    message: str,
    *,
    details: Sequence[Mapping[str, Any]] = (),
    status_code: int | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    request_id = request_id_from_scope(request.scope) or new_request_id()
    return JSONResponse(
        status_code=status_code or ERROR_STATUS[code],
        content={
            "error": {
                "code": code.value,
                "message": message,
                "details": [dict(item) for item in details],
                "request_id": request_id,
            }
        },
        headers={**(headers or {}), REQUEST_ID_HEADER: request_id},
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return error_response(request, exc.code, exc.message, details=exc.details, headers=exc.headers)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return error_response(
        request, ErrorCode.VALIDATION_ERROR, "The request is invalid.", details=details
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    # exc.detail is ignored: framework text is not part of the contract.
    if exc.status_code in _HTTP_ERRORS:
        code, message = _HTTP_ERRORS[exc.status_code]
        status_code = None
    elif exc.status_code >= 500:
        code, message, status_code = (
            ErrorCode.INTERNAL_ERROR,
            "An unexpected error occurred.",
            exc.status_code,
        )
    else:
        code, message, status_code = (
            ErrorCode.BAD_REQUEST,
            "The request could not be processed.",
            exc.status_code,
        )
    return error_response(
        request, code, message, status_code=status_code, headers=dict(exc.headers or {})
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = request_id_from_scope(request.scope) or new_request_id()
    request.scope.setdefault("state", {})["request_id"] = request_id
    logger.error(
        "unhandled exception",
        exc_info=exc,
        extra={
            "request_id": request_id,
            "route": getattr(request.scope.get("route"), "path", None),
        },
    )
    return error_response(request, ErrorCode.INTERNAL_ERROR, "An unexpected error occurred.")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
