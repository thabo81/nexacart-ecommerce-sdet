"""Guarded local/test reset: removes seed-owned and test-created (qa_) data, then re-seeds.

Boundaries (explicit; nothing outside them is deleted):
  * users: the seed accounts plus any user whose email starts with ``qa_`` (TR-016), and everything
    owned by those users (orders and dependants, carts, wishlist, addresses, sessions, reviews,
    idempotency records, audit events they acted in);
  * catalogue: seed products/categories plus slugs starting ``qa-``, and their children;
  * coupons: the five seed coupons plus codes starting ``QA_``; shipping: the two seed codes.
Rows owned by any other user that reference these records make the foreign keys refuse the delete;
the single transaction then rolls back and nothing changes. No DROP/TRUNCATE is ever issued.
Inventory movements are append-only in normal operation; this explicit reset is the one authorised
exception and deletes only movements of in-scope variants/orders/actors.
"""

from typing import Any

from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError

from app.persistence.models.catalog import Category
from app.persistence.models.identity import User
from app.persistence.models.pricing import Coupon, ShippingOption
from app.seed import catalogue
from app.seed.constants import QA_COUPON_PREFIX, QA_EMAIL_PREFIX, QA_SLUG_PREFIX
from app.seed.guard import SeedGuardError
from app.seed.plan import Plan, product_id

_LIKE_ESCAPE = "\\"


def _like(prefix: str) -> str:
    return prefix.replace("_", "\\_").replace("%", "\\%") + "%"


def _ids(plan: Plan, model: Any) -> list[str]:
    return [str(r["id"]) for r in plan.rows(model)]


def _prepare_targets(conn: Connection, plan: Plan) -> None:
    seed_products = [str(product_id(p.slug)) for p in catalogue.all_products()]
    params = {
        "su": _ids(plan, User),
        "sc": _ids(plan, Category),
        "sp": seed_products,
        "scp": _ids(plan, Coupon),
        "ssh": _ids(plan, ShippingOption),
        "qe": _like(QA_EMAIL_PREFIX),
        "qs": _like(QA_SLUG_PREFIX),
        "qc": _like(QA_COUPON_PREFIX),
    }
    stmts = [
        "CREATE TEMP TABLE t_users ON COMMIT DROP AS SELECT id, email FROM users "
        "WHERE id = ANY(CAST(:su AS uuid[])) OR email LIKE :qe ESCAPE '\\'",
        "CREATE TEMP TABLE t_categories ON COMMIT DROP AS SELECT id FROM categories "
        "WHERE id = ANY(CAST(:sc AS uuid[])) OR slug LIKE :qs ESCAPE '\\'",
        "CREATE TEMP TABLE t_products ON COMMIT DROP AS SELECT id FROM products "
        "WHERE id = ANY(CAST(:sp AS uuid[])) OR slug LIKE :qs ESCAPE '\\'",
        "CREATE TEMP TABLE t_variants ON COMMIT DROP AS SELECT id FROM product_variants "
        "WHERE product_id IN (SELECT id FROM t_products)",
        "CREATE TEMP TABLE t_coupons ON COMMIT DROP AS SELECT id FROM coupons "
        "WHERE id = ANY(CAST(:scp AS uuid[])) OR code LIKE :qc ESCAPE '\\'",
        "CREATE TEMP TABLE t_shipping ON COMMIT DROP AS SELECT id FROM shipping_options "
        "WHERE id = ANY(CAST(:ssh AS uuid[]))",
        "CREATE TEMP TABLE t_orders ON COMMIT DROP AS SELECT id FROM orders "
        "WHERE customer_id IN (SELECT id FROM t_users)",
    ]
    for stmt in stmts:
        conn.execute(text(stmt), params)


_BLOCKERS = (
    (
        "order items of in-scope orders that reference variants outside the seed/qa catalogue",
        "SELECT count(*) FROM order_items WHERE order_id IN (SELECT id FROM t_orders) "
        "AND variant_id NOT IN (SELECT id FROM t_variants)",
    ),
    (
        "inventory movements of in-scope orders/actors on variants outside the seed/qa catalogue",
        "SELECT count(*) FROM inventory_movements "
        "WHERE variant_id NOT IN (SELECT id FROM t_variants) "
        "AND (order_id IN (SELECT id FROM t_orders) OR actor_user_id IN (SELECT id FROM t_users))",
    ),
    (
        "reviews by in-scope users on products outside the seed/qa catalogue",
        "SELECT count(*) FROM reviews WHERE customer_id IN (SELECT id FROM t_users) "
        "AND product_id NOT IN (SELECT id FROM t_products)",
    ),
)

_DELETES = (
    "DELETE FROM payment_attempts WHERE order_id IN (SELECT id FROM t_orders)",
    "DELETE FROM refunds WHERE order_id IN (SELECT id FROM t_orders)",
    "DELETE FROM coupon_usages WHERE order_id IN (SELECT id FROM t_orders) "
    "OR customer_id IN (SELECT id FROM t_users)",
    "DELETE FROM inventory_movements WHERE variant_id IN (SELECT id FROM t_variants) "
    "OR order_id IN (SELECT id FROM t_orders) OR actor_user_id IN (SELECT id FROM t_users)",
    "DELETE FROM idempotency_records WHERE customer_id IN (SELECT id FROM t_users) "
    "OR order_id IN (SELECT id FROM t_orders)",
    "DELETE FROM order_status_history WHERE order_id IN (SELECT id FROM t_orders)",
    "DELETE FROM order_address_snapshots WHERE order_id IN (SELECT id FROM t_orders)",
    "DELETE FROM cart_lines WHERE cart_id IN (SELECT id FROM carts WHERE customer_id IN (SELECT "
    "id FROM t_users))",
    "DELETE FROM carts WHERE customer_id IN (SELECT id FROM t_users)",
    "DELETE FROM reviews WHERE customer_id IN (SELECT id FROM t_users)",
    "DELETE FROM order_items WHERE order_id IN (SELECT id FROM t_orders)",
    "DELETE FROM orders WHERE id IN (SELECT id FROM t_orders)",
    "DELETE FROM wishlist_items WHERE customer_id IN (SELECT id FROM t_users)",
    "DELETE FROM addresses WHERE customer_id IN (SELECT id FROM t_users)",
    "DELETE FROM auth_sessions WHERE user_id IN (SELECT id FROM t_users)",
    "DELETE FROM login_throttle_state WHERE email_key IN (SELECT email FROM t_users)",
    "DELETE FROM audit_events WHERE actor_user_id IN (SELECT id FROM t_users)",
    "DELETE FROM product_specifications WHERE product_id IN (SELECT id FROM t_products)",
    "DELETE FROM product_images WHERE product_id IN (SELECT id FROM t_products)",
    "DELETE FROM product_variants WHERE id IN (SELECT id FROM t_variants)",
    "DELETE FROM products WHERE id IN (SELECT id FROM t_products)",
    "DELETE FROM categories WHERE id IN (SELECT id FROM t_categories) AND parent_id IS NOT NULL",
    "DELETE FROM categories WHERE id IN (SELECT id FROM t_categories)",
    "DELETE FROM coupons WHERE id IN (SELECT id FROM t_coupons)",
    "DELETE FROM shipping_options WHERE id IN (SELECT id FROM t_shipping)",
    "DELETE FROM users WHERE id IN (SELECT id FROM t_users)",
)


def clear_scope(conn: Connection, plan: Plan) -> dict[str, int]:
    """Delete everything inside the reset boundary; raises SeedGuardError on any conflict."""
    _prepare_targets(conn, plan)
    for label, sql in _BLOCKERS:
        count = conn.execute(text(sql)).scalar_one()
        if count:
            raise SeedGuardError(f"Reset aborted, nothing deleted: {count} {label}.")
    deleted: dict[str, int] = {}
    for stmt in _DELETES:
        table = stmt.split()[2]
        try:
            result = conn.execute(text(stmt))
        except IntegrityError as exc:
            constraint = (
                getattr(getattr(exc.orig, "diag", None), "constraint_name", None) or "unknown"
            )
            raise SeedGuardError(
                f"Reset aborted, nothing deleted: records outside the seed/qa boundary reference "
                f"in-scope rows (constraint {constraint} on {table}). "
                "Remove them or use a fresh database."
            ) from exc
        deleted[table] = deleted.get(table, 0) + result.rowcount
    return deleted
