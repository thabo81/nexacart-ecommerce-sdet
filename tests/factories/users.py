"""Synthetic User factory for PostgreSQL-backed tests."""

from typing import Literal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.persistence.models.identity import User

# Deliberately not a valid Argon2id hash. This value is only for database tests
# that never authenticate the synthetic user.
TEST_ONLY_PASSWORD_HASH = "test-only-placeholder-not-a-real-password-hash"
ROLLBACK_VERIFICATION_EMAILS_KEY = "rollback_verification_emails"


def create_user(
    session: Session,
    *,
    name: str = "NexaCart Canary User",
    email: str | None = None,
    password_hash: str = TEST_ONLY_PASSWORD_HASH,
    phone: str | None = None,
    role: Literal["customer", "admin"] = "customer",
    is_active: bool = True,
) -> User:
    """Add and flush a valid synthetic User without committing the Session.

    When used with the db_session fixture, the unique email is registered
    for independent post-rollback verification by that fixture.
    """
    normalized_email = (email or f"canary-{uuid4().hex}@example.test").strip().lower()
    user = User(
        name=name,
        email=normalized_email,
        password_hash=password_hash,
        phone=phone,
        role=role,
        is_active=is_active,
    )
    session.add(user)
    session.flush()

    verification_emails = session.info.get(ROLLBACK_VERIFICATION_EMAILS_KEY)
    if verification_emails is not None:
        verification_emails.append(user.email)

    return user
