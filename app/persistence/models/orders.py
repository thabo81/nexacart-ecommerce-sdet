"""Order, payment and refund tables (ERD §3.5)."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CHAR,
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base
from app.persistence.models._common import (
    IDEMPOTENCY_KEY_PATTERN,
    ORDER_STATUSES,
    created_at,
    in_list,
    optional_ts,
    updated_at,
    uuid_pk,
)


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("order_number", name="uq_order_number"),
        CheckConstraint(in_list("status", ORDER_STATUSES), name="ck_orders_status"),
        CheckConstraint(
            "subtotal_minor >= 0 AND discount_minor >= 0"
            " AND shipping_fee_minor >= 0 AND total_minor >= 0",
            name="ck_orders_money_nonnegative",
        ),
        CheckConstraint(
            "discount_minor <= subtotal_minor", name="ck_orders_discount_not_above_subtotal"
        ),
        CheckConstraint(
            "total_minor = subtotal_minor - discount_minor + shipping_fee_minor",
            name="ck_orders_total_arithmetic",
        ),
        CheckConstraint(
            "reservation_deadline > placed_at", name="ck_orders_reservation_after_placement"
        ),
        CheckConstraint("order_number ~ '^NC-[0-9]{8}-[0-9]{6}$'", name="ck_orders_number_format"),
        Index("ix_orders_customer_placed_at", "customer_id", text("placed_at DESC")),
        Index("ix_orders_status_deadline", "status", "reservation_deadline"),
        Index(
            "uq_one_pending_order_per_customer",
            "customer_id",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_number: Mapped[str] = mapped_column(String(18))
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(Text)
    subtotal_minor: Mapped[int] = mapped_column(BigInteger)
    discount_minor: Mapped[int] = mapped_column(BigInteger)
    shipping_fee_minor: Mapped[int] = mapped_column(BigInteger)
    total_minor: Mapped[int] = mapped_column(BigInteger)
    coupon_code_snapshot: Mapped[str | None] = mapped_column(String(20))
    shipping_option_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("shipping_options.id"))
    shipping_option_code_snapshot: Mapped[str] = mapped_column(String(30))
    shipping_option_name_snapshot: Mapped[str] = mapped_column(String(80))
    reservation_deadline: Mapped[datetime]
    placed_at: Mapped[datetime]
    cancelled_at: Mapped[datetime | None] = optional_ts()
    created_at: Mapped[datetime] = created_at()
    updated_at: Mapped[datetime] = updated_at()


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "variant_id", name="uq_order_variant_line"),
        CheckConstraint("unit_price_minor > 0", name="ck_order_items_unit_price_positive"),
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint(
            "line_total_minor = unit_price_minor * quantity", name="ck_order_items_line_total"
        ),
        CheckConstraint(
            "btrim(product_name_snapshot) <> ''", name="ck_order_items_product_name_nonblank"
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"))
    variant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT")
    )
    product_name_snapshot: Mapped[str] = mapped_column(String(200))
    variant_description_snapshot: Mapped[str] = mapped_column(String(1000))
    sku_snapshot: Mapped[str] = mapped_column(String(80))
    image_asset_key_snapshot: Mapped[str] = mapped_column(String(240))
    unit_price_minor: Mapped[int] = mapped_column(BigInteger)
    quantity: Mapped[int]
    line_total_minor: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = created_at()


class OrderAddressSnapshot(Base):
    __tablename__ = "order_address_snapshots"
    __table_args__ = (
        CheckConstraint(
            "postal_code ~ '^[0-9]{4}$'", name="ck_order_address_snapshots_postal_code_format"
        ),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    recipient_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(16))
    line1: Mapped[str] = mapped_column(String(150))
    line2: Mapped[str | None] = mapped_column(String(150))
    city: Mapped[str] = mapped_column(String(80))
    province: Mapped[str] = mapped_column(String(80))
    postal_code: Mapped[str] = mapped_column(String(4))
    country_code: Mapped[str] = mapped_column(CHAR(2))
    created_at: Mapped[datetime] = created_at()


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    __table_args__ = (
        CheckConstraint(
            in_list("to_status", ORDER_STATUSES), name="ck_order_status_history_to_status"
        ),
        CheckConstraint(
            f"from_status IS NULL OR {in_list('from_status', ORDER_STATUSES)}",
            name="ck_order_status_history_from_status",
        ),
        CheckConstraint(
            "NOT (actor_type = 'admin' AND to_status = 'cancelled')"
            " OR (reason IS NOT NULL AND char_length(btrim(reason)) BETWEEN 1 AND 200)",
            name="ck_order_status_history_admin_cancel_reason",
        ),
        CheckConstraint(
            in_list("actor_type", ("customer", "admin", "system")),
            name="ck_order_status_history_actor_type",
        ),
        Index("ix_order_status_history_order_time", "order_id", "occurred_at"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"))
    from_status: Mapped[str | None] = mapped_column(Text)
    to_status: Mapped[str] = mapped_column(Text)
    actor_type: Mapped[str] = mapped_column(Text)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str | None] = mapped_column(String(200))
    request_id: Mapped[str | None] = mapped_column(String(100))
    occurred_at: Mapped[datetime]


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"
    __table_args__ = (
        UniqueConstraint("order_id", "attempt_number", name="uq_payment_attempt_number"),
        UniqueConstraint("order_id", "idempotency_key", name="uq_payment_idempotency_key"),
        UniqueConstraint("idempotency_record_id", name="uq_payment_attempts_idempotency_record"),
        CheckConstraint("attempt_number > 0", name="ck_payment_attempts_attempt_number_positive"),
        CheckConstraint(
            in_list("outcome", ("approved", "declined", "timed_out", "error")),
            name="ck_payment_attempts_outcome",
        ),
        CheckConstraint("amount_minor > 0", name="ck_payment_attempts_amount_positive"),
        CheckConstraint(
            f"idempotency_key ~ '{IDEMPOTENCY_KEY_PATTERN}'",
            name="ck_payment_attempts_idempotency_key_format",
        ),
        Index(
            "uq_one_approved_payment_per_order",
            "order_id",
            unique=True,
            postgresql_where=text("outcome = 'approved'"),
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"))
    attempt_number: Mapped[int]
    outcome: Mapped[str] = mapped_column(Text)
    amount_minor: Mapped[int] = mapped_column(BigInteger)
    idempotency_key: Mapped[str] = mapped_column(String(64))
    idempotency_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("idempotency_records.id", ondelete="SET NULL")
    )
    occurred_at: Mapped[datetime]


class Refund(Base):
    __tablename__ = "refunds"
    __table_args__ = (
        UniqueConstraint("order_id", name="uq_refund_order"),
        CheckConstraint(
            in_list("status", ("refund_pending", "refunded")), name="ck_refunds_status"
        ),
        CheckConstraint("amount_minor > 0", name="ck_refunds_amount_positive"),
        CheckConstraint(
            "(status = 'refunded' AND completed_at IS NOT NULL)"
            " OR (status = 'refund_pending' AND completed_at IS NULL)",
            name="ck_refunds_completion_consistency",
        ),
        Index("ix_refunds_status_created", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"))
    amount_minor: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at()
    completed_at: Mapped[datetime | None] = optional_ts()
    reason: Mapped[str | None] = mapped_column(String(200))
