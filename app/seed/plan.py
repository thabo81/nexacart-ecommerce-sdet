"""Builds every seed row as plain dicts (pure, no database); the loader inserts them."""

import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from app.persistence.models.catalog import (
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    ProductVariant,
)
from app.persistence.models.engagement import Review
from app.persistence.models.identity import User
from app.persistence.models.ledger import InventoryMovement
from app.persistence.models.orders import (
    Order,
    OrderAddressSnapshot,
    OrderItem,
    OrderStatusHistory,
    PaymentAttempt,
)
from app.persistence.models.pricing import Coupon, ShippingOption
from app.persistence.models.shopping import Address, Cart, CartLine
from app.seed import catalogue, commerce, people, taxonomy
from app.seed.constants import COUNTRY_CODE, FAR_FUTURE, at
from app.seed.ids import seed_id
from app.seed.model import (
    ProductSpec,
    VariantSpec,
    options_key,
    variant_label,
    variant_sku,
)

ZERO_FIXTURE_INITIAL = 10  # initial_stock quantity later neutralised for zero-stock variants


@dataclass
class Plan:
    tables: list[tuple[Any, list[dict[str, Any]]]] = field(default_factory=list)
    user_emails: dict[str, str] = field(default_factory=dict)  # account key -> email
    expected_stock: dict[uuid.UUID, int] = field(default_factory=dict)

    def add(self, model: Any, rows: list[dict[str, Any]]) -> None:
        self.tables.append((model, rows))

    def rows(self, model: Any) -> list[dict[str, Any]]:
        return [r for m, rows in self.tables if m is model for r in rows]


def product_id(slug: str) -> uuid.UUID:
    return seed_id("product", slug)


def variant_id_for(product: ProductSpec, variant: VariantSpec) -> uuid.UUID:
    return seed_id("variant", variant_sku(product.base_sku, variant.options))


def user_id(key: str) -> uuid.UUID:
    return seed_id("user", key)


def seed_user_ids() -> list[uuid.UUID]:
    return [user_id(a.key) for a in people.ACCOUNTS]


def build_plan() -> Plan:
    plan = Plan()
    products = catalogue.all_products()
    by_slug = {p.slug: p for p in products}
    orders = people.orders()
    admin_id = user_id("admin")

    # ---- categories (parents first)
    categories = taxonomy.build_categories()
    plan.add(
        Category,
        [
            {
                "id": seed_id("category", c.slug),
                "slug": c.slug,
                "name": c.name,
                "description": c.description,
                "parent_id": seed_id("category", c.parent_slug) if c.parent_slug else None,
                "is_active": True,
                "is_small_goods": c.small_goods,
                "sort_order": c.sort_order,
                "created_at": at(0),
                "updated_at": at(0),
            }
            for c in sorted(categories, key=lambda x: x.parent_slug is not None)
        ],
    )

    # ---- shipping + coupons
    plan.add(
        ShippingOption,
        [
            {
                "id": seed_id("shipping", s.code),
                "code": s.code,
                "display_name": s.name,
                "base_fee_minor": s.base_fee_minor,
                "delivery_estimate": s.estimate,
                "is_active": True,
                "sort_order": s.sort_order,
            }
            for s in commerce.SHIPPING
        ],
    )
    plan.add(
        Coupon,
        [
            {
                "id": seed_id("coupon", c.code),
                "code": c.code,
                "discount_type": c.discount_type,
                "percentage_basis_points": c.percentage_basis_points,
                "fixed_discount_minor": c.fixed_discount_minor,
                "maximum_discount_minor": c.maximum_discount_minor,
                "minimum_order_minor": c.minimum_order_minor,
                "minimum_is_exclusive": c.minimum_is_exclusive,
                "starts_at": c.starts_at,
                "expires_at": c.expires_at,
                "is_active": c.is_active,
                "global_usage_limit": c.global_usage_limit,
                "per_customer_usage_limit": c.per_customer_usage_limit,
                "eligibility_rule": c.eligibility_rule,
                "created_at": at(0),
                "updated_at": at(0),
            }
            for c in commerce.COUPONS
        ],
    )

    # ---- users (password_hash injected by the loader, only for accounts that do not yet exist)
    plan.add(
        User,
        [
            {
                "id": user_id(a.key),
                "name": a.name,
                "email": a.email,
                "phone": a.phone,
                "role": a.role,
                "is_active": True,
                "created_at": at(0),
                "updated_at": at(0),
            }
            for a in people.ACCOUNTS
        ],
    )
    plan.user_emails = {a.key: a.email for a in people.ACCOUNTS}
    plan.add(
        Address,
        [
            {
                "id": seed_id("address", a.key),
                "customer_id": user_id(a.key),
                "recipient_name": people.ADDRESS["recipient_name"],
                "phone": people.ADDRESS["phone"],
                "line1": people.ADDRESS["line1"],
                "line2": people.ADDRESS["line2"],
                "city": people.ADDRESS["city"],
                "province": people.ADDRESS["province"],
                "postal_code": people.ADDRESS["postal_code"],
                "country_code": COUNTRY_CODE,
                "is_default": True,
                "created_at": at(0),
                "updated_at": at(0),
            }
            for a in people.ACCOUNTS
            if a.has_address
        ],
    )

    # ---- review aggregates
    ratings: dict[str, list[int]] = defaultdict(list)
    for review in people.REVIEWS:
        ratings[review.product_slug].append(review.rating)

    # ---- products, variants, images, specs
    prod_rows: list[dict[str, Any]] = []
    var_rows: list[dict[str, Any]] = []
    img_rows: list[dict[str, Any]] = []
    spec_rows: list[dict[str, Any]] = []
    for index, p in enumerate(products):
        average, count = people.aggregate(ratings.get(p.slug, []))
        created = at(minutes=index)
        prod_rows.append(
            {
                "id": product_id(p.slug),
                "category_id": seed_id("category", p.sub),
                "slug": p.slug,
                "base_sku": p.base_sku,
                "name": p.name,
                "brand": p.brand,
                "description": catalogue.full_description(p),
                "is_active": p.active,
                "is_featured": p.featured,
                "is_fictional": True,
                "rating_average": average,
                "rating_count": count,
                "created_at": created,
                "updated_at": created,
            }
        )
        for v in p.variants:
            var_rows.append(
                {
                    "id": variant_id_for(p, v),
                    "product_id": product_id(p.slug),
                    "sku": variant_sku(p.base_sku, v.options),
                    "options": {k.strip().lower(): val.strip() for k, val in v.options},
                    "options_key": options_key(v.options),
                    "unit_price_minor": v.price_minor,
                    "is_active": v.active,
                    "is_default": v.is_default,
                    "created_at": created,
                    "updated_at": created,
                    # stock_quantity is filled in below once order consumption is known
                }
            )
        for order_index, key in enumerate(catalogue.asset_keys(p)):
            alt_suffix = "product image" if order_index == 0 else "alternate view"
            img_rows.append(
                {
                    "id": seed_id("image", key),
                    "product_id": product_id(p.slug),
                    "asset_key": key,
                    "alt_text": f"{p.name} — {alt_suffix}",
                    "is_primary": order_index == 0,
                    "sort_order": order_index,
                    "created_at": created,
                }
            )
        for spec_index, (name, value) in enumerate(p.specs):
            spec_rows.append(
                {
                    "id": seed_id("spec", f"{p.slug}:{name}"),
                    "product_id": product_id(p.slug),
                    "name": name,
                    "value": value,
                    "sort_order": spec_index,
                }
            )

    # ---- stock accounting: initial = final + net consumption by non-cancelled seed orders
    consumed: dict[uuid.UUID, int] = defaultdict(int)
    for order in orders:
        if order.status == "cancelled":
            continue
        for line in order.lines:
            consumed[_variant_for(by_slug, line.product_slug, line.options)] += line.quantity
    final_stock: dict[uuid.UUID, int] = {}
    for p in products:
        for v in p.variants:
            final_stock[variant_id_for(p, v)] = v.stock
    for row in var_rows:
        row["stock_quantity"] = final_stock[row["id"]]
    plan.expected_stock = dict(final_stock)

    plan.add(Product, prod_rows)
    plan.add(ProductVariant, var_rows)
    plan.add(ProductImage, img_rows)
    plan.add(ProductSpecification, spec_rows)

    # ---- orders and dependants
    sku_by_variant = {r["id"]: r["sku"] for r in var_rows}
    price_by_variant = {r["id"]: r["unit_price_minor"] for r in var_rows}
    order_rows: list[dict[str, Any]] = []
    item_rows: list[dict[str, Any]] = []
    snap_rows: list[dict[str, Any]] = []
    hist_rows: list[dict[str, Any]] = []
    pay_rows: list[dict[str, Any]] = []
    move_rows: list[dict[str, Any]] = []
    ship_by_code = {s.code: s for s in commerce.SHIPPING}
    for order in orders:
        oid = seed_id("order", order.number)
        placed = at(order.day)
        subtotal = 0
        for line in order.lines:
            product = by_slug[line.product_slug]
            vid = _variant_for(by_slug, line.product_slug, line.options)
            variant = next(v for v in product.variants if variant_id_for(product, v) == vid)
            unit = price_by_variant[vid]
            total = unit * line.quantity
            subtotal += total
            item_id = seed_id("order_item", f"{order.number}:{sku_by_variant[vid]}")
            item_rows.append(
                {
                    "id": item_id,
                    "order_id": oid,
                    "product_id": product_id(product.slug),
                    "variant_id": vid,
                    "product_name_snapshot": product.name,
                    "variant_description_snapshot": variant_label(variant.options),
                    "sku_snapshot": sku_by_variant[vid],
                    "image_asset_key_snapshot": catalogue.asset_keys(product)[0],
                    "unit_price_minor": unit,
                    "quantity": line.quantity,
                    "line_total_minor": total,
                    "created_at": placed,
                }
            )
            op_key = f"seed:order_placed:{order.number}:{sku_by_variant[vid]}"
            move_rows.append(
                _movement(
                    vid,
                    -line.quantity,
                    "order_placed",
                    op_key,
                    placed,
                    oid,
                    item_id,
                    "order_item",
                    item_id,
                    None,
                    None,
                )
            )
            if order.status == "cancelled":
                cancel_key = f"seed:order_cancelled:{order.number}:{sku_by_variant[vid]}"
                move_rows.append(
                    _movement(
                        vid,
                        line.quantity,
                        "order_cancelled",
                        cancel_key,
                        placed + timedelta(hours=1),
                        oid,
                        item_id,
                        "order_item",
                        item_id,
                        None,
                        None,
                    )
                )
        shipping = ship_by_code[order.shipping_code]
        is_pending = order.status == "pending"
        order_rows.append(
            {
                "id": oid,
                "order_number": order.number,
                "customer_id": user_id(order.customer),
                "status": order.status,
                "subtotal_minor": subtotal,
                "discount_minor": 0,
                "shipping_fee_minor": order.shipping_fee_minor,
                "total_minor": subtotal + order.shipping_fee_minor,
                "coupon_code_snapshot": None,
                "shipping_option_id": seed_id("shipping", shipping.code),
                "shipping_option_code_snapshot": shipping.code,
                "shipping_option_name_snapshot": shipping.name,
                # A seeded pending order must not be expired by the (future) reservation worker.
                "reservation_deadline": FAR_FUTURE
                if is_pending
                else placed + timedelta(minutes=30),
                "placed_at": placed,
                "cancelled_at": placed + timedelta(hours=1)
                if order.status == "cancelled"
                else None,
                "created_at": placed,
                "updated_at": placed,
            }
        )
        snap_rows.append(
            {
                "order_id": oid,
                "recipient_name": people.ADDRESS["recipient_name"],
                "phone": people.ADDRESS["phone"],
                "line1": people.ADDRESS["line1"],
                "line2": people.ADDRESS["line2"],
                "city": people.ADDRESS["city"],
                "province": people.ADDRESS["province"],
                "postal_code": people.ADDRESS["postal_code"],
                "country_code": COUNTRY_CODE,
                "created_at": placed,
            }
        )
        hist_rows.extend(_history(order, oid, placed, admin_id, user_id(order.customer)))
        if order.status not in ("pending", "cancelled"):
            pay_rows.append(
                {
                    "id": seed_id("payment", order.number),
                    "order_id": oid,
                    "attempt_number": 1,
                    "outcome": "approved",
                    "amount_minor": subtotal + order.shipping_fee_minor,
                    "idempotency_key": f"seed-pay-{order.number}",
                    "idempotency_record_id": None,
                    "occurred_at": placed + timedelta(minutes=5),
                }
            )
    plan.add(Order, order_rows)
    plan.add(OrderItem, item_rows)
    plan.add(OrderAddressSnapshot, snap_rows)
    plan.add(OrderStatusHistory, hist_rows)
    plan.add(PaymentAttempt, pay_rows)

    # ---- carts: customer@ empty; history@ locked to its pending order (cart lock)
    pending = next(o for o in orders if o.status == "pending")
    cart_rows = [
        {
            "id": seed_id("cart", "customer"),
            "customer_id": user_id("customer"),
            "applied_coupon_id": None,
            "shipping_option_id": seed_id("shipping", "standard"),
            "locked_by_order_id": None,
            "created_at": at(0),
            "updated_at": at(0),
        },
        {
            "id": seed_id("cart", "history"),
            "customer_id": user_id("history"),
            "applied_coupon_id": None,
            "shipping_option_id": seed_id("shipping", "standard"),
            "locked_by_order_id": seed_id("order", pending.number),
            "created_at": at(pending.day),
            "updated_at": at(pending.day),
        },
    ]
    line_rows = []
    for line in pending.lines:
        vid = _variant_for(by_slug, line.product_slug, line.options)
        line_rows.append(
            {
                "id": seed_id("cart_line", f"history:{sku_by_variant[vid]}"),
                "cart_id": seed_id("cart", "history"),
                "variant_id": vid,
                "quantity": line.quantity,
                "last_acknowledged_unit_price_minor": price_by_variant[vid],
                "created_at": at(pending.day),
                "updated_at": at(pending.day),
            }
        )
    plan.add(Cart, cart_rows)
    plan.add(CartLine, line_rows)

    # ---- reviews (verified by the reviewer's delivered order)
    order_by_customer = {
        o.customer: o for o in orders if o.status == "delivered" and o.key.endswith("-delivered")
    }
    plan.add(
        Review,
        [
            {
                "id": seed_id("review", f"{r.reviewer}:{r.product_slug}"),
                "customer_id": user_id(r.reviewer),
                "product_id": product_id(r.product_slug),
                "verified_order_id": seed_id("order", order_by_customer[r.reviewer].number),
                "rating": r.rating,
                "comment": r.comment,
                "is_hidden": False,
                "hidden_by_user_id": None,
                "hidden_at": None,
                "created_at": at(order_by_customer[r.reviewer].day + 10, minutes=i),
            }
            for i, r in enumerate(people.REVIEWS)
        ],
    )

    # ---- initial ledger (deterministic operation keys)
    for row in var_rows:
        vid = row["id"]
        final = final_stock[vid]
        initial = final + consumed[vid] if final > 0 or consumed[vid] else ZERO_FIXTURE_INITIAL
        sku = row["sku"]
        move_rows.append(
            _movement(
                vid,
                initial,
                "initial_stock",
                f"seed:initial_stock:{sku}",
                at(0),
                None,
                None,
                "seed",
                None,
                None,
                None,
            )
        )
        if final == 0 and consumed[vid] == 0:
            move_rows.append(
                _movement(
                    vid,
                    -ZERO_FIXTURE_INITIAL,
                    "admin_adjustment",
                    f"seed:seed_adjustment:{sku}",
                    at(minutes=1),
                    None,
                    None,
                    "seed",
                    None,
                    admin_id,
                    "Seed fixture: baseline out-of-stock variant (zero-stock scenario)",
                )
            )
    plan.add(InventoryMovement, move_rows)
    return plan


def _variant_for(
    by_slug: dict[str, ProductSpec], slug: str, options: tuple[tuple[str, str], ...]
) -> uuid.UUID:
    product = by_slug[slug]
    for variant in product.variants:
        if variant.options == options:
            return variant_id_for(product, variant)
    raise KeyError(f"no variant {options} on {slug}")


def _movement(
    variant: uuid.UUID,
    delta: int,
    reason: str,
    key: str,
    occurred: Any,
    order_id: uuid.UUID | None,
    item_id: uuid.UUID | None,
    ref_type: str,
    ref_id: uuid.UUID | None,
    actor: uuid.UUID | None,
    text: str | None,
) -> dict[str, Any]:
    return {
        "id": seed_id("movement", key),
        "variant_id": variant,
        "delta_quantity": delta,
        "reason_code": reason,
        "order_id": order_id,
        "order_item_id": item_id,
        "reference_type": ref_type,
        "reference_id": ref_id,
        "operation_key": key,
        "actor_user_id": actor,
        "reason_text": text,
        "occurred_at": occurred,
    }


def _history(
    order: Any, oid: uuid.UUID, placed: Any, admin_id: uuid.UUID, customer: uuid.UUID
) -> list[dict[str, Any]]:
    steps: list[tuple[str | None, str, str, uuid.UUID | None]] = [
        (None, "pending", "customer", customer)
    ]
    chain = ["confirmed", "processing", "shipped", "delivered"]
    if order.status == "cancelled":
        steps.append(("pending", "cancelled", "customer", customer))
    elif order.status != "pending":
        previous = "pending"
        for target in chain:
            actor, actor_id = ("system", None) if target == "confirmed" else ("admin", admin_id)
            steps.append((previous, target, actor, actor_id))
            previous = target
            if target == order.status:
                break
    rows = []
    for offset, (frm, to, actor, actor_id) in enumerate(steps):
        rows.append(
            {
                "id": seed_id("order_history", f"{order.number}:{to}"),
                "order_id": oid,
                "from_status": frm,
                "to_status": to,
                "actor_type": actor,
                "actor_user_id": actor_id,
                "reason": "Customer cancelled before payment" if to == "cancelled" else None,
                "request_id": None,
                "occurred_at": placed
                + timedelta(hours=offset if to == "cancelled" else 0, minutes=offset * 10),
            }
        )
    return rows
