"""Addresses, cart and wishlist tables (ERD §3.3)."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CHAR,
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base
from app.persistence.models._common import PHONE_PATTERN, bool_col, created_at, updated_at, uuid_pk


class Address(Base):
    __tablename__ = "addresses"
    __table_args__ = (
        CheckConstraint("btrim(recipient_name) <> ''", name="ck_addresses_recipient_nonblank"),
        CheckConstraint(f"phone ~ '{PHONE_PATTERN}'", name="ck_addresses_phone_format"),
        CheckConstraint("btrim(line1) <> ''", name="ck_addresses_line1_nonblank"),
        CheckConstraint("btrim(city) <> ''", name="ck_addresses_city_nonblank"),
        CheckConstraint("btrim(province) <> ''", name="ck_addresses_province_nonblank"),
        CheckConstraint("postal_code ~ '^[0-9]{4}$'", name="ck_addresses_postal_code_format"),
        CheckConstraint("country_code ~ '^[A-Z]{2}$'", name="ck_addresses_country_code_format"),
        Index("ix_addresses_customer_created", "customer_id", text("created_at DESC")),
        Index(
            "uq_addresses_one_default_per_customer",
            "customer_id",
            unique=True,
            postgresql_where=text("is_default IS TRUE"),
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    recipient_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(16))
    line1: Mapped[str] = mapped_column(String(150))
    line2: Mapped[str | None] = mapped_column(String(150))
    city: Mapped[str] = mapped_column(String(80))
    province: Mapped[str] = mapped_column(String(80))
    postal_code: Mapped[str] = mapped_column(String(4))
    country_code: Mapped[str] = mapped_column(CHAR(2))
    is_default: Mapped[bool] = bool_col()
    created_at: Mapped[datetime] = created_at()
    updated_at: Mapped[datetime] = updated_at()


class Cart(Base):
    __tablename__ = "carts"
    __table_args__ = (
        UniqueConstraint("customer_id", name="uq_cart_customer"),
        Index(
            "uq_carts_locked_by_order",
            "locked_by_order_id",
            unique=True,
            postgresql_where=text("locked_by_order_id IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    applied_coupon_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("coupons.id"))
    shipping_option_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("shipping_options.id"))
    locked_by_order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"))
    created_at: Mapped[datetime] = created_at()
    updated_at: Mapped[datetime] = updated_at()


class CartLine(Base):
    __tablename__ = "cart_lines"
    __table_args__ = (
        UniqueConstraint("cart_id", "variant_id", name="uq_cart_line_variant"),
        CheckConstraint("quantity BETWEEN 1 AND 10", name="ck_cart_lines_quantity_range"),
        CheckConstraint(
            "last_acknowledged_unit_price_minor IS NULL OR last_acknowledged_unit_price_minor >= 0",
            name="ck_cart_lines_acknowledged_price_nonnegative",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    cart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("carts.id"))
    variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product_variants.id"))
    quantity: Mapped[int]
    last_acknowledged_unit_price_minor: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = created_at()
    updated_at: Mapped[datetime] = updated_at()


class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    __table_args__ = (
        UniqueConstraint("customer_id", "product_id", name="uq_wishlist_customer_product"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    created_at: Mapped[datetime] = created_at()
