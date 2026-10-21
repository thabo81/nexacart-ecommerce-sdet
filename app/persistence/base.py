"""Declarative base shared by all models. Models and constraint names arrive with DATA-001."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
