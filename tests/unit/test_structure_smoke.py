"""FOUND-001 structure smoke tests: configuration, entry points and persistence boundary."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.persistence.base import Base
from app.persistence.session import create_db_engine, create_session_factory


def test_database_url_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_database_url_is_not_exposed_in_repr(settings: Settings) -> None:
    assert "placeholder" not in repr(settings)


def test_engine_and_session_factory_are_lazy(settings: Settings) -> None:
    engine = create_db_engine(settings)
    factory = create_session_factory(engine)
    assert engine.dialect.name == "postgresql"
    assert factory.kw["bind"] is engine


def test_base_metadata_has_no_tables_before_data_001() -> None:
    assert not Base.metadata.tables
