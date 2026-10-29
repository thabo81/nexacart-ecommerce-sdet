"""Declarative base shared by all models.

Primary-key and foreign-key names follow the approved convention
(``pk_<table>``, ``fk_<table>_<column>_<target>``). Every CHECK, unique constraint and index is
named explicitly in the model, so the CHECK convention only echoes the explicit name.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "ck": "%(constraint_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map = {  # noqa: RUF012
        uuid.UUID: UUID(as_uuid=True),
        datetime: DateTime(timezone=True),
    }
