"""Constraint enforcement against real PostgreSQL 16 (each test rolls back its own work)."""

import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy import Connection, insert, select, text, update
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.persistence.base import Base
from app.persistence.models import (
    Address,
    Cart,
    CartLine,
    Category,
    Coupon,
    CouponUsage,
    IdempotencyRecord,
    InventoryMovement,
    Order,
    OrderItem,
    PaymentAttempt,
    Product,
    ProductImage,
    ProductVariant,
    Refund,
    Review,
    ShippingOption,
    User,
    WishlistItem,
)

NOW = datetime(2026, 10, 28, 12, 0, tzinfo=UTC)
Factory = Callable[..., uuid.UUID]


def _insert(conn: Connection, model: type[Base], **values: Any) -> uuid.UUID:
    pk = sa_inspect(model).primary_key[0]
    result = conn.execute(insert(model).values(**values).returning(pk))
    return result.scalar_one()  # type: ignore[no-any-return]


def expect_violation(conn: Connection, constraint: str | tuple[str, ...], stmt: Any) -> None:
    """The statement must fail on a named constraint/index (any one of ``constraint``)."""
    names = (constraint,) if isinstance(constraint, str) else constraint
    with pytest.raises(IntegrityError) as info, conn.begin_nested():
        conn.execute(stmt)
    assert any(n in str(info.value.orig) for n in names), str(info.value.orig)


class Seed:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn
        self.n = 0

    def uid(self) -> str:
        self.n += 1
        return f"{self.n:04d}"

    def user(self, **kw: Any) -> uuid.UUID:
        i = self.uid()
        base: dict[str, Any] = {
            "name": "Test User",
            "email": f"user{i}@example.test",
            "password_hash": "x",
            "role": "customer",
        }
        return _insert(self.conn, User, **{**base, **kw})

    def category(self, **kw: Any) -> uuid.UUID:
        i = self.uid()
        base: dict[str, Any] = {
            "slug": f"cat-{i}",
            "name": "Cat",
            "is_active": True,
            "sort_order": 0,
        }
        return _insert(self.conn, Category, **{**base, **kw})

    def product(self, category_id: uuid.UUID | None = None, **kw: Any) -> uuid.UUID:
        i = self.uid()
        base: dict[str, Any] = {
            "category_id": category_id or self.category(),
            "slug": f"prod-{i}",
            "base_sku": f"SKU-{i}",
            "name": "Prod",
            "brand": "Brand",
            "description": "d",
            "is_active": True,
            "is_featured": False,
        }
        return _insert(self.conn, Product, **{**base, **kw})

    def variant(self, product_id: uuid.UUID | None = None, **kw: Any) -> uuid.UUID:
        i = self.uid()
        base: dict[str, Any] = {
            "product_id": product_id or self.product(),
            "sku": f"VSKU-{i}",
            "options": {},
            "options_key": "{}",
            "unit_price_minor": 10000,
            "stock_quantity": 5,
            "is_active": True,
        }
        return _insert(self.conn, ProductVariant, **{**base, **kw})

    def shipping(self, **kw: Any) -> uuid.UUID:
        i = self.uid()
        base: dict[str, Any] = {
            "code": f"ship-{i}",
            "display_name": "Ship",
            "base_fee_minor": 6000,
            "delivery_estimate": "3 days",
            "is_active": True,
            "sort_order": 0,
        }
        return _insert(self.conn, ShippingOption, **{**base, **kw})

    def order(self, customer_id: uuid.UUID | None = None, **kw: Any) -> uuid.UUID:
        i = self.uid()
        base: dict[str, Any] = {
            "order_number": f"NC-20261028-{int(i):06d}",
            "customer_id": customer_id or self.user(),
            "status": "confirmed",
            "subtotal_minor": 10000,
            "discount_minor": 1000,
            "shipping_fee_minor": 6000,
            "total_minor": 15000,
            "shipping_option_id": self.shipping(),
            "shipping_option_code_snapshot": "standard",
            "shipping_option_name_snapshot": "Standard",
            "reservation_deadline": NOW + timedelta(minutes=30),
            "placed_at": NOW,
        }
        return _insert(self.conn, Order, **{**base, **kw})

    def idem(self, customer_id: uuid.UUID, **kw: Any) -> uuid.UUID:
        i = self.uid()
        base: dict[str, Any] = {
            "customer_id": customer_id,
            "scope": "place_order",
            "key_value": f"key-{i}-abcd",
            "request_fingerprint": "a" * 64,
            "response_status": 201,
            "response_body": {"ok": True},
            "created_at": NOW,
            "expires_at": NOW + timedelta(hours=24),
        }
        return _insert(self.conn, IdempotencyRecord, **{**base, **kw})

    def payment(self, order_id: uuid.UUID, **kw: Any) -> uuid.UUID:
        i = self.uid()
        base: dict[str, Any] = {
            "order_id": order_id,
            "attempt_number": 1,
            "outcome": "declined",
            "amount_minor": 15000,
            "idempotency_key": f"pay-{i}-abcd",
            "occurred_at": NOW,
        }
        return _insert(self.conn, PaymentAttempt, **{**base, **kw})


@pytest.fixture
def seed(conn: Connection) -> Seed:
    return Seed(conn)


def test_email_unique_and_normalized(seed: Seed, conn: Connection) -> None:
    seed.user(email="a@example.test")
    expect_violation(
        conn,
        "uq_users_email",
        insert(User).values(name="B", email="a@example.test", password_hash="x", role="customer"),
    )
    expect_violation(
        conn,
        "ck_users_email_normalized",
        insert(User).values(
            name="B", email="Upper@Example.test", password_hash="x", role="customer"
        ),
    )
    expect_violation(
        conn,
        "ck_users_role",
        insert(User).values(name="B", email="b@example.test", password_hash="x", role="superuser"),
    )
    expect_violation(
        conn,
        "ck_users_phone_format",
        insert(User).values(
            name="B", email="c@example.test", password_hash="x", role="customer", phone="12"
        ),
    )


def test_foreign_keys_reject_orphans(conn: Connection) -> None:
    expect_violation(
        conn,
        "fk_products_category_id_categories",
        insert(Product).values(
            category_id=uuid.uuid4(),
            slug="x",
            base_sku="X",
            name="n",
            brand="b",
            description="d",
            is_active=True,
            is_featured=False,
        ),
    )


def test_sku_uniqueness_and_variant_option_uniqueness(seed: Seed, conn: Connection) -> None:
    pid = seed.product(base_sku="BASE-1")
    expect_violation(
        conn,
        "uq_products_base_sku",
        insert(Product).values(
            category_id=seed.category(),
            slug="other",
            base_sku="BASE-1",
            name="n",
            brand="b",
            description="d",
            is_active=True,
            is_featured=False,
        ),
    )
    seed.variant(pid, sku="V-1", options={"size": "M"}, options_key='{"size":"M"}')
    expect_violation(
        conn,
        "uq_product_variants_sku",
        insert(ProductVariant).values(
            product_id=pid,
            sku="V-1",
            options={},
            options_key="{}",
            unit_price_minor=1,
            stock_quantity=0,
            is_active=True,
        ),
    )
    expect_violation(
        conn,
        "uq_variant_product_options",
        insert(ProductVariant).values(
            product_id=pid,
            sku="V-2",
            options={"size": "M"},
            options_key='{"size":"M"}',
            unit_price_minor=1,
            stock_quantity=0,
            is_active=True,
        ),
    )


def test_stock_and_price_bounds(seed: Seed, conn: Connection) -> None:
    vid = seed.variant(stock_quantity=1)
    expect_violation(
        conn,
        "ck_product_variants_stock_nonnegative",
        update(ProductVariant).where(ProductVariant.id == vid).values(stock_quantity=0 - 1),
    )
    # Conditional decrement used by TX-1 cannot drive stock below zero.
    result = conn.execute(
        text(
            "UPDATE product_variants SET stock_quantity = stock_quantity - 2"
            " WHERE id = :id AND stock_quantity >= 2"
        ),
        {"id": vid},
    )
    assert result.rowcount == 0
    expect_violation(
        conn,
        "ck_product_variants_price_positive",
        update(ProductVariant).where(ProductVariant.id == vid).values(unit_price_minor=0),
    )
    seed.variant(stock_quantity=0)  # zero stock is valid


def test_single_default_variant_and_default_has_no_options(seed: Seed, conn: Connection) -> None:
    pid = seed.product()
    seed.variant(pid, is_default=True)
    expect_violation(
        conn,
        # Both fire for a second no-options default; the unique (product, options_key) wins first.
        ("uq_product_variants_one_default_per_product", "uq_variant_product_options"),
        insert(ProductVariant).values(
            product_id=pid,
            sku="D2",
            options={},
            options_key="{}",
            unit_price_minor=1,
            stock_quantity=0,
            is_active=True,
            is_default=True,
        ),
    )
    expect_violation(
        conn,
        "ck_product_variants_default_has_no_options",
        insert(ProductVariant).values(
            product_id=seed.product(),
            sku="D3",
            options={"a": "b"},
            options_key='{"a":"b"}',
            unit_price_minor=1,
            stock_quantity=0,
            is_active=True,
            is_default=True,
        ),
    )


def test_one_primary_image_per_product(seed: Seed, conn: Connection) -> None:
    pid = seed.product()
    cols: dict[str, Any] = {
        "product_id": pid,
        "asset_key": "a",
        "alt_text": "t",
        "is_primary": True,
        "sort_order": 0,
    }
    _insert(conn, ProductImage, **cols)
    _insert(conn, ProductImage, **{**cols, "is_primary": False})
    expect_violation(conn, "uq_product_images_primary", insert(ProductImage).values(**cols))


def test_category_cannot_be_its_own_parent(seed: Seed, conn: Connection) -> None:
    cid = seed.category()
    expect_violation(
        conn,
        "ck_categories_not_own_parent",
        update(Category).where(Category.id == cid).values(parent_id=cid),
    )


def test_cart_constraints(seed: Seed, conn: Connection) -> None:
    user = seed.user()
    ship = seed.shipping()
    cart = _insert(conn, Cart, customer_id=user, shipping_option_id=ship)
    expect_violation(
        conn,
        "uq_cart_customer",
        insert(Cart).values(customer_id=user, shipping_option_id=ship),
    )
    variant = seed.variant()
    for bad in (0, 11):
        expect_violation(
            conn,
            "ck_cart_lines_quantity_range",
            insert(CartLine).values(cart_id=cart, variant_id=variant, quantity=bad),
        )
    _insert(conn, CartLine, cart_id=cart, variant_id=variant, quantity=10)
    expect_violation(
        conn,
        "uq_cart_line_variant",
        insert(CartLine).values(cart_id=cart, variant_id=variant, quantity=1),
    )


def test_cart_lock_is_exclusive_per_order(seed: Seed, conn: Connection) -> None:
    order = seed.order()
    ship = seed.shipping()
    _insert(conn, Cart, customer_id=seed.user(), shipping_option_id=ship, locked_by_order_id=order)
    expect_violation(
        conn,
        "uq_carts_locked_by_order",
        insert(Cart).values(
            customer_id=seed.user(), shipping_option_id=ship, locked_by_order_id=order
        ),
    )


def test_wishlist_and_review_uniqueness_and_rating_bounds(seed: Seed, conn: Connection) -> None:
    user, product = seed.user(), seed.product()
    _insert(conn, WishlistItem, customer_id=user, product_id=product)
    expect_violation(
        conn,
        "uq_wishlist_customer_product",
        insert(WishlistItem).values(customer_id=user, product_id=product),
    )
    order = seed.order(user)
    review: dict[str, Any] = {
        "customer_id": user,
        "product_id": product,
        "verified_order_id": order,
        "rating": 5,
    }
    _insert(conn, Review, **review)
    expect_violation(conn, "uq_review_customer_product", insert(Review).values(**review))
    other = seed.product()
    for bad in (0, 6):
        expect_violation(
            conn,
            "ck_reviews_rating_range",
            insert(Review).values(**{**review, "product_id": other, "rating": bad}),
        )
    expect_violation(
        conn,
        "ck_reviews_hidden_metadata_consistency",
        insert(Review).values(**{**review, "product_id": other, "is_hidden": True}),
    )


def test_address_constraints(seed: Seed, conn: Connection) -> None:
    user = seed.user()
    base: dict[str, Any] = {
        "customer_id": user,
        "recipient_name": "R",
        "phone": "0821234567",
        "line1": "1 Main",
        "city": "Johannesburg",
        "province": "Gauteng",
        "postal_code": "2000",
        "country_code": "ZA",
        "is_default": True,
    }
    _insert(conn, Address, **base)
    expect_violation(conn, "uq_addresses_one_default_per_customer", insert(Address).values(**base))
    _insert(conn, Address, **{**base, "is_default": False})
    expect_violation(
        conn,
        "ck_addresses_postal_code_format",
        insert(Address).values(**{**base, "is_default": False, "postal_code": "200A"}),
    )
    expect_violation(
        conn,
        "ck_addresses_country_code_format",
        insert(Address).values(**{**base, "is_default": False, "country_code": "za"}),
    )


def _coupon(**kw: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "code": "SAVE10",
        "discount_type": "percentage",
        "percentage_basis_points": 1000,
        "minimum_order_minor": 0,
        "minimum_is_exclusive": False,
        "starts_at": NOW,
        "expires_at": NOW + timedelta(days=1),
        "is_active": True,
        "eligibility_rule": "all_customers",
    }
    return {**base, **kw}


def test_coupon_constraints(conn: Connection) -> None:
    _insert(conn, Coupon, **_coupon())
    expect_violation(conn, "uq_coupon_code", insert(Coupon).values(**_coupon()))
    expect_violation(
        conn,
        "ck_coupons_discount_value_matches_type",
        insert(Coupon).values(**_coupon(code="BAD1", fixed_discount_minor=500)),
    )
    expect_violation(
        conn,
        "ck_coupons_discount_value_matches_type",
        insert(Coupon).values(
            **_coupon(code="BAD2", discount_type="fixed", percentage_basis_points=None)
        ),
    )
    expect_violation(
        conn,
        "ck_coupons_percentage_range",
        insert(Coupon).values(**_coupon(code="BAD3", percentage_basis_points=10001)),
    )
    expect_violation(
        conn,
        "ck_coupons_validity_window",
        insert(Coupon).values(**_coupon(code="BAD4", expires_at=NOW)),
    )
    expect_violation(conn, "ck_coupons_code_format", insert(Coupon).values(**_coupon(code="lower")))
    expect_violation(
        conn,
        "ck_coupons_global_usage_limit_positive",
        insert(Coupon).values(**_coupon(code="BAD5", global_usage_limit=0)),
    )


def test_coupon_usage_state_and_one_usage_per_order(seed: Seed, conn: Connection) -> None:
    user = seed.user()
    order = seed.order(user)
    coupon = _insert(conn, Coupon, **_coupon())
    usage: dict[str, Any] = {
        "coupon_id": coupon,
        "customer_id": user,
        "order_id": order,
        "usage_state": "reserved",
        "reserved_at": NOW,
    }
    _insert(conn, CouponUsage, **usage)
    expect_violation(conn, "uq_coupon_usage_order", insert(CouponUsage).values(**usage))
    expect_violation(
        conn,
        "ck_coupon_usages_finalization_consistency",
        insert(CouponUsage).values(
            **{**usage, "order_id": seed.order(user), "usage_state": "consumed"}
        ),
    )
    expect_violation(
        conn,
        ("ck_coupon_usages_state", "ck_coupon_usages_finalization_consistency"),
        insert(CouponUsage).values(
            **{**usage, "order_id": seed.order(user), "usage_state": "weird"}
        ),
    )


def test_order_money_status_and_number_invariants(seed: Seed, conn: Connection) -> None:
    ok = seed.order(
        subtotal_minor=10000, discount_minor=1000, shipping_fee_minor=6000, total_minor=15000
    )
    assert ok
    expect_violation(
        conn,
        "ck_orders_total_arithmetic",
        update(Order).where(Order.id == ok).values(total_minor=14999),
    )
    expect_violation(
        conn,
        "ck_orders_status",
        update(Order).where(Order.id == ok).values(status="paid"),
    )
    expect_violation(
        conn,
        "ck_orders_number_format",
        update(Order).where(Order.id == ok).values(order_number="NC-1"),
    )
    expect_violation(
        conn,
        "ck_orders_discount_not_above_subtotal",
        update(Order).where(Order.id == ok).values(discount_minor=10001, total_minor=5999),
    )
    expect_violation(
        conn,
        "ck_orders_reservation_after_placement",
        update(Order).where(Order.id == ok).values(reservation_deadline=NOW),
    )


def test_at_most_one_pending_order_per_customer(seed: Seed, conn: Connection) -> None:
    user = seed.user()
    seed.order(user, status="pending")
    seed.order(user, status="confirmed")
    seed.order(user, status="cancelled")
    expect_violation(
        conn,
        "uq_one_pending_order_per_customer",
        insert(Order).values(
            order_number="NC-20261028-999999",
            customer_id=user,
            status="pending",
            subtotal_minor=1,
            discount_minor=0,
            shipping_fee_minor=0,
            total_minor=1,
            shipping_option_id=seed.shipping(),
            shipping_option_code_snapshot="s",
            shipping_option_name_snapshot="S",
            reservation_deadline=NOW + timedelta(minutes=5),
            placed_at=NOW,
        ),
    )


def test_order_item_line_total_and_restrict_delete(seed: Seed, conn: Connection) -> None:
    order, product = seed.order(), seed.product()
    variant = seed.variant(product)
    item: dict[str, Any] = {
        "order_id": order,
        "product_id": product,
        "variant_id": variant,
        "product_name_snapshot": "P",
        "variant_description_snapshot": "v",
        "sku_snapshot": "S",
        "image_asset_key_snapshot": "k",
        "unit_price_minor": 100,
        "quantity": 3,
        "line_total_minor": 300,
    }
    _insert(conn, OrderItem, **item)
    expect_violation(
        conn,
        "ck_order_items_line_total",
        insert(OrderItem).values(
            **{
                **item,
                "variant_id": seed.variant(
                    product, sku="OTHER-V", options={"c": "1"}, options_key='{"c":"1"}'
                ),
                "line_total_minor": 299,
            }
        ),
    )
    expect_violation(conn, "uq_order_variant_line", insert(OrderItem).values(**item))
    with pytest.raises(IntegrityError), conn.begin_nested():
        conn.execute(text("DELETE FROM product_variants WHERE id = :id"), {"id": variant})


def test_payment_attempt_constraints(seed: Seed, conn: Connection) -> None:
    order = seed.order()
    seed.payment(order, attempt_number=1, outcome="declined", idempotency_key="key-aaaa-1")
    expect_violation(
        conn,
        "uq_payment_attempt_number",
        insert(PaymentAttempt).values(
            order_id=order,
            attempt_number=1,
            outcome="error",
            amount_minor=15000,
            idempotency_key="key-bbbb-2",
            occurred_at=NOW,
        ),
    )
    expect_violation(
        conn,
        "uq_payment_idempotency_key",
        insert(PaymentAttempt).values(
            order_id=order,
            attempt_number=2,
            outcome="error",
            amount_minor=15000,
            idempotency_key="key-aaaa-1",
            occurred_at=NOW,
        ),
    )
    seed.payment(order, attempt_number=2, outcome="approved", idempotency_key="key-cccc-3")
    expect_violation(
        conn,
        "uq_one_approved_payment_per_order",
        insert(PaymentAttempt).values(
            order_id=order,
            attempt_number=3,
            outcome="approved",
            amount_minor=15000,
            idempotency_key="key-dddd-4",
            occurred_at=NOW,
        ),
    )
    expect_violation(
        conn,
        "ck_payment_attempts_outcome",
        insert(PaymentAttempt).values(
            order_id=order,
            attempt_number=4,
            outcome="paid",
            amount_minor=15000,
            idempotency_key="key-eeee-5",
            occurred_at=NOW,
        ),
    )
    expect_violation(
        conn,
        "ck_payment_attempts_idempotency_key_format",
        insert(PaymentAttempt).values(
            order_id=order,
            attempt_number=5,
            outcome="error",
            amount_minor=15000,
            idempotency_key="bad key!!",
            occurred_at=NOW,
        ),
    )


def test_idempotency_scope_key_retention_and_purge_keeps_payment_attempt(
    seed: Seed, conn: Connection
) -> None:
    user = seed.user()
    order = seed.order(user)
    record = seed.idem(user, scope=f"pay_order:{order}", key_value="same-key-1")
    expect_violation(
        conn,
        "uq_idempotency_scope_key",
        insert(IdempotencyRecord).values(
            customer_id=user,
            scope=f"pay_order:{order}",
            key_value="same-key-1",
            request_fingerprint="b" * 64,
            response_status=200,
            response_body={},
            expires_at=NOW + timedelta(days=2),
        ),
    )
    seed.idem(user, scope="place_order", key_value="same-key-1")  # same key, different scope
    seed.idem(seed.user(), scope=f"pay_order:{order}", key_value="same-key-1")  # other customer
    expect_violation(
        conn,
        "ck_idempotency_records_retention",
        insert(IdempotencyRecord).values(
            customer_id=user,
            scope="s",
            key_value="short-ret-1",
            request_fingerprint="c" * 64,
            response_status=200,
            response_body={},
            created_at=NOW,
            expires_at=NOW + timedelta(hours=23),
        ),
    )
    expect_violation(
        conn,
        "ck_idempotency_records_fingerprint_format",
        insert(IdempotencyRecord).values(
            customer_id=user,
            scope="s",
            key_value="fp-bad-key1",
            request_fingerprint="XYZ",
            response_status=200,
            response_body={},
            expires_at=NOW + timedelta(days=2),
        ),
    )
    attempt = seed.payment(order, idempotency_record_id=record)
    conn.execute(text("DELETE FROM idempotency_records WHERE id = :id"), {"id": record})
    link = conn.execute(
        select(PaymentAttempt.idempotency_record_id).where(PaymentAttempt.id == attempt)
    ).scalar_one()
    assert link is None


def test_refund_constraints(seed: Seed, conn: Connection) -> None:
    order = seed.order()
    _insert(conn, Refund, order_id=order, amount_minor=15000, status="refund_pending")
    expect_violation(
        conn,
        "uq_refund_order",
        insert(Refund).values(order_id=order, amount_minor=15000, status="refund_pending"),
    )
    other = seed.order()
    expect_violation(
        conn,
        "ck_refunds_completion_consistency",
        insert(Refund).values(order_id=other, amount_minor=15000, status="refunded"),
    )
    expect_violation(
        conn,
        "ck_refunds_completion_consistency",
        insert(Refund).values(
            order_id=other, amount_minor=15000, status="refund_pending", completed_at=NOW
        ),
    )
    _insert(conn, Refund, order_id=other, amount_minor=15000, status="refunded", completed_at=NOW)


def test_inventory_movement_constraints(seed: Seed, conn: Connection) -> None:
    variant = seed.variant()
    mv: dict[str, Any] = {
        "variant_id": variant,
        "delta_quantity": 5,
        "reason_code": "initial_stock",
        "reference_type": "seed",
        "operation_key": "seed:v1",
        "occurred_at": NOW,
    }
    _insert(conn, InventoryMovement, **mv)
    expect_violation(conn, "uq_inventory_operation_key", insert(InventoryMovement).values(**mv))
    expect_violation(
        conn,
        "ck_inventory_movements_delta_nonzero",
        insert(InventoryMovement).values(**{**mv, "delta_quantity": 0, "operation_key": "k2"}),
    )
    expect_violation(
        conn,
        "ck_inventory_movements_reason_code",
        insert(InventoryMovement).values(**{**mv, "reason_code": "oops", "operation_key": "k3"}),
    )
    expect_violation(
        conn,
        "ck_inventory_movements_admin_reason",
        insert(InventoryMovement).values(
            **{**mv, "reason_code": "admin_adjustment", "operation_key": "k4"}
        ),
    )
    _insert(
        conn,
        InventoryMovement,
        **{
            **mv,
            "reason_code": "admin_adjustment",
            "operation_key": "k5",
            "reason_text": "recount",
        },
    )


def test_status_history_admin_cancel_reason_required(seed: Seed, conn: Connection) -> None:
    order = seed.order()
    row: dict[str, Any] = {
        "order_id": order,
        "to_status": "cancelled",
        "actor_type": "admin",
        "occurred_at": NOW,
    }
    expect_violation(
        conn,
        "ck_order_status_history_admin_cancel_reason",
        text(
            "INSERT INTO order_status_history (order_id,to_status,actor_type,occurred_at)"
            f" VALUES ('{order}','cancelled','admin','{NOW.isoformat()}')"
        ),
    )
    conn.execute(
        text(
            "INSERT INTO order_status_history (order_id,to_status,actor_type,reason,occurred_at)"
            f" VALUES ('{order}','cancelled','admin','stock error','{NOW.isoformat()}')"
        )
    )
    conn.execute(
        text(
            "INSERT INTO order_status_history (order_id,to_status,actor_type,occurred_at)"
            f" VALUES ('{order}','cancelled','customer','{NOW.isoformat()}')"
        )
    )
    assert row


def test_non_dml_errors_are_database_errors_not_silent(conn: Connection) -> None:
    with pytest.raises(DBAPIError), conn.begin_nested():
        conn.execute(
            text(
                "INSERT INTO users (name,email,password_hash,role) VALUES (NULL,'z@example.test','x','customer')"
            )
        )
