"""Fixed identity namespace and baseline timestamps. Changing these changes every seed ID."""

import uuid
from datetime import UTC, datetime, timedelta

# Namespace for every seed-owned UUIDv5. Never change: IDs are the seed ownership boundary.
SEED_NAMESPACE = uuid.UUID("6e0c4f0e-3a53-5b0e-9d6e-4e7a1c2b9a01")

# All seed-owned timestamps derive from this fixed instant so repeated runs are identical.
SEED_EPOCH = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
FAR_FUTURE = datetime(2099, 12, 31, 0, 0, 0, tzinfo=UTC)

COUNTRY_CODE = "ZA"

# Test-created records (TR-016) carry these prefixes; reset treats them as disposable.
QA_EMAIL_PREFIX = "qa_"
QA_SLUG_PREFIX = "qa-"  # slugs/SKUs: underscore is not allowed in slugs
QA_COUPON_PREFIX = "QA_"


def at(days: float = 0, hours: float = 0, minutes: float = 0) -> datetime:
    return SEED_EPOCH + timedelta(days=days, hours=hours, minutes=minutes)


def rand(amount: float) -> int:
    """Rand amount to integer minor units (cents), exact for 2-decimal literals."""
    return round(amount * 100)
