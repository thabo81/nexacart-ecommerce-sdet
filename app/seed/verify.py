"""Read-only baseline report and invariant checks (counts, ledger = stock, rating aggregates)."""

import hashlib
import json
from typing import Any

from sqlalchemy import Connection, text

from app.persistence.models.catalog import Product
from app.seed.catalogue import BANDS
from app.seed.taxonomy import COMPUTERS, FOOTBALL, PHONES, SHOES, WEARABLES

# Tables included in the snapshot digest (order-independent, id-sorted).
SNAPSHOT_TABLES = (
    "categories",
    "products",
    "product_variants",
    "product_images",
    "product_specifications",
    "shipping_options",
    "coupons",
    "users",
    "addresses",
    "carts",
    "cart_lines",
    "orders",
    "order_items",
    "order_address_snapshots",
    "order_status_history",
    "payment_attempts",
    "reviews",
    "inventory_movements",
    "coupon_usages",
    "refunds",
)

_PK = {"order_address_snapshots": "order_id"}


def snapshot(conn: Connection) -> dict[str, dict[str, Any]]:
    """Per-table row count and sha256 over all columns (including password_hash) ordered by key."""
    result: dict[str, dict[str, Any]] = {}
    for table in SNAPSHOT_TABLES:
        pk = _PK.get(table, "id")
        rows = conn.execute(text(f"SELECT t::text FROM {table} t ORDER BY {pk}")).scalars().all()  # noqa: S608
        digest = hashlib.sha256("\n".join(rows).encode()).hexdigest()
        result[table] = {"rows": len(rows), "sha256": digest}
    return result


def baseline_report(conn: Connection) -> dict[str, Any]:
    def scalar(sql: str) -> Any:
        return conn.execute(text(sql)).scalar_one()

    def rows(sql: str) -> list[tuple[Any, ...]]:
        return [tuple(r) for r in conn.execute(text(sql)).all()]

    report: dict[str, Any] = {
        "top_level_categories": scalar("SELECT count(*) FROM categories WHERE parent_id IS NULL"),
        "subcategories": scalar("SELECT count(*) FROM categories WHERE parent_id IS NOT NULL"),
        "products": scalar("SELECT count(*) FROM products"),
        "variants": scalar("SELECT count(*) FROM product_variants"),
        "images": scalar("SELECT count(*) FROM product_images"),
        "multi_variant_products": scalar(
            "SELECT count(*) FROM (SELECT product_id FROM product_variants GROUP BY product_id "
            "HAVING count(*) > 1) s"
        ),
        "shipping": rows("SELECT code, base_fee_minor FROM shipping_options ORDER BY sort_order"),
        "coupons": rows(
            "SELECT code, discount_type, percentage_basis_points, fixed_discount_minor FROM "
            "coupons ORDER BY code"
        ),
        "users": rows("SELECT email, role FROM users ORDER BY email"),
        "orders_by_status": rows(
            "SELECT status, count(*) FROM orders GROUP BY status ORDER BY status"
        ),
        "reviews": scalar("SELECT count(*) FROM reviews"),
        "inventory_movements": scalar("SELECT count(*) FROM inventory_movements"),
        "coupon_usages": scalar("SELECT count(*) FROM coupon_usages"),
    }
    report["products_per_category"] = rows(
        "SELECT c.slug, count(*) FROM products p JOIN categories s ON s.id = p.category_id "
        "JOIN categories c ON c.id = s.parent_id GROUP BY c.slug ORDER BY c.slug"
    )
    cases = " ".join(
        f"WHEN '{slug}' THEN CASE WHEN m.price < {low} THEN 'budget' "
        f"WHEN m.price <= {high} THEN 'mid' ELSE 'premium' END"
        for slug, (low, high) in BANDS.items()
    )
    report["products_per_tier"] = rows(
        f"SELECT c.slug, CASE c.slug {cases} END AS tier, count(*) "  # noqa: S608
        "FROM (SELECT product_id, min(unit_price_minor) AS price FROM product_variants GROUP BY "
        "product_id) m "
        "JOIN products p ON p.id = m.product_id JOIN categories s ON s.id = p.category_id "
        "JOIN categories c ON c.id = s.parent_id GROUP BY c.slug, tier ORDER BY c.slug, tier"
    )
    return report


def invariant_failures(conn: Connection) -> list[str]:
    """Invariants over seed-owned rows only; unrelated data can never fail a seed/reset."""
    from app.seed.plan import build_plan, seed_user_ids

    plan = build_plan()
    params = {
        "pids": [str(r["id"]) for r in plan.rows(Product)],
        "uids": [str(u) for u in seed_user_ids()],
    }
    failures: list[str] = []

    def check(label: str, sql: str) -> None:
        count = conn.execute(text(sql), params).scalar_one()
        if count:
            failures.append(f"{label}: {count}")

    check(
        "variants whose stock != ledger sum",
        "SELECT count(*) FROM product_variants v WHERE v.product_id = ANY(CAST(:pids AS uuid[])) "
        "AND v.stock_quantity != "
        "COALESCE((SELECT sum(delta_quantity) FROM inventory_movements m WHERE m.variant_id = "
        "v.id), 0)",
    )
    check(
        "variants without an initial_stock movement",
        "SELECT count(*) FROM product_variants v WHERE v.product_id = ANY(CAST(:pids AS uuid[])) "
        "AND NOT EXISTS "
        "(SELECT 1 FROM inventory_movements m WHERE m.variant_id = v.id AND m.reason_code = "
        "'initial_stock')",
    )
    check(
        "rating aggregate != visible review rows",
        "SELECT count(*) FROM products p WHERE p.id = ANY(CAST(:pids AS uuid[])) "
        "AND (p.rating_count != (SELECT count(*) FROM reviews r "
        "WHERE r.product_id = p.id AND NOT r.is_hidden) OR p.rating_average != COALESCE((SELECT "
        "round(avg(r.rating)::numeric, 1) FROM reviews r WHERE r.product_id = p.id AND NOT "
        "r.is_hidden), 0))",
    )
    check(
        "products with no primary image",
        "SELECT count(*) FROM products p WHERE p.id = ANY(CAST(:pids AS uuid[])) "
        "AND NOT EXISTS (SELECT 1 FROM product_images i "
        "WHERE i.product_id = p.id AND i.is_primary)",
    )
    check(
        "order totals != item sums",
        "SELECT count(*) FROM orders o WHERE o.customer_id = ANY(CAST(:uids AS uuid[])) AND "
        "o.subtotal_minor != "
        "(SELECT sum(line_total_minor) FROM order_items i WHERE i.order_id = o.id)",
    )
    check(
        "reviews not backed by a delivered order of the same customer containing the product",
        "SELECT count(*) FROM reviews r WHERE r.product_id = ANY(CAST(:pids AS uuid[])) AND NOT "
        "EXISTS "
        "(SELECT 1 FROM orders o JOIN order_items i ON i.order_id = o.id WHERE o.id = "
        "r.verified_order_id "
        "AND o.customer_id = r.customer_id AND o.status = 'delivered' AND i.product_id = "
        "r.product_id)",
    )
    return failures


def category_codes() -> tuple[str, ...]:
    return (COMPUTERS, PHONES, WEARABLES, FOOTBALL, SHOES)


def dumps(data: Any) -> str:
    return json.dumps(data, indent=2, default=str, sort_keys=True)
