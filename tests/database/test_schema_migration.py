"""Migration, naming-registry and model/migration parity checks against PostgreSQL 16."""

import re
from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url

import app.persistence.models  # noqa: F401
from app.persistence.base import Base
from tests.database.conftest import TEST_DATABASE_URL, alembic_config, sibling_database_url

ERD = Path("docs/planning/DATABASE_SCHEMA_AND_ERD.md")
EXPECTED_TABLE_COUNT = 26


def test_migration_creates_all_tables(migrated_engine: Engine) -> None:
    with migrated_engine.connect() as c:
        names = set(
            c.execute(
                text(
                    "SELECT table_name FROM information_schema.tables"
                    " WHERE table_schema='public' AND table_name <> 'alembic_version'"
                )
            ).scalars()
        )
    assert names == set(Base.metadata.tables)
    assert len(names) == EXPECTED_TABLE_COUNT


def _erd_names(prefix: str) -> set[str]:
    return set(re.findall(rf"`({prefix}_[a-z0-9_]+)`", ERD.read_text(encoding="utf-8")))


def test_every_erd_registry_name_exists_in_database(migrated_engine: Engine) -> None:
    """Names are read from the approved ERD text, independent of the models."""
    with migrated_engine.connect() as c:
        constraints = set(c.execute(text("SELECT conname FROM pg_constraint")).scalars())
        indexes = set(c.execute(text("SELECT indexname FROM pg_indexes")).scalars())
    present = constraints | indexes
    expected = _erd_names("ck") | _erd_names("uq") | _erd_names("ix")
    assert len(_erd_names("ck")) >= 90
    assert expected - present == set()


def test_no_constraint_or_index_name_is_truncated_or_generated(migrated_engine: Engine) -> None:
    with migrated_engine.connect() as c:
        rows = c.execute(
            text(
                "SELECT conname FROM pg_constraint WHERE connamespace='public'::regnamespace"
                " UNION SELECT indexname FROM pg_indexes WHERE schemaname='public'"
            )
        ).scalars()
        names = list(rows)
    assert all(len(n) <= 63 for n in names)
    assert not [
        n
        for n in names
        if n != "alembic_version_pkc" and not n.startswith(("pk_", "fk_", "uq_", "ix_", "ck_"))
    ]


def test_money_columns_are_integers_and_times_are_timestamptz(migrated_engine: Engine) -> None:
    with migrated_engine.connect() as c:
        money = c.execute(
            text(
                "SELECT table_name, column_name, data_type FROM information_schema.columns"
                " WHERE table_schema='public' AND column_name LIKE '%\\_minor'"
            )
        ).all()
        times = c.execute(
            text(
                "SELECT table_name, column_name, data_type FROM information_schema.columns"
                " WHERE table_schema='public' AND (column_name LIKE '%\\_at'"
                " OR column_name IN ('issued_at','locked_until','reservation_deadline'))"
            )
        ).all()
        floats = c.execute(
            text(
                "SELECT count(*) FROM information_schema.columns WHERE table_schema='public'"
                " AND data_type IN ('real','double precision')"
            )
        ).scalar_one()
    assert money
    assert {r.data_type for r in money} <= {"bigint", "integer"}
    assert times
    assert {r.data_type for r in times} == {"timestamp with time zone"}
    assert floats == 0


def test_uuid_defaults_use_native_gen_random_uuid(migrated_engine: Engine) -> None:
    with migrated_engine.connect() as c:
        rows = c.execute(
            text(
                "SELECT table_name, column_default FROM information_schema.columns"
                " WHERE table_schema='public' AND data_type='uuid' AND column_default IS NOT NULL"
            )
        ).all()
        extensions = set(c.execute(text("SELECT extname FROM pg_extension")).scalars())
    assert len(rows) == 24  # 23 generated ids plus auth_sessions.jti
    assert {r.column_default for r in rows} == {"gen_random_uuid()"}
    assert extensions == {"plpgsql"}


def _catalog(engine: Engine) -> dict[str, list[tuple[str, ...]]]:
    queries = {
        "constraints": "SELECT conrelid::regclass::text, conname, pg_get_constraintdef(oid)"
        " FROM pg_constraint WHERE connamespace='public'::regnamespace"
        " AND conrelid::regclass::text <> 'alembic_version' ORDER BY 1, 2",
        "indexes": "SELECT tablename, indexname, indexdef FROM pg_indexes"
        " WHERE schemaname='public' AND tablename <> 'alembic_version' ORDER BY 1, 2",
        "columns": "SELECT table_name, column_name, data_type, character_maximum_length,"
        " is_nullable, column_default FROM information_schema.columns"
        " WHERE table_schema='public' AND table_name <> 'alembic_version' ORDER BY 1, 2",
    }
    with engine.connect() as c:
        return {k: [tuple(r) for r in c.execute(text(q))] for k, q in queries.items()}


def test_migration_matches_orm_metadata(migrated_engine: Engine) -> None:
    """Build a second database from the models and compare the PostgreSQL catalogs."""
    assert TEST_DATABASE_URL
    parity_url = sibling_database_url(TEST_DATABASE_URL, "parity")
    name = make_url(parity_url).database
    admin = create_engine(TEST_DATABASE_URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        c.execute(text(f'DROP DATABASE IF EXISTS "{name}"'))
        c.execute(text(f'CREATE DATABASE "{name}"'))
    parity = create_engine(parity_url)
    try:
        Base.metadata.create_all(parity)
        assert _catalog(parity) == _catalog(migrated_engine)
    finally:
        parity.dispose()
        with admin.connect() as c:
            c.execute(text(f'DROP DATABASE IF EXISTS "{name}"'))
        admin.dispose()


@pytest.mark.usefixtures("migrated_engine")
def test_downgrade_then_upgrade_round_trip(migrated_engine: Engine) -> None:
    assert TEST_DATABASE_URL
    cfg = alembic_config(TEST_DATABASE_URL)
    command.downgrade(cfg, "base")
    with migrated_engine.connect() as c:
        left = c.execute(
            text(
                "SELECT count(*) FROM information_schema.tables"
                " WHERE table_schema='public' AND table_name <> 'alembic_version'"
            )
        ).scalar_one()
    assert left == 0
    command.upgrade(cfg, "head")
    assert len(_catalog(migrated_engine)["constraints"]) == 180
