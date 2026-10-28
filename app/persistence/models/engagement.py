"""Reviews and R3 notifications (ERD §3.7)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base
from app.persistence.models._common import bool_col, created_at, in_list, optional_ts, uuid_pk

NOTIFICATION_TYPES = (
    "order_confirmed",
    "payment_failed",
    "order_status_changed",
    "order_cancelled",
    "refund_completed",
)


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("customer_id", "product_id", name="uq_review_customer_product"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_range"),
        CheckConstraint(
            "comment IS NULL OR char_length(comment) <= 1000", name="ck_reviews_comment_length"
        ),
        CheckConstraint(
            "(NOT is_hidden AND hidden_by_user_id IS NULL AND hidden_at IS NULL)"
            " OR (is_hidden AND hidden_by_user_id IS NOT NULL AND hidden_at IS NOT NULL)",
            name="ck_reviews_hidden_metadata_consistency",
        ),
        Index("ix_reviews_product_created", "product_id", "is_hidden", text("created_at DESC")),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    verified_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"))
    rating: Mapped[int] = mapped_column(SmallInteger)
    comment: Mapped[str | None] = mapped_column(String(1000))
    is_hidden: Mapped[bool] = bool_col(default=False)
    hidden_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    hidden_at: Mapped[datetime | None] = optional_ts()
    created_at: Mapped[datetime] = created_at()


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            in_list("notification_type", NOTIFICATION_TYPES), name="ck_notifications_type"
        ),
        Index("ix_notifications_customer_created", "customer_id", text("created_at DESC")),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    notification_type: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = created_at()
    read_at: Mapped[datetime | None] = optional_ts()
