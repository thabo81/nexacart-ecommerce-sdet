"""Idempotent loader: inserts missing seed rows (ON CONFLICT DO NOTHING); never updates."""

import uuid
from typing import Any

from sqlalchemy import Connection, literal_column, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.persistence.models.catalog import Category, Product, ProductVariant
from app.persistence.models.identity import User
from app.persistence.models.pricing import Coupon, ShippingOption
from app.seed import people
from app.seed.guard import SeedGuardError
from app.seed.passwords import hash_password, password_for
from app.seed.plan import Plan
from app.seed.settings import SeedSettings

_BATCH = 500


def _natural_key_collisions(conn: Connection, plan: Plan) -> list[str]:
    """Rows that already hold a seed natural key under a *different* id (not seed-owned)."""
    problems: list[str] = []
    checks: list[tuple[Any, str]] = [
        (User, "email"),
        (Category, "slug"),
        (Product, "slug"),
        (Product, "base_sku"),
        (ProductVariant, "sku"),
        (Coupon, "code"),
        (ShippingOption, "code"),
    ]
    for model, column in checks:
        rows = plan.rows(model)
        if not rows:
            continue
        col = getattr(model, column)
        wanted = {r[column]: r["id"] for r in rows}
        found = conn.execute(select(model.id, col).where(col.in_(list(wanted)))).all()
        for existing_id, value in found:
            if wanted[value] != existing_id:
                problems.append(f"{model.__tablename__}.{column}={value!r}")
    return problems


def apply_plan(conn: Connection, plan: Plan, settings: SeedSettings) -> dict[str, int]:
    """Insert missing rows in the caller's transaction; returns inserted counts per table."""
    collisions = _natural_key_collisions(conn, plan)
    if collisions:
        raise SeedGuardError(
            "Seed natural keys already exist on non-seed rows (refusing to proceed): "
            + ", ".join(collisions[:10])
        )

    existing_users = set(conn.execute(select(User.id)).scalars())
    hashes: dict[uuid.UUID, str] = {}
    for account in people.ACCOUNTS:
        uid = next(r["id"] for r in plan.rows(User) if r["email"] == account.email)
        if uid not in existing_users:  # hash only when creating the account
            hashes[uid] = hash_password(password_for(settings, account.password_var))

    inserted: dict[str, int] = {}
    for model, rows in plan.tables:
        table = model.__tablename__
        prepared: list[dict[str, Any]] = rows
        if model is User:
            prepared = [
                {**r, "password_hash": hashes.get(r["id"], "")} for r in rows if r["id"] in hashes
            ]
            # Existing accounts are skipped entirely so their stored hash is never touched.
            skipped = len(rows) - len(prepared)
            if skipped:
                inserted[table] = 0
        count = 0
        for start in range(0, len(prepared), _BATCH):
            batch = prepared[start : start + _BATCH]
            stmt: Any = (
                pg_insert(model)
                .values(batch)
                .on_conflict_do_nothing()
                .returning(literal_column("1"))
            )
            count += len(
                conn.execute(stmt).all()
            )  # driver rowcount is unreliable for multi-row inserts
        inserted[table] = count
    return inserted
