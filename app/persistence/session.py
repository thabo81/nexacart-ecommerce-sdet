"""Engine and session factories. Sessions are scoped to a request or a worker task."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings

# Fail fast when PostgreSQL is unreachable so readiness reports promptly.
DB_CONNECT_TIMEOUT_SECONDS = 3


def create_db_engine(settings: Settings) -> Engine:
    """Create an engine lazily; no connection is opened until first use."""
    return create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        connect_args={"connect_timeout": DB_CONNECT_TIMEOUT_SECONDS},
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
