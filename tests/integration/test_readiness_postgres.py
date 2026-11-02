"""Readiness against a real PostgreSQL. Skipped unless NEXACART_TEST_DATABASE_URL is set.

Example (placeholder credentials):
  NEXACART_TEST_DATABASE_URL=postgresql+psycopg://user:pass@localhost/db pytest -m integration
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import Settings
from app.main import create_app

DATABASE_URL = os.environ.get("NEXACART_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="NEXACART_TEST_DATABASE_URL not set")


def test_readiness_is_200_against_real_postgresql() -> None:
    assert DATABASE_URL
    settings = Settings(app_env="test", database_url=DATABASE_URL)
    app = create_app(settings)
    with TestClient(app) as client:
        assert client.get("/health/ready").status_code == 200
        with app.state.engine.connect() as connection:
            assert connection.execute(text("show server_version")).scalar_one().startswith("16.")
