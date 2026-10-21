"""Engine and session factories. Sessions are scoped to a request or a worker task."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


def create_db_engine(settings: Settings) -> Engine:
    """Create an engine lazily; no connection is opened until first use."""
    return create_engine(settings.database_url.get_secret_value(), pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
