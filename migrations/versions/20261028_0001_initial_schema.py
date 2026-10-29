"""Create the initial PostgreSQL schema (DATA-001).

Implements the 25 non-R3 tables from DATABASE_SCHEMA_AND_ERD.md v0.9 with explicitly named primary/foreign/unique
constraints, named CHECK constraints (created with ``op.create_check_constraint``), named partial
and supporting indexes. Requires PostgreSQL 16 (native ``gen_random_uuid()``; no extension).

Rollback: ``downgrade`` drops every table created here and therefore destroys all data. It exists
for disposable local/test databases only; recover production from backup instead.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (table, explicit constraint name, SQL condition): names are the ERD §5.1 registry.
CHECK_CONSTRAINTS: list[tuple[str, str, str]] = [
    ("categories", "ck_categories_not_own_parent", "parent_id IS NULL OR parent_id <> id"),
    ("categories", "ck_categories_sort_order_nonnegative", "sort_order >= 0"),
    ("categories", "ck_categories_name_nonblank", "btrim(name) <> ''"),
    ("categories", "ck_categories_slug_format", "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'"),
    ("coupons", "ck_coupons_validity_window", "starts_at < expires_at"),
    (
        "coupons",
        "ck_coupons_maximum_discount_nonnegative",
        "maximum_discount_minor IS NULL OR maximum_discount_minor >= 0",
    ),
    (
        "coupons",
        "ck_coupons_percentage_range",
        "percentage_basis_points IS NULL OR percentage_basis_points BETWEEN 1 AND 10000",
    ),
    (
        "coupons",
        "ck_coupons_global_usage_limit_positive",
        "global_usage_limit IS NULL OR global_usage_limit > 0",
    ),
    ("coupons", "ck_coupons_discount_type", "discount_type IN ('percentage', 'fixed')"),
    ("coupons", "ck_coupons_minimum_order_nonnegative", "minimum_order_minor >= 0"),
    (
        "coupons",
        "ck_coupons_per_customer_usage_limit_positive",
        "per_customer_usage_limit IS NULL OR per_customer_usage_limit > 0",
    ),
    (
        "coupons",
        "ck_coupons_discount_value_matches_type",
        "(discount_type = 'percentage' AND percentage_basis_points IS NOT NULL AND fixed_discount_minor IS NULL) OR (discount_type = 'fixed' AND fixed_discount_minor IS NOT NULL AND percentage_basis_points IS NULL)",
    ),
    ("coupons", "ck_coupons_code_format", "code ~ '^[A-Z0-9_-]{3,20}$'"),
    (
        "coupons",
        "ck_coupons_eligibility_rule",
        "eligibility_rule IN ('all_customers', 'returning_customer')",
    ),
    (
        "coupons",
        "ck_coupons_fixed_discount_positive",
        "fixed_discount_minor IS NULL OR fixed_discount_minor > 0",
    ),
    ("login_throttle_state", "ck_login_throttle_failures_nonnegative", "consecutive_failures >= 0"),
    ("shipping_options", "ck_shipping_options_code_format", "code ~ '^[a-z0-9_-]{1,30}$'"),
    ("shipping_options", "ck_shipping_options_fee_nonnegative", "base_fee_minor >= 0"),
    ("shipping_options", "ck_shipping_options_sort_order_nonnegative", "sort_order >= 0"),
    ("users", "ck_users_name_nonblank", "btrim(name) <> ''"),
    ("users", "ck_users_phone_format", "phone IS NULL OR phone ~ '^\\+?[0-9]{7,15}$'"),
    ("users", "ck_users_email_normalized", "email = lower(btrim(email))"),
    ("users", "ck_users_role", "role IN ('customer', 'admin')"),
    ("addresses", "ck_addresses_province_nonblank", "btrim(province) <> ''"),
    ("addresses", "ck_addresses_recipient_nonblank", "btrim(recipient_name) <> ''"),
    ("addresses", "ck_addresses_postal_code_format", "postal_code ~ '^[0-9]{4}$'"),
    ("addresses", "ck_addresses_line1_nonblank", "btrim(line1) <> ''"),
    ("addresses", "ck_addresses_country_code_format", "country_code ~ '^[A-Z]{2}$'"),
    ("addresses", "ck_addresses_city_nonblank", "btrim(city) <> ''"),
    ("addresses", "ck_addresses_phone_format", "phone ~ '^\\+?[0-9]{7,15}$'"),
    ("audit_events", "ck_audit_events_action_nonblank", "btrim(action) <> ''"),
    ("audit_events", "ck_audit_events_actor_role", "actor_role IN ('customer', 'admin', 'system')"),
    ("audit_events", "ck_audit_events_entity_type_nonblank", "btrim(entity_type) <> ''"),
    ("auth_sessions", "ck_auth_sessions_expiry_after_issue", "expires_at > issued_at"),
    (
        "auth_sessions",
        "ck_auth_sessions_csrf_token_hash_format",
        "csrf_token_hash ~ '^[0-9a-f]{64}$'",
    ),
    (
        "orders",
        "ck_orders_money_nonnegative",
        "subtotal_minor >= 0 AND discount_minor >= 0 AND shipping_fee_minor >= 0 AND total_minor >= 0",
    ),
    ("orders", "ck_orders_reservation_after_placement", "reservation_deadline > placed_at"),
    ("orders", "ck_orders_number_format", "order_number ~ '^NC-[0-9]{8}-[0-9]{6}$'"),
    ("orders", "ck_orders_discount_not_above_subtotal", "discount_minor <= subtotal_minor"),
    (
        "orders",
        "ck_orders_status",
        "status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')",
    ),
    (
        "orders",
        "ck_orders_total_arithmetic",
        "total_minor = subtotal_minor - discount_minor + shipping_fee_minor",
    ),
    ("products", "ck_products_slug_format", "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'"),
    ("products", "ck_products_name_nonblank", "btrim(name) <> ''"),
    ("products", "ck_products_rating_average_range", "rating_average BETWEEN 0 AND 5"),
    ("products", "ck_products_brand_nonblank", "btrim(brand) <> ''"),
    ("products", "ck_products_base_sku_nonblank", "btrim(base_sku) <> ''"),
    ("products", "ck_products_rating_count_nonnegative", "rating_count >= 0"),
    (
        "coupon_usages",
        "ck_coupon_usages_finalization_consistency",
        "(usage_state = 'reserved' AND finalized_at IS NULL) OR (usage_state IN ('consumed', 'released') AND finalized_at IS NOT NULL)",
    ),
    (
        "coupon_usages",
        "ck_coupon_usages_state",
        "usage_state IN ('reserved', 'consumed', 'released')",
    ),
    ("idempotency_records", "ck_idempotency_records_scope_nonblank", "btrim(scope) <> ''"),
    (
        "idempotency_records",
        "ck_idempotency_records_response_status",
        "response_status BETWEEN 100 AND 599",
    ),
    (
        "idempotency_records",
        "ck_idempotency_records_retention",
        "expires_at >= created_at + interval '24 hours'",
    ),
    (
        "idempotency_records",
        "ck_idempotency_records_key_format",
        "key_value ~ '^[A-Za-z0-9_-]{8,64}$'",
    ),
    (
        "idempotency_records",
        "ck_idempotency_records_fingerprint_format",
        "request_fingerprint ~ '^[0-9a-f]{64}$'",
    ),
    (
        "order_address_snapshots",
        "ck_order_address_snapshots_postal_code_format",
        "postal_code ~ '^[0-9]{4}$'",
    ),
    (
        "order_status_history",
        "ck_order_status_history_to_status",
        "to_status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')",
    ),
    (
        "order_status_history",
        "ck_order_status_history_from_status",
        "from_status IS NULL OR from_status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')",
    ),
    (
        "order_status_history",
        "ck_order_status_history_actor_type",
        "actor_type IN ('customer', 'admin', 'system')",
    ),
    (
        "order_status_history",
        "ck_order_status_history_admin_cancel_reason",
        "NOT (actor_type = 'admin' AND to_status = 'cancelled') OR (reason IS NOT NULL AND char_length(btrim(reason)) BETWEEN 1 AND 200)",
    ),
    ("product_images", "ck_product_images_asset_key_nonblank", "btrim(asset_key) <> ''"),
    ("product_images", "ck_product_images_alt_text_nonblank", "btrim(alt_text) <> ''"),
    ("product_images", "ck_product_images_sort_order_nonnegative", "sort_order >= 0"),
    ("product_specifications", "ck_product_specifications_name_nonblank", "btrim(name) <> ''"),
    (
        "product_specifications",
        "ck_product_specifications_sort_order_nonnegative",
        "sort_order >= 0",
    ),
    ("product_specifications", "ck_product_specifications_value_nonblank", "btrim(value) <> ''"),
    ("product_variants", "ck_product_variants_sku_nonblank", "btrim(sku) <> ''"),
    ("product_variants", "ck_product_variants_price_positive", "unit_price_minor > 0"),
    ("product_variants", "ck_product_variants_options_object", "jsonb_typeof(options) = 'object'"),
    ("product_variants", "ck_product_variants_options_key_nonblank", "btrim(options_key) <> ''"),
    ("product_variants", "ck_product_variants_stock_nonnegative", "stock_quantity >= 0"),
    (
        "product_variants",
        "ck_product_variants_default_has_no_options",
        "NOT is_default OR options_key = '{}'",
    ),
    ("refunds", "ck_refunds_amount_positive", "amount_minor > 0"),
    (
        "refunds",
        "ck_refunds_completion_consistency",
        "(status = 'refunded' AND completed_at IS NOT NULL) OR (status = 'refund_pending' AND completed_at IS NULL)",
    ),
    ("refunds", "ck_refunds_status", "status IN ('refund_pending', 'refunded')"),
    ("reviews", "ck_reviews_rating_range", "rating BETWEEN 1 AND 5"),
    ("reviews", "ck_reviews_comment_length", "comment IS NULL OR char_length(comment) <= 1000"),
    (
        "reviews",
        "ck_reviews_hidden_metadata_consistency",
        "(NOT is_hidden AND hidden_by_user_id IS NULL AND hidden_at IS NULL) OR (is_hidden AND hidden_by_user_id IS NOT NULL AND hidden_at IS NOT NULL)",
    ),
    ("cart_lines", "ck_cart_lines_quantity_range", "quantity BETWEEN 1 AND 10"),
    (
        "cart_lines",
        "ck_cart_lines_acknowledged_price_nonnegative",
        "last_acknowledged_unit_price_minor IS NULL OR last_acknowledged_unit_price_minor >= 0",
    ),
    ("order_items", "ck_order_items_line_total", "line_total_minor = unit_price_minor * quantity"),
    ("order_items", "ck_order_items_unit_price_positive", "unit_price_minor > 0"),
    ("order_items", "ck_order_items_product_name_nonblank", "btrim(product_name_snapshot) <> ''"),
    ("order_items", "ck_order_items_quantity_positive", "quantity > 0"),
    ("payment_attempts", "ck_payment_attempts_attempt_number_positive", "attempt_number > 0"),
    ("payment_attempts", "ck_payment_attempts_amount_positive", "amount_minor > 0"),
    (
        "payment_attempts",
        "ck_payment_attempts_outcome",
        "outcome IN ('approved', 'declined', 'timed_out', 'error')",
    ),
    (
        "payment_attempts",
        "ck_payment_attempts_idempotency_key_format",
        "idempotency_key ~ '^[A-Za-z0-9_-]{8,64}$'",
    ),
    ("inventory_movements", "ck_inventory_movements_delta_nonzero", "delta_quantity <> 0"),
    (
        "inventory_movements",
        "ck_inventory_movements_reason_code",
        "reason_code IN ('initial_stock', 'order_placed', 'order_cancelled', 'reservation_expired', 'admin_adjustment')",
    ),
    (
        "inventory_movements",
        "ck_inventory_movements_operation_key_nonblank",
        "btrim(operation_key) <> ''",
    ),
    (
        "inventory_movements",
        "ck_inventory_movements_admin_reason",
        "reason_code <> 'admin_adjustment' OR (reason_text IS NOT NULL AND char_length(btrim(reason_text)) BETWEEN 1 AND 200)",
    ),
]


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=True),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_small_goods", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["categories.id"], name=op.f("fk_categories_parent_id_categories")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
        sa.UniqueConstraint("slug", name="uq_categories_slug"),
    )
    op.create_index(
        "ix_categories_parent_sort_order",
        "categories",
        ["parent_id", "sort_order", "id"],
        unique=False,
    )
    op.create_table(
        "coupons",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("discount_type", sa.Text(), nullable=False),
        sa.Column("percentage_basis_points", sa.Integer(), nullable=True),
        sa.Column("fixed_discount_minor", sa.BigInteger(), nullable=True),
        sa.Column("maximum_discount_minor", sa.BigInteger(), nullable=True),
        sa.Column("minimum_order_minor", sa.BigInteger(), nullable=False),
        sa.Column("minimum_is_exclusive", sa.Boolean(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("global_usage_limit", sa.Integer(), nullable=True),
        sa.Column("per_customer_usage_limit", sa.Integer(), nullable=True),
        sa.Column("eligibility_rule", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_coupons")),
        sa.UniqueConstraint("code", name="uq_coupon_code"),
    )
    op.create_table(
        "login_throttle_state",
        sa.Column("email_key", sa.String(length=254), nullable=False),
        sa.Column(
            "consecutive_failures", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("email_key", name=op.f("pk_login_throttle_state")),
    )
    op.create_table(
        "shipping_options",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("display_name", sa.String(length=80), nullable=False),
        sa.Column("base_fee_minor", sa.BigInteger(), nullable=False),
        sa.Column("delivery_estimate", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_shipping_options")),
        sa.UniqueConstraint("code", name="uq_shipping_options_code"),
    )
    op.create_index(
        "ix_shipping_options_active_sort",
        "shipping_options",
        ["is_active", "sort_order", "id"],
        unique=False,
    )
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("phone", sa.String(length=16), nullable=True),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "addresses",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("recipient_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=16), nullable=False),
        sa.Column("line1", sa.String(length=150), nullable=False),
        sa.Column("line2", sa.String(length=150), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("province", sa.String(length=80), nullable=False),
        sa.Column("postal_code", sa.String(length=4), nullable=False),
        sa.Column("country_code", sa.CHAR(length=2), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["users.id"], name=op.f("fk_addresses_customer_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_addresses")),
    )
    op.create_index(
        "ix_addresses_customer_created",
        "addresses",
        ["customer_id", sa.literal_column("created_at DESC")],
        unique=False,
    )
    op.create_index(
        "uq_addresses_one_default_per_customer",
        "addresses",
        ["customer_id"],
        unique=True,
        postgresql_where=sa.text("is_default IS TRUE"),
    )
    op.create_table(
        "audit_events",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("actor_user_id", sa.UUID(), nullable=True),
        sa.Column("actor_role", sa.Text(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=True),
        sa.Column("before_summary", postgresql.JSONB(astext_type=Text()), nullable=True),
        sa.Column("after_summary", postgresql.JSONB(astext_type=Text()), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_user_id"], ["users.id"], name=op.f("fk_audit_events_actor_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_events")),
    )
    op.create_index(
        "ix_audit_events_action_time",
        "audit_events",
        ["action", sa.literal_column("occurred_at DESC")],
        unique=False,
    )
    op.create_index(
        "ix_audit_events_actor_time",
        "audit_events",
        ["actor_user_id", sa.literal_column("occurred_at DESC")],
        unique=False,
    )
    op.create_index(
        "ix_audit_events_entity_time",
        "audit_events",
        ["entity_type", "entity_id", sa.literal_column("occurred_at DESC")],
        unique=False,
    )
    op.create_index(
        "ix_audit_events_occurred_at",
        "audit_events",
        [sa.literal_column("occurred_at DESC")],
        unique=False,
    )
    op.create_table(
        "auth_sessions",
        sa.Column("jti", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.String(length=100), nullable=True),
        sa.Column("csrf_token_hash", sa.CHAR(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_auth_sessions_user_id_users")
        ),
        sa.PrimaryKeyConstraint("jti", name=op.f("pk_auth_sessions")),
    )
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"], unique=False)
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"], unique=False)
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("order_number", sa.String(length=18), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("subtotal_minor", sa.BigInteger(), nullable=False),
        sa.Column("discount_minor", sa.BigInteger(), nullable=False),
        sa.Column("shipping_fee_minor", sa.BigInteger(), nullable=False),
        sa.Column("total_minor", sa.BigInteger(), nullable=False),
        sa.Column("coupon_code_snapshot", sa.String(length=20), nullable=True),
        sa.Column("shipping_option_id", sa.UUID(), nullable=False),
        sa.Column("shipping_option_code_snapshot", sa.String(length=30), nullable=False),
        sa.Column("shipping_option_name_snapshot", sa.String(length=80), nullable=False),
        sa.Column("reservation_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("placed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["users.id"], name=op.f("fk_orders_customer_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["shipping_option_id"],
            ["shipping_options.id"],
            name=op.f("fk_orders_shipping_option_id_shipping_options"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders")),
        sa.UniqueConstraint("order_number", name="uq_order_number"),
    )
    op.create_index(
        "ix_orders_customer_placed_at",
        "orders",
        ["customer_id", sa.literal_column("placed_at DESC")],
        unique=False,
    )
    op.create_index(
        "ix_orders_status_deadline", "orders", ["status", "reservation_deadline"], unique=False
    )
    op.create_index(
        "uq_one_pending_order_per_customer",
        "orders",
        ["customer_id"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("base_sku", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("brand", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=5000), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("is_fictional", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "rating_average",
            sa.Numeric(precision=3, scale=1),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("rating_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"], name=op.f("fk_products_category_id_categories")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_products")),
        sa.UniqueConstraint("base_sku", name="uq_products_base_sku"),
        sa.UniqueConstraint("slug", name="uq_products_slug"),
    )
    op.create_index("ix_products_brand_active", "products", ["brand", "is_active"], unique=False)
    op.create_index(
        "ix_products_category_active_created",
        "products",
        [
            "category_id",
            "is_active",
            sa.literal_column("created_at DESC"),
            sa.literal_column("id ASC"),
        ],
        unique=False,
    )
    op.create_index(
        "ix_products_rating_sort",
        "products",
        [
            sa.literal_column("(rating_count = 0)"),
            sa.literal_column("rating_average DESC"),
            sa.literal_column("rating_count DESC"),
            sa.literal_column("id ASC"),
        ],
        unique=False,
    )
    op.create_table(
        "carts",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("applied_coupon_id", sa.UUID(), nullable=True),
        sa.Column("shipping_option_id", sa.UUID(), nullable=False),
        sa.Column("locked_by_order_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["applied_coupon_id"], ["coupons.id"], name=op.f("fk_carts_applied_coupon_id_coupons")
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["users.id"], name=op.f("fk_carts_customer_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["locked_by_order_id"], ["orders.id"], name=op.f("fk_carts_locked_by_order_id_orders")
        ),
        sa.ForeignKeyConstraint(
            ["shipping_option_id"],
            ["shipping_options.id"],
            name=op.f("fk_carts_shipping_option_id_shipping_options"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carts")),
        sa.UniqueConstraint("customer_id", name="uq_cart_customer"),
    )
    op.create_index(
        "uq_carts_locked_by_order",
        "carts",
        ["locked_by_order_id"],
        unique=True,
        postgresql_where=sa.text("locked_by_order_id IS NOT NULL"),
    )
    op.create_table(
        "coupon_usages",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("coupon_id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("usage_state", sa.Text(), nullable=False),
        sa.Column("reserved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["coupon_id"], ["coupons.id"], name=op.f("fk_coupon_usages_coupon_id_coupons")
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["users.id"], name=op.f("fk_coupon_usages_customer_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_coupon_usages_order_id_orders")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_coupon_usages")),
        sa.UniqueConstraint("order_id", name="uq_coupon_usage_order"),
    )
    op.create_index(
        "ix_coupon_usages_coupon_state", "coupon_usages", ["coupon_id", "usage_state"], unique=False
    )
    op.create_index(
        "ix_coupon_usages_customer_coupon_state",
        "coupon_usages",
        ["customer_id", "coupon_id", "usage_state"],
        unique=False,
    )
    op.create_table(
        "idempotency_records",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("scope", sa.String(length=100), nullable=False),
        sa.Column("key_value", sa.String(length=64), nullable=False),
        sa.Column("request_fingerprint", sa.CHAR(length=64), nullable=False),
        sa.Column("response_status", sa.SmallInteger(), nullable=False),
        sa.Column("response_body", postgresql.JSONB(astext_type=Text()), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["users.id"], name=op.f("fk_idempotency_records_customer_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_idempotency_records_order_id_orders")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_idempotency_records")),
        sa.UniqueConstraint("customer_id", "scope", "key_value", name="uq_idempotency_scope_key"),
    )
    op.create_index(
        "ix_idempotency_records_expires_at", "idempotency_records", ["expires_at"], unique=False
    )
    op.create_table(
        "order_address_snapshots",
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("recipient_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=16), nullable=False),
        sa.Column("line1", sa.String(length=150), nullable=False),
        sa.Column("line2", sa.String(length=150), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("province", sa.String(length=80), nullable=False),
        sa.Column("postal_code", sa.String(length=4), nullable=False),
        sa.Column("country_code", sa.CHAR(length=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_order_address_snapshots_order_id_orders")
        ),
        sa.PrimaryKeyConstraint("order_id", name=op.f("pk_order_address_snapshots")),
    )
    op.create_table(
        "order_status_history",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("from_status", sa.Text(), nullable=True),
        sa.Column("to_status", sa.Text(), nullable=False),
        sa.Column("actor_type", sa.Text(), nullable=False),
        sa.Column("actor_user_id", sa.UUID(), nullable=True),
        sa.Column("reason", sa.String(length=200), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_order_status_history_actor_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_order_status_history_order_id_orders")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_status_history")),
    )
    op.create_index(
        "ix_order_status_history_order_time",
        "order_status_history",
        ["order_id", "occurred_at"],
        unique=False,
    )
    op.create_table(
        "product_images",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("asset_key", sa.String(length=240), nullable=False),
        sa.Column("alt_text", sa.String(length=250), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name=op.f("fk_product_images_product_id_products")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_images")),
    )
    op.create_index(
        "ix_product_images_product_sort",
        "product_images",
        ["product_id", "sort_order", "id"],
        unique=False,
    )
    op.create_index(
        "uq_product_images_primary",
        "product_images",
        ["product_id"],
        unique=True,
        postgresql_where=sa.text("is_primary IS TRUE"),
    )
    op.create_table(
        "product_specifications",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_product_specifications_product_id_products"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_specifications")),
    )
    op.create_index(
        "ix_product_specifications_product_sort",
        "product_specifications",
        ["product_id", "sort_order", "id"],
        unique=False,
    )
    op.create_index(
        "uq_product_specifications_product_name",
        "product_specifications",
        ["product_id", sa.literal_column("lower(btrim(name))")],
        unique=True,
    )
    op.create_table(
        "product_variants",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("sku", sa.String(length=80), nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=Text()), nullable=False),
        sa.Column("options_key", sa.String(length=2000), nullable=False),
        sa.Column("unit_price_minor", sa.BigInteger(), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name=op.f("fk_product_variants_product_id_products")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_variants")),
        sa.UniqueConstraint("product_id", "options_key", name="uq_variant_product_options"),
        sa.UniqueConstraint("sku", name="uq_product_variants_sku"),
    )
    op.create_index(
        "ix_product_variants_product_active_price",
        "product_variants",
        ["product_id", "is_active", "unit_price_minor"],
        unique=False,
    )
    op.create_index(
        "ix_product_variants_product_active_stock",
        "product_variants",
        ["product_id", "is_active", "stock_quantity"],
        unique=False,
    )
    op.create_index(
        "uq_product_variants_one_default_per_product",
        "product_variants",
        ["product_id"],
        unique=True,
        postgresql_where=sa.text("is_default IS TRUE"),
    )
    op.create_table(
        "refunds",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reason", sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_refunds_order_id_orders")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refunds")),
        sa.UniqueConstraint("order_id", name="uq_refund_order"),
    )
    op.create_index("ix_refunds_status_created", "refunds", ["status", "created_at"], unique=False)
    op.create_table(
        "reviews",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("verified_order_id", sa.UUID(), nullable=False),
        sa.Column("rating", sa.SmallInteger(), nullable=False),
        sa.Column("comment", sa.String(length=1000), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("hidden_by_user_id", sa.UUID(), nullable=True),
        sa.Column("hidden_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["users.id"], name=op.f("fk_reviews_customer_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["hidden_by_user_id"], ["users.id"], name=op.f("fk_reviews_hidden_by_user_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name=op.f("fk_reviews_product_id_products")
        ),
        sa.ForeignKeyConstraint(
            ["verified_order_id"], ["orders.id"], name=op.f("fk_reviews_verified_order_id_orders")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reviews")),
        sa.UniqueConstraint("customer_id", "product_id", name="uq_review_customer_product"),
    )
    op.create_index(
        "ix_reviews_product_created",
        "reviews",
        ["product_id", "is_hidden", sa.literal_column("created_at DESC")],
        unique=False,
    )
    op.create_table(
        "wishlist_items",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["users.id"], name=op.f("fk_wishlist_items_customer_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name=op.f("fk_wishlist_items_product_id_products")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_wishlist_items")),
        sa.UniqueConstraint("customer_id", "product_id", name="uq_wishlist_customer_product"),
    )
    op.create_table(
        "cart_lines",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("cart_id", sa.UUID(), nullable=False),
        sa.Column("variant_id", sa.UUID(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("last_acknowledged_unit_price_minor", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["cart_id"], ["carts.id"], name=op.f("fk_cart_lines_cart_id_carts")
        ),
        sa.ForeignKeyConstraint(
            ["variant_id"],
            ["product_variants.id"],
            name=op.f("fk_cart_lines_variant_id_product_variants"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cart_lines")),
        sa.UniqueConstraint("cart_id", "variant_id", name="uq_cart_line_variant"),
    )
    op.create_table(
        "order_items",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("variant_id", sa.UUID(), nullable=False),
        sa.Column("product_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("variant_description_snapshot", sa.String(length=1000), nullable=False),
        sa.Column("sku_snapshot", sa.String(length=80), nullable=False),
        sa.Column("image_asset_key_snapshot", sa.String(length=240), nullable=False),
        sa.Column("unit_price_minor", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("line_total_minor", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_order_items_order_id_orders")
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_order_items_product_id_products"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["variant_id"],
            ["product_variants.id"],
            name=op.f("fk_order_items_variant_id_product_variants"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_items")),
        sa.UniqueConstraint("order_id", "variant_id", name="uq_order_variant_line"),
    )
    op.create_table(
        "payment_attempts",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=64), nullable=False),
        sa.Column("idempotency_record_id", sa.UUID(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["idempotency_record_id"],
            ["idempotency_records.id"],
            name=op.f("fk_payment_attempts_idempotency_record_id_idempotency_records"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_payment_attempts_order_id_orders")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_payment_attempts")),
        sa.UniqueConstraint("idempotency_record_id", name="uq_payment_attempts_idempotency_record"),
        sa.UniqueConstraint("order_id", "attempt_number", name="uq_payment_attempt_number"),
        sa.UniqueConstraint("order_id", "idempotency_key", name="uq_payment_idempotency_key"),
    )
    op.create_index(
        "uq_one_approved_payment_per_order",
        "payment_attempts",
        ["order_id"],
        unique=True,
        postgresql_where=sa.text("outcome = 'approved'"),
    )
    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("variant_id", sa.UUID(), nullable=False),
        sa.Column("delta_quantity", sa.Integer(), nullable=False),
        sa.Column("reason_code", sa.Text(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=True),
        sa.Column("order_item_id", sa.UUID(), nullable=True),
        sa.Column("reference_type", sa.Text(), nullable=False),
        sa.Column("reference_id", sa.UUID(), nullable=True),
        sa.Column("operation_key", sa.String(length=160), nullable=False),
        sa.Column("actor_user_id", sa.UUID(), nullable=True),
        sa.Column("reason_text", sa.String(length=200), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_user_id"], ["users.id"], name=op.f("fk_inventory_movements_actor_user_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_inventory_movements_order_id_orders")
        ),
        sa.ForeignKeyConstraint(
            ["order_item_id"],
            ["order_items.id"],
            name=op.f("fk_inventory_movements_order_item_id_order_items"),
        ),
        sa.ForeignKeyConstraint(
            ["variant_id"],
            ["product_variants.id"],
            name=op.f("fk_inventory_movements_variant_id_product_variants"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory_movements")),
        sa.UniqueConstraint("operation_key", name="uq_inventory_operation_key"),
    )
    op.create_index(
        "ix_inventory_movements_reference",
        "inventory_movements",
        ["reference_type", "reference_id"],
        unique=False,
    )
    op.create_index(
        "ix_inventory_movements_variant_time",
        "inventory_movements",
        ["variant_id", "occurred_at"],
        unique=False,
    )
    for table_name, constraint_name, condition in CHECK_CONSTRAINTS:
        op.create_check_constraint(constraint_name, table_name, condition)


def downgrade() -> None:
    op.drop_table("inventory_movements")
    op.drop_table("payment_attempts")
    op.drop_table("order_items")
    op.drop_table("cart_lines")
    op.drop_table("wishlist_items")
    op.drop_table("reviews")
    op.drop_table("refunds")
    op.drop_table("product_variants")
    op.drop_table("product_specifications")
    op.drop_table("product_images")
    op.drop_table("order_status_history")
    op.drop_table("order_address_snapshots")
    op.drop_table("idempotency_records")
    op.drop_table("coupon_usages")
    op.drop_table("carts")
    op.drop_table("products")
    op.drop_table("orders")
    op.drop_table("auth_sessions")
    op.drop_table("audit_events")
    op.drop_table("addresses")
    op.drop_table("users")
    op.drop_table("shipping_options")
    op.drop_table("login_throttle_state")
    op.drop_table("coupons")
    op.drop_table("categories")
