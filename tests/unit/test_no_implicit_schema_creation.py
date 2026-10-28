"""Alembic owns the schema: application code must never create tables itself."""

from pathlib import Path


def test_application_code_never_calls_create_all() -> None:
    offenders = [
        str(path) for path in Path("app").rglob("*.py") if "create_all" in path.read_text("utf-8")
    ]
    assert offenders == []
