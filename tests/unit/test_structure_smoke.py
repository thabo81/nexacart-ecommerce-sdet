"""FOUND-001 structure smoke tests: configuration, entry points and persistence boundary."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.persistence.base import Base
from app.persistence.session import create_db_engine, create_session_factory
from app.worker.__main__ import main as worker_main


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


def test_worker_entry_point_runs_and_exits(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:placeholder@localhost/test")
    monkeypatch.setenv("APP_ENV", "test")
    from app.core.config import get_settings

    get_settings.cache_clear()
    with caplog.at_level("INFO", logger="nexacart.worker"):
        worker_main()
    get_settings.cache_clear()
    assert "worker started" in caplog.text
