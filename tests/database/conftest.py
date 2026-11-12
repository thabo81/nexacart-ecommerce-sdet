"""PostgreSQL fixtures for schema tests.

These tests need a real, disposable PostgreSQL 16 database. Set ``TEST_DATABASE_URL`` to an
*empty* database the role may fully manage (for example
``postgresql+psycopg://user:pw@localhost:5433/nexacart_test``). Without it, the tests are
skipped, never silently passed against another engine.
"""

import os
import re
import uuid
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

    database_name = make_url(TEST_DATABASE_URL).database or ""
    if not re.search(r"(^|[_-])test($|[_-])", database_name, flags=re.IGNORECASE):
        pytest.fail(
            "TEST_DATABASE_URL must name a dedicated test database whose name contains "
            "a standalone 'test' segment (for example nexacart_test)."
        )
    if os.environ.get("ALLOW_DESTRUCTIVE_TEST_DB") != "1":
        pytest.fail(
            "The database fixture applies and downgrades a schema. Set "
            "ALLOW_DESTRUCTIVE_TEST_DB=1 only after verifying TEST_DATABASE_URL "
            "points to an empty, disposable PostgreSQL 16 test database."
        )
    return TEST_DATABASE_URL


@pytest.fixture(scope="session")
def migrated_engine() -> Iterator[Engine]:
    url = _require_url()
    engine = create_engine(url)
    migrated = False
    try:
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

        command.upgrade(alembic_config(url), "head")
        migrated = True
        yield engine
    finally:
        try:
            if migrated:
                # Destructive by design; _require_url requires explicit owner acknowledgement.
                command.downgrade(alembic_config(url), "base")
        finally:
            engine.dispose()


@pytest.fixture
def conn(migrated_engine: Engine) -> Iterator[Connection]:
    """A connection whose work is rolled back after each test."""
    with migrated_engine.connect() as connection:
        outer = connection.begin()
        yield connection
        outer.rollback()


def sibling_database_url(url: str, suffix: str) -> str:
    """Create a unique sibling database URL; never reuse a predictable database name."""
    parsed = make_url(url)
    if not parsed.database:
        raise ValueError("TEST_DATABASE_URL must include an explicit database name")
    safe_suffix = re.sub(r"[^a-z0-9_]+", "_", suffix.lower()).strip("_")
    if not safe_suffix:
        raise ValueError("A non-empty, identifier-safe database suffix is required")
    unique_suffix = f"_{safe_suffix}_{uuid.uuid4().hex[:12]}"
    database_name = f"{parsed.database[: 63 - len(unique_suffix)]}{unique_suffix}"
    return parsed.set(database=database_name).render_as_string(hide_password=False)


@pytest.fixture
def db_session(migrated_engine: Engine) -> Iterator["Session"]:
    """Yield a Session isolated by an outer transaction owned by this fixture.

    The Session is bound to the same connection as the outer transaction.
    Session commits release only their savepoint; fixture teardown rolls back
    the outer transaction and independently verifies registered User emails
    through a newly acquired PostgreSQL connection.
    """
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from app.persistence.models.identity import User

    rollback_emails: list[str] = []

    with migrated_engine.connect() as connection:
        outer_transaction = connection.begin()
        session = Session(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        session.info["rollback_verification_emails"] = rollback_emails

        try:
            yield session
        finally:
            try:
                session.close()
            finally:
                try:
                    if outer_transaction.is_active:
                        outer_transaction.rollback()
                finally:
                    if rollback_emails:
                        with migrated_engine.connect() as verification_connection:
                            for email in rollback_emails:
                                remaining = verification_connection.scalar(
                                    select(func.count())
                                    .select_from(User)
                                    .where(User.email == email)
                                )
                                if remaining != 0:
                                    pytest.fail(
                                        "Database transaction rollback verification failed: "
                                        f"email={email!r}, remaining_records={remaining!r}"
                                    )
