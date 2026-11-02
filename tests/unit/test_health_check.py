"""database_is_reachable: true for a working engine, false (no exception) otherwise."""

from sqlalchemy import create_engine

from app.core.config import Settings
from app.core.observability.health import database_is_reachable
from app.persistence.session import create_db_engine


def test_reachable_engine_is_reported_reachable() -> None:
    assert database_is_reachable(create_engine("sqlite://")) is True


def test_unreachable_database_is_reported_not_reachable(unreachable_settings: Settings) -> None:
    assert database_is_reachable(create_db_engine(unreachable_settings)) is False
