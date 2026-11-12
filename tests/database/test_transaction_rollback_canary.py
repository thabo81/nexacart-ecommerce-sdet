"""Canary proving synchronous SQLAlchemy writes roll back after test teardown."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.identity import User
from tests.factories import create_user


def test_user_insert_is_rolled_back_after_test_teardown(db_session: Session) -> None:
    """A committed Session savepoint must not commit the fixture outer transaction."""
    user = create_user(db_session)
    unique_email = user.email

    # PostgreSQL generated the UUID and the uncommitted row is visible in this transaction.
    assert isinstance(user.id, uuid.UUID)
    assert db_session.scalar(select(User.id).where(User.email == unique_email)) == user.id

    # This commits the Session savepoint, not the fixture-owned outer transaction.
    db_session.commit()

    # The row remains visible on the original transaction connection.
    assert db_session.scalar(select(User.id).where(User.email == unique_email)) == user.id

    # db_session teardown closes the Session, rolls back the outer transaction,
    # then checks this email using a fresh PostgreSQL connection.
