"""Shared pytest configuration. Fixtures for HTTPX, Playwright, SQL, users and clock: TEST-002."""

from collections.abc import Callable, Iterator
from typing import Any

import pytest

from app.core.config import Settings, get_settings

AREAS = {"unit", "api", "ui", "integration", "database", "bdd"}


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Tag each test with the marker matching its tests/<area>/ directory."""
    for item in items:
        parts = item.path.parts
        if "tests" in parts:
            area = parts[parts.index("tests") + 1]
            if area in AREAS:
                item.add_marker(getattr(pytest.mark, area))


PLACEHOLDER_DB_URL = "postgresql+psycopg://test:placeholder@localhost:5432/test"


@pytest.fixture
def settings_factory() -> Iterator[Callable[..., Settings]]:
    """Build Settings with overrides, e.g. settings_factory(page_size_max=20)."""
    get_settings.cache_clear()

    def make(**overrides: Any) -> Settings:
        values: dict[str, Any] = {"app_env": "test", "database_url": PLACEHOLDER_DB_URL}
        return Settings(**{**values, **overrides})

    yield make
    get_settings.cache_clear()


@pytest.fixture
def settings() -> Iterator[Settings]:
    """Settings with a placeholder DB URL; the engine is lazy, so nothing connects."""
    get_settings.cache_clear()
    yield Settings(
        app_env="test",
        database_url="postgresql+psycopg://test:placeholder@localhost:5432/test",
    )
    get_settings.cache_clear()


@pytest.fixture
def unreachable_settings() -> Iterator[Settings]:
    """Settings pointing at a closed local port: connection is refused immediately."""
    get_settings.cache_clear()
    yield Settings(
        app_env="test",
        database_url="postgresql+psycopg://test:placeholder@127.0.0.1:1/test",
    )
    get_settings.cache_clear()
