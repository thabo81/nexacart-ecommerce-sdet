"""PostgreSQL fixtures for schema tests.

These tests need a real, disposable PostgreSQL 16 database. Set ``TEST_DATABASE_URL`` to an
*empty* database the role may fully manage (for example
``postgresql+psycopg://user:pw@localhost:5433/nexacart_test``). Without it, the tests are
skipped, never silently passed against another engine.
"""

import os
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import get_settings

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


def alembic_config(url: str) -> Config:
    os.environ["DATABASE_URL"] = url
    get_settings.cache_clear()
    return Config("alembic.ini")


def _require_url() -> str:
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL is not set; PostgreSQL 16 database tests cannot run")
    return TEST_DATABASE_URL


@pytest.fixture(scope="session")
def migrated_engine() -> Iterator[Engine]:
    url = _require_url()
    engine = create_engine(url)
    with engine.connect() as conn:
        version = conn.execute(text("SHOW server_version_num")).scalar_one()
        assert str(version).startswith("16"), f"PostgreSQL 16 required, got {version}"
        leftovers = conn.execute(
            text(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
                " AND table_name <> 'alembic_version'"
            )
        ).scalar_one()
        assert leftovers == 0, "TEST_DATABASE_URL must point at an empty database"
    cfg = alembic_config(url)
    command.upgrade(cfg, "head")
    yield engine
    command.downgrade(cfg, "base")
    engine.dispose()


@pytest.fixture
def conn(migrated_engine: Engine) -> Iterator[Connection]:
    """A connection whose work is rolled back after each test."""
    with migrated_engine.connect() as connection:
        outer = connection.begin()
        yield connection
        outer.rollback()


def sibling_database_url(url: str, suffix: str) -> str:
    parsed = make_url(url)
    return parsed.set(database=f"{parsed.database}_{suffix}").render_as_string(hide_password=False)
