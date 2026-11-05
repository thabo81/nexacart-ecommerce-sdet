"""Shipping options and the five PRD §8.3 reference coupons (definitions live only here)."""

from dataclasses import dataclass
from datetime import datetime

from app.seed.constants import FAR_FUTURE, SEED_EPOCH


@dataclass(frozen=True)
class ShippingSpec:
    code: str
    name: str
    base_fee_minor: int
    estimate: str
    sort_order: int


SHIPPING = (
    ShippingSpec("standard", "Standard", 6000, "3\u20135 business days", 0),
    ShippingSpec("express", "Express", 12000, "1\u20132 business days", 1),
)


@dataclass(frozen=True)
class CouponSpec:
    code: str
    discount_type: str
    percentage_basis_points: int | None
    fixed_discount_minor: int | None
    maximum_discount_minor: int | None
    minimum_order_minor: int
    minimum_is_exclusive: bool
    starts_at: datetime
    expires_at: datetime
    is_active: bool
    global_usage_limit: int | None
    per_customer_usage_limit: int | None
    eligibility_rule: str


_PAST_START = datetime(2019, 1, 1, tzinfo=SEED_EPOCH.tzinfo)
_EXPIRED_AT = datetime(2020, 12, 31, 23, 59, 59, tzinfo=SEED_EPOCH.tzinfo)

COUPONS = (
    CouponSpec(
        "WELCOME10",
        "percentage",
        1000,
        None,
        20000,
        50000,
        False,
        SEED_EPOCH,
        FAR_FUTURE,
        True,
        None,
        1,
        "returning_customer",
    ),
    CouponSpec(
        "SAVE100",
        "fixed",
        None,
        10000,
        None,
        80000,
        True,
        SEED_EPOCH,
        FAR_FUTURE,
        True,
        100,
        3,
        "all_customers",
    ),
    CouponSpec(
        "ONCE1",
        "percentage",
        500,
        None,
        5000,
        0,
        False,
        SEED_EPOCH,
        FAR_FUTURE,
        True,
        1,
        1,
        "all_customers",
    ),
    CouponSpec(
        "EXPIRED5",
        "percentage",
        500,
        None,
        None,
        0,
        False,
        _PAST_START,
        _EXPIRED_AT,
        True,
        None,
        None,
        "all_customers",
    ),
    CouponSpec(
        "INACTIVE15",
        "percentage",
        1500,
        None,
        None,
        0,
        False,
        SEED_EPOCH,
        FAR_FUTURE,
        False,
        None,
        None,
        "all_customers",
    ),
)
