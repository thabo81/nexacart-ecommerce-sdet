"""Coupon and shipping tables (ERD §3.4)."""

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base
from app.persistence.models._common import (
    bool_col,
    created_at,
    in_list,
    optional_ts,
    updated_at,
    uuid_pk,
)


class Coupon(Base):
    __tablename__ = "coupons"
    __table_args__ = (
        UniqueConstraint("code", name="uq_coupon_code"),
        CheckConstraint("code ~ '^[A-Z0-9_-]{3,20}$'", name="ck_coupons_code_format"),
        CheckConstraint(
            in_list("discount_type", ("percentage", "fixed")), name="ck_coupons_discount_type"
        ),
        CheckConstraint(
            "percentage_basis_points IS NULL OR percentage_basis_points BETWEEN 1 AND 10000",
            name="ck_coupons_percentage_range",
        ),
        CheckConstraint(
            "fixed_discount_minor IS NULL OR fixed_discount_minor > 0",
            name="ck_coupons_fixed_discount_positive",
        ),
        CheckConstraint(
            "maximum_discount_minor IS NULL OR maximum_discount_minor >= 0",
            name="ck_coupons_maximum_discount_nonnegative",
        ),
        CheckConstraint("minimum_order_minor >= 0", name="ck_coupons_minimum_order_nonnegative"),
        CheckConstraint(
            "(discount_type = 'percentage' AND percentage_basis_points IS NOT NULL"
            " AND fixed_discount_minor IS NULL)"
            " OR (discount_type = 'fixed' AND fixed_discount_minor IS NOT NULL"
            " AND percentage_basis_points IS NULL)",
            name="ck_coupons_discount_value_matches_type",
        ),
        CheckConstraint("starts_at < expires_at", name="ck_coupons_validity_window"),
        CheckConstraint(
            "global_usage_limit IS NULL OR global_usage_limit > 0",
            name="ck_coupons_global_usage_limit_positive",
        ),
        CheckConstraint(
            "per_customer_usage_limit IS NULL OR per_customer_usage_limit > 0",
            name="ck_coupons_per_customer_usage_limit_positive",
        ),
        CheckConstraint(
            in_list("eligibility_rule", ("all_customers", "returning_customer")),
            name="ck_coupons_eligibility_rule",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(String(20))
    discount_type: Mapped[str] = mapped_column(Text)
    percentage_basis_points: Mapped[int | None]
    fixed_discount_minor: Mapped[int | None] = mapped_column(BigInteger)
    maximum_discount_minor: Mapped[int | None] = mapped_column(BigInteger)
    minimum_order_minor: Mapped[int] = mapped_column(BigInteger)
    minimum_is_exclusive: Mapped[bool] = bool_col()
    starts_at: Mapped[datetime]
    expires_at: Mapped[datetime]
    is_active: Mapped[bool] = bool_col()
    global_usage_limit: Mapped[int | None]
    per_customer_usage_limit: Mapped[int | None]
    eligibility_rule: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at()
    updated_at: Mapped[datetime] = updated_at()


class CouponUsage(Base):
    __tablename__ = "coupon_usages"
    __table_args__ = (
        UniqueConstraint("order_id", name="uq_coupon_usage_order"),
        CheckConstraint(
            in_list("usage_state", ("reserved", "consumed", "released")),
            name="ck_coupon_usages_state",
        ),
        CheckConstraint(
            "(usage_state = 'reserved' AND finalized_at IS NULL)"
            " OR (usage_state IN ('consumed', 'released') AND finalized_at IS NOT NULL)",
            name="ck_coupon_usages_finalization_consistency",
        ),
        Index("ix_coupon_usages_coupon_state", "coupon_id", "usage_state"),
        Index("ix_coupon_usages_customer_coupon_state", "customer_id", "coupon_id", "usage_state"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    coupon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("coupons.id"))
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"))
    usage_state: Mapped[str] = mapped_column(Text)
    reserved_at: Mapped[datetime]
    finalized_at: Mapped[datetime | None] = optional_ts()


class ShippingOption(Base):
    __tablename__ = "shipping_options"
    __table_args__ = (
        UniqueConstraint("code", name="uq_shipping_options_code"),
        CheckConstraint("code ~ '^[a-z0-9_-]{1,30}$'", name="ck_shipping_options_code_format"),
        CheckConstraint("base_fee_minor >= 0", name="ck_shipping_options_fee_nonnegative"),
        CheckConstraint("sort_order >= 0", name="ck_shipping_options_sort_order_nonnegative"),
        Index("ix_shipping_options_active_sort", "is_active", "sort_order", "id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(String(30))
    display_name: Mapped[str] = mapped_column(String(80))
    base_fee_minor: Mapped[int] = mapped_column(BigInteger)
    delivery_estimate: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = bool_col()
    sort_order: Mapped[int]
