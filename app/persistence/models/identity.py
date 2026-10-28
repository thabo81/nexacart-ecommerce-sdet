"""Identity and session security tables (ERD §3.1)."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base
from app.persistence.models._common import (
    HEX64_PATTERN,
    PHONE_PATTERN,
    bool_col,
    created_at,
    in_list,
    optional_ts,
    updated_at,
    uuid_pk,
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint("btrim(name) <> ''", name="ck_users_name_nonblank"),
        CheckConstraint("email = lower(btrim(email))", name="ck_users_email_normalized"),
        CheckConstraint(in_list("role", ("customer", "admin")), name="ck_users_role"),
        CheckConstraint(
            f"phone IS NULL OR phone ~ '{PHONE_PATTERN}'", name="ck_users_phone_format"
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254))
    password_hash: Mapped[str] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(16))
    role: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = bool_col(default=True)
    created_at: Mapped[datetime] = created_at()
    updated_at: Mapped[datetime] = updated_at()
    password_changed_at: Mapped[datetime | None] = optional_ts()


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        CheckConstraint(
            f"csrf_token_hash ~ '{HEX64_PATTERN}'", name="ck_auth_sessions_csrf_token_hash_format"
        ),
        CheckConstraint("expires_at > issued_at", name="ck_auth_sessions_expiry_after_issue"),
        Index("ix_auth_sessions_user_id", "user_id"),
        Index("ix_auth_sessions_expires_at", "expires_at"),
    )

    jti: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    issued_at: Mapped[datetime]
    expires_at: Mapped[datetime]
    revoked_at: Mapped[datetime | None] = optional_ts()
    revocation_reason: Mapped[str | None] = mapped_column(String(100))
    csrf_token_hash: Mapped[str] = mapped_column(CHAR(64))
    created_at: Mapped[datetime] = created_at()


class LoginThrottleState(Base):
    __tablename__ = "login_throttle_state"
    __table_args__ = (
        CheckConstraint("consecutive_failures >= 0", name="ck_login_throttle_failures_nonnegative"),
    )

    email_key: Mapped[str] = mapped_column(String(254), primary_key=True)
    consecutive_failures: Mapped[int] = mapped_column(server_default=text("0"))
    locked_until: Mapped[datetime | None] = optional_ts()
    updated_at: Mapped[datetime] = updated_at()
