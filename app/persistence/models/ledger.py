"""Idempotency, inventory ledger and audit tables (ERD §3.6)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CHAR,
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
from app.persistence.models._common import (
    HEX64_PATTERN,
    IDEMPOTENCY_KEY_PATTERN,
    created_at,
    in_list,
    uuid_pk,
)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("customer_id", "scope", "key_value", name="uq_idempotency_scope_key"),
        CheckConstraint("btrim(scope) <> ''", name="ck_idempotency_records_scope_nonblank"),
        CheckConstraint(
            f"key_value ~ '{IDEMPOTENCY_KEY_PATTERN}'", name="ck_idempotency_records_key_format"
        ),
        CheckConstraint(
            f"request_fingerprint ~ '{HEX64_PATTERN}'",
            name="ck_idempotency_records_fingerprint_format",
        ),
        CheckConstraint(
            "response_status BETWEEN 100 AND 599", name="ck_idempotency_records_response_status"
        ),
        CheckConstraint(
            "expires_at >= created_at + interval '24 hours'",
            name="ck_idempotency_records_retention",
        ),
        Index("ix_idempotency_records_expires_at", "expires_at"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    scope: Mapped[str] = mapped_column(String(100))
    key_value: Mapped[str] = mapped_column(String(64))
    request_fingerprint: Mapped[str] = mapped_column(CHAR(64))
    response_status: Mapped[int] = mapped_column(SmallInteger)
    response_body: Mapped[dict[str, Any]] = mapped_column(JSONB)
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"))
    created_at: Mapped[datetime] = created_at()
    expires_at: Mapped[datetime]


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    __table_args__ = (
        UniqueConstraint("operation_key", name="uq_inventory_operation_key"),
        CheckConstraint("delta_quantity <> 0", name="ck_inventory_movements_delta_nonzero"),
        CheckConstraint(
            in_list(
                "reason_code",
                (
                    "initial_stock",
                    "order_placed",
                    "order_cancelled",
                    "reservation_expired",
                    "admin_adjustment",
                ),
            ),
            name="ck_inventory_movements_reason_code",
        ),
        CheckConstraint(
            "btrim(operation_key) <> ''", name="ck_inventory_movements_operation_key_nonblank"
        ),
        CheckConstraint(
            "reason_code <> 'admin_adjustment'"
            " OR (reason_text IS NOT NULL AND char_length(btrim(reason_text)) BETWEEN 1 AND 200)",
            name="ck_inventory_movements_admin_reason",
        ),
        Index("ix_inventory_movements_variant_time", "variant_id", "occurred_at"),
        Index("ix_inventory_movements_reference", "reference_type", "reference_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product_variants.id"))
    delta_quantity: Mapped[int]
    reason_code: Mapped[str] = mapped_column(Text)
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"))
    order_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("order_items.id"))
    reference_type: Mapped[str] = mapped_column(Text)
    reference_id: Mapped[uuid.UUID | None]
    operation_key: Mapped[str] = mapped_column(String(160))
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    reason_text: Mapped[str | None] = mapped_column(String(200))
    occurred_at: Mapped[datetime]


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        CheckConstraint("btrim(action) <> ''", name="ck_audit_events_action_nonblank"),
        CheckConstraint("btrim(entity_type) <> ''", name="ck_audit_events_entity_type_nonblank"),
        CheckConstraint(
            in_list("actor_role", ("customer", "admin", "system")),
            name="ck_audit_events_actor_role",
        ),
        Index("ix_audit_events_occurred_at", text("occurred_at DESC")),
        Index("ix_audit_events_actor_time", "actor_user_id", text("occurred_at DESC")),
        Index("ix_audit_events_action_time", "action", text("occurred_at DESC")),
        Index("ix_audit_events_entity_time", "entity_type", "entity_id", text("occurred_at DESC")),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    actor_role: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(String(100))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[uuid.UUID | None]
    before_summary: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after_summary: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    request_id: Mapped[str] = mapped_column(String(100))
    occurred_at: Mapped[datetime]
