"""Deterministic identity: every seed-owned row id is UUIDv5(namespace, '<kind>:<natural key>')."""

import uuid

from app.seed.constants import SEED_NAMESPACE


def seed_id(kind: str, key: str) -> uuid.UUID:
    return uuid.uuid5(SEED_NAMESPACE, f"{kind}:{key}")
