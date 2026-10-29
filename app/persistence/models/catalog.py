"""Catalog and asset tables (ERD §3.2)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base
from app.persistence.models._common import (
    SLUG_PATTERN,
    bool_col,
    created_at,
    updated_at,
    uuid_pk,
)


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_categories_slug"),
        CheckConstraint(f"slug ~ '{SLUG_PATTERN}'", name="ck_categories_slug_format"),
        CheckConstraint("btrim(name) <> ''", name="ck_categories_name_nonblank"),
        CheckConstraint("sort_order >= 0", name="ck_categories_sort_order_nonnegative"),
        CheckConstraint(
            "parent_id IS NULL OR parent_id <> id", name="ck_categories_not_own_parent"
        ),
        Index("ix_categories_parent_sort_order", "parent_id", "sort_order", "id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"))
    slug: Mapped[str] = mapped_column(String(120))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(1000))
    is_active: Mapped[bool] = bool_col()
    is_small_goods: Mapped[bool] = bool_col(default=False)
    sort_order: Mapped[int]
    created_at: Mapped[datetime] = created_at()
    updated_at: Mapped[datetime] = updated_at()


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_products_slug"),
        UniqueConstraint("base_sku", name="uq_products_base_sku"),
        CheckConstraint(f"slug ~ '{SLUG_PATTERN}'", name="ck_products_slug_format"),
        CheckConstraint("btrim(base_sku) <> ''", name="ck_products_base_sku_nonblank"),
        CheckConstraint("btrim(name) <> ''", name="ck_products_name_nonblank"),
        CheckConstraint("btrim(brand) <> ''", name="ck_products_brand_nonblank"),
        CheckConstraint("rating_average BETWEEN 0 AND 5", name="ck_products_rating_average_range"),
        CheckConstraint("rating_count >= 0", name="ck_products_rating_count_nonnegative"),
        Index(
            "ix_products_category_active_created",
            "category_id",
            "is_active",
            text("created_at DESC"),
            text("id ASC"),
        ),
        Index("ix_products_brand_active", "brand", "is_active"),
        Index(
            "ix_products_rating_sort",
            text("(rating_count = 0)"),
            text("rating_average DESC"),
            text("rating_count DESC"),
            text("id ASC"),
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"))
    slug: Mapped[str] = mapped_column(String(160))
    base_sku: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(200))
    brand: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(5000))
    is_active: Mapped[bool] = bool_col()
    is_featured: Mapped[bool] = bool_col()
    is_fictional: Mapped[bool] = bool_col(default=True)
    rating_average: Mapped[Decimal] = mapped_column(Numeric(3, 1), server_default=text("0"))
    rating_count: Mapped[int] = mapped_column(server_default=text("0"))
    created_at: Mapped[datetime] = created_at()
    updated_at: Mapped[datetime] = updated_at()


class ProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("sku", name="uq_product_variants_sku"),
        UniqueConstraint("product_id", "options_key", name="uq_variant_product_options"),
        CheckConstraint("btrim(sku) <> ''", name="ck_product_variants_sku_nonblank"),
        CheckConstraint("unit_price_minor > 0", name="ck_product_variants_price_positive"),
        CheckConstraint("stock_quantity >= 0", name="ck_product_variants_stock_nonnegative"),
        CheckConstraint(
            "jsonb_typeof(options) = 'object'", name="ck_product_variants_options_object"
        ),
        CheckConstraint(
            "btrim(options_key) <> ''", name="ck_product_variants_options_key_nonblank"
        ),
        CheckConstraint(
            "NOT is_default OR options_key = '{}'",
            name="ck_product_variants_default_has_no_options",
        ),
        Index(
            "uq_product_variants_one_default_per_product",
            "product_id",
            unique=True,
            postgresql_where=text("is_default IS TRUE"),
        ),
        Index(
            "ix_product_variants_product_active_price",
            "product_id",
            "is_active",
            "unit_price_minor",
        ),
        Index(
            "ix_product_variants_product_active_stock", "product_id", "is_active", "stock_quantity"
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    sku: Mapped[str] = mapped_column(String(80))
    options: Mapped[dict[str, Any]] = mapped_column(JSONB)
    options_key: Mapped[str] = mapped_column(String(2000))
    unit_price_minor: Mapped[int] = mapped_column(BigInteger)
    stock_quantity: Mapped[int]
    is_active: Mapped[bool] = bool_col()
    is_default: Mapped[bool] = bool_col(default=False)
    created_at: Mapped[datetime] = created_at()
    updated_at: Mapped[datetime] = updated_at()


class ProductImage(Base):
    __tablename__ = "product_images"
    __table_args__ = (
        CheckConstraint("btrim(asset_key) <> ''", name="ck_product_images_asset_key_nonblank"),
        CheckConstraint("btrim(alt_text) <> ''", name="ck_product_images_alt_text_nonblank"),
        CheckConstraint("sort_order >= 0", name="ck_product_images_sort_order_nonnegative"),
        Index(
            "uq_product_images_primary",
            "product_id",
            unique=True,
            postgresql_where=text("is_primary IS TRUE"),
        ),
        Index("ix_product_images_product_sort", "product_id", "sort_order", "id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    asset_key: Mapped[str] = mapped_column(String(240))
    alt_text: Mapped[str] = mapped_column(String(250))
    is_primary: Mapped[bool] = bool_col()
    sort_order: Mapped[int]
    created_at: Mapped[datetime] = created_at()


class ProductSpecification(Base):
    __tablename__ = "product_specifications"
    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="ck_product_specifications_name_nonblank"),
        CheckConstraint("btrim(value) <> ''", name="ck_product_specifications_value_nonblank"),
        CheckConstraint("sort_order >= 0", name="ck_product_specifications_sort_order_nonnegative"),
        Index(
            "uq_product_specifications_product_name",
            "product_id",
            text("lower(btrim(name))"),
            unique=True,
        ),
        Index("ix_product_specifications_product_sort", "product_id", "sort_order", "id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    name: Mapped[str] = mapped_column(String(100))
    value: Mapped[str] = mapped_column(String(500))
    sort_order: Mapped[int]
