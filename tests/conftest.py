"""Shared pytest configuration. Fixtures for HTTPX, Playwright, SQL, users and clock: TEST-002."""

from collections.abc import Iterator

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


@pytest.fixture
def settings() -> Iterator[Settings]:
    """Settings with a placeholder DB URL; the engine is lazy, so nothing connects."""
    get_settings.cache_clear()
    yield Settings(
        app_env="test",
        database_url="postgresql+psycopg://test:placeholder@localhost:5432/test",
    )
    get_settings.cache_clear()
