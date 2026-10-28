"""Column helpers and shared constraint fragments for the persistence models."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

ORDER_STATUSES = ("pending", "confirmed", "processing", "shipped", "delivered", "cancelled")
IDEMPOTENCY_KEY_PATTERN = r"^[A-Za-z0-9_-]{8,64}$"
PHONE_PATTERN = r"^\+?[0-9]{7,15}$"
SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
HEX64_PATTERN = r"^[0-9a-f]{64}$"


def in_list(column: str, values: tuple[str, ...]) -> str:
    quoted = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({quoted})"


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))


def created_at() -> Mapped[datetime]:
    return mapped_column(server_default=text("now()"))


def updated_at() -> Mapped[datetime]:
    return mapped_column(server_default=text("now()"))


def optional_ts() -> Mapped[datetime | None]:
    return mapped_column(nullable=True)


def bool_col(default: bool | None = None) -> Mapped[bool]:
    if default is None:
        return mapped_column()
    return mapped_column(server_default=text("true" if default else "false"))


def table_args(*items: Any) -> tuple[Any, ...]:
    return tuple(items)
