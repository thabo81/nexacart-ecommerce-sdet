"""Read-only seed completeness and invariant checks (ledger = stock, rating aggregates)."""

import hashlib
import json
from typing import Any

from sqlalchemy import Connection, select, text, tuple_

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


def seed_baseline_report(conn: Connection) -> dict[str, dict[str, Any]]:
    """Check presence of every planned seed row by its deterministic primary key.

    Counts are scoped to the seed plan, not whole tables, so unrelated local/test records do not
    cause false failures. The check deliberately covers every table populated by the seed plan.
    """
    from app.seed.plan import build_plan

    report: dict[str, dict[str, Any]] = {}
    for model, rows in build_plan().tables:
        if not rows:
            continue

        primary_key_columns = list(model.__mapper__.primary_key)
        key_names = [column.key for column in primary_key_columns]
        primary_key_attributes = [getattr(model, name) for name in key_names]
        expected_keys = {tuple(row[name] for name in key_names) for row in rows}

        if len(primary_key_attributes) == 1:
            values = [key[0] for key in expected_keys]
            present_values = conn.execute(
                select(primary_key_attributes[0]).where(primary_key_attributes[0].in_(values))
            ).scalars()
            present_keys = {(value,) for value in present_values}
        else:
            present_rows = conn.execute(
                select(*primary_key_attributes).where(
                    tuple_(*primary_key_attributes).in_(list(expected_keys))
                )
            )
            present_keys = {tuple(row) for row in present_rows}

        missing_keys = expected_keys - present_keys

        def display_key(key: tuple[Any, ...]) -> str | list[str]:
            if len(key) == 1:
                return str(key[0])
            return [str(value) for value in key]

        report[model.__tablename__] = {
            "expected": len(rows),
            "unique_expected": len(expected_keys),
            "present": len(present_keys),
            "missing": len(missing_keys),
            "duplicate_expected": len(rows) - len(expected_keys),
            "missing_keys": [
                display_key(key)
                for key in sorted(missing_keys, key=lambda values: tuple(str(v) for v in values))[
                    :10
                ]
            ],
        }
    return report


def seed_baseline_failures(report: dict[str, dict[str, Any]]) -> list[str]:
    """Return failures when planned seed rows are duplicated or absent from the database."""
    failures: list[str] = []
    for table, counts in report.items():
        duplicates = int(counts["duplicate_expected"])
        missing = int(counts["missing"])
        if duplicates:
            failures.append(f"{table}: seed plan contains {duplicates} duplicate primary key(s)")
        if missing:
            failures.append(
                f"{table}: {missing} of {counts['unique_expected']} "
                "expected seed row(s) are missing"
            )
    return failures


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
