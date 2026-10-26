"""Error-code catalogue and the application error type (PRD Appendix A, TR-011).

Codes and statuses mirror PRD Appendix A and are stable once approved. BAD_REQUEST (400),
METHOD_NOT_ALLOWED (405) and INTERNAL_ERROR (500) were approved by the owner on 2026-10-25 for
framework-level failures. The HTTP status is always derived from the code (ERROR_STATUS), so a
response can never pair a code with a contradictory status. A parity test checks this module
against Appendix A.
"""

from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class ErrorCode(StrEnum):
    # 401
    UNAUTHENTICATED = "UNAUTHENTICATED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    # 403
    FORBIDDEN = "FORBIDDEN"
    REVIEW_NOT_ELIGIBLE = "REVIEW_NOT_ELIGIBLE"
    # 404
    NOT_FOUND = "NOT_FOUND"
    # 409
    EMAIL_ALREADY_REGISTERED = "EMAIL_ALREADY_REGISTERED"
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"
    PRICE_CHANGED = "PRICE_CHANGED"
    PRODUCT_UNAVAILABLE = "PRODUCT_UNAVAILABLE"
    CART_EMPTY = "CART_EMPTY"
    WISHLIST_DUPLICATE = "WISHLIST_DUPLICATE"
    REVIEW_DUPLICATE = "REVIEW_DUPLICATE"
    ADDRESS_LIMIT_REACHED = "ADDRESS_LIMIT_REACHED"
    ORDER_NOT_CANCELLABLE = "ORDER_NOT_CANCELLABLE"
    INVALID_STATUS_TRANSITION = "INVALID_STATUS_TRANSITION"
    ORDER_ALREADY_PAID = "ORDER_ALREADY_PAID"
    PAYMENT_ATTEMPTS_EXHAUSTED = "PAYMENT_ATTEMPTS_EXHAUSTED"
    CATEGORY_NOT_EMPTY = "CATEGORY_NOT_EMPTY"
    ORDER_NOT_PAYABLE = "ORDER_NOT_PAYABLE"
    CHECKOUT_ALREADY_PENDING = "CHECKOUT_ALREADY_PENDING"
    CART_LOCKED = "CART_LOCKED"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    ORDER_BELOW_MINIMUM = "ORDER_BELOW_MINIMUM"
    # 422
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_CURRENT_PASSWORD = "INVALID_CURRENT_PASSWORD"
    COUPON_NOT_FOUND = "COUPON_NOT_FOUND"
    COUPON_NOT_ACTIVE = "COUPON_NOT_ACTIVE"
    COUPON_EXPIRED = "COUPON_EXPIRED"
    COUPON_MIN_ORDER_NOT_MET = "COUPON_MIN_ORDER_NOT_MET"
    COUPON_USAGE_LIMIT_REACHED = "COUPON_USAGE_LIMIT_REACHED"
    COUPON_NOT_ELIGIBLE = "COUPON_NOT_ELIGIBLE"
    IDEMPOTENCY_KEY_REQUIRED = "IDEMPOTENCY_KEY_REQUIRED"
    IDEMPOTENCY_KEY_REUSED = "IDEMPOTENCY_KEY_REUSED"
    # 429
    RATE_LIMITED = "RATE_LIMITED"
    # 503
    NOT_READY = "NOT_READY"
    # Framework-level codes (owner-approved 2026-10-25)
    BAD_REQUEST = "BAD_REQUEST"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


_STATUS_BY_CODE: dict[int, tuple[ErrorCode, ...]] = {
    401: (ErrorCode.UNAUTHENTICATED, ErrorCode.TOKEN_EXPIRED, ErrorCode.INVALID_CREDENTIALS),
    403: (ErrorCode.FORBIDDEN, ErrorCode.REVIEW_NOT_ELIGIBLE),
    404: (ErrorCode.NOT_FOUND,),
    409: (
        ErrorCode.EMAIL_ALREADY_REGISTERED,
        ErrorCode.INSUFFICIENT_STOCK,
        ErrorCode.PRICE_CHANGED,
        ErrorCode.PRODUCT_UNAVAILABLE,
        ErrorCode.CART_EMPTY,
        ErrorCode.WISHLIST_DUPLICATE,
        ErrorCode.REVIEW_DUPLICATE,
        ErrorCode.ADDRESS_LIMIT_REACHED,
        ErrorCode.ORDER_NOT_CANCELLABLE,
        ErrorCode.INVALID_STATUS_TRANSITION,
        ErrorCode.ORDER_ALREADY_PAID,
        ErrorCode.PAYMENT_ATTEMPTS_EXHAUSTED,
        ErrorCode.CATEGORY_NOT_EMPTY,
        ErrorCode.ORDER_NOT_PAYABLE,
        ErrorCode.CHECKOUT_ALREADY_PENDING,
        ErrorCode.CART_LOCKED,
        ErrorCode.DUPLICATE_RESOURCE,
        ErrorCode.ORDER_BELOW_MINIMUM,
    ),
    422: (
        ErrorCode.VALIDATION_ERROR,
        ErrorCode.INVALID_CURRENT_PASSWORD,
        ErrorCode.COUPON_NOT_FOUND,
        ErrorCode.COUPON_NOT_ACTIVE,
        ErrorCode.COUPON_EXPIRED,
        ErrorCode.COUPON_MIN_ORDER_NOT_MET,
        ErrorCode.COUPON_USAGE_LIMIT_REACHED,
        ErrorCode.COUPON_NOT_ELIGIBLE,
        ErrorCode.IDEMPOTENCY_KEY_REQUIRED,
        ErrorCode.IDEMPOTENCY_KEY_REUSED,
    ),
    429: (ErrorCode.RATE_LIMITED,),
    503: (ErrorCode.NOT_READY,),
    400: (ErrorCode.BAD_REQUEST,),
    405: (ErrorCode.METHOD_NOT_ALLOWED,),
    500: (ErrorCode.INTERNAL_ERROR,),
}

ERROR_STATUS: dict[ErrorCode, int] = {
    code: status for status, codes in _STATUS_BY_CODE.items() for code in codes
}
assert set(ERROR_STATUS) == set(ErrorCode), "every error code needs a status"  # noqa: S101


class AppError(Exception):
    """Raised by services/routes; rendered as the standard error envelope.

    The HTTP status comes from the catalogue, so a code can never be paired with the wrong
    status. `details` must be safe to show to the client (no internals, no other users' data).
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        details: Sequence[Mapping[str, Any]] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = [dict(item) for item in details or ()]
        self.headers = dict(headers or {})

    @property
    def status_code(self) -> int:
        return ERROR_STATUS[self.code]


class ErrorBody(BaseModel):
    code: ErrorCode
    message: str
    details: list[dict[str, Any]]
    request_id: str


class ErrorEnvelope(BaseModel):
    """The single error response shape (FR-108, AC-070)."""

    error: ErrorBody
