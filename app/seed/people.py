"""Seeded accounts, order histories and R1 review data. No coupon usages are seeded."""

from decimal import ROUND_HALF_UP, Decimal

from app.seed.model import AccountSpec, OrderLineSpec, OrderSpec, ReviewSpec

DOMAIN = "nexacart.test"

ACCOUNTS = (
    AccountSpec("admin", f"admin@{DOMAIN}", "Seed Admin", "admin", None, "seed_password_admin"),
    AccountSpec(
        "customer",
        f"customer@{DOMAIN}",
        "Sam First-Time Buyer",
        "customer",
        "+27110000001",
        "seed_password_customer",
        True,
    ),
    AccountSpec(
        "history",
        f"history@{DOMAIN}",
        "Hannah Returning",
        "customer",
        "+27110000002",
        "seed_password_history",
        True,
    ),
    AccountSpec(
        "r1", f"reviewer@{DOMAIN}", "Reviewer One", "customer", None, "seed_password_reviewer"
    ),
    AccountSpec(
        "r2", f"reviewer2@{DOMAIN}", "Reviewer Two", "customer", None, "seed_password_reviewer"
    ),
    AccountSpec(
        "r3", f"reviewer3@{DOMAIN}", "Reviewer Three", "customer", None, "seed_password_reviewer"
    ),
    AccountSpec(
        "r4", f"reviewer4@{DOMAIN}", "Reviewer Four", "customer", None, "seed_password_reviewer"
    ),
    AccountSpec(
        "r5", f"reviewer5@{DOMAIN}", "Reviewer Five", "customer", None, "seed_password_reviewer"
    ),
)

# Saved delivery address (synthetic, fictional street).
ADDRESS = {
    "recipient_name": "Seed Recipient",
    "phone": "+27110000009",
    "line1": "1 Fixture Street",
    "line2": None,
    "city": "Johannesburg",
    "province": "Gauteng",
    "postal_code": "2196",
}

_NO: tuple[tuple[str, str], ...] = ()


def L(slug: str, qty: int = 1, **options: str) -> OrderLineSpec:
    return OrderLineSpec(slug, tuple(sorted(options.items())), qty)


_SONIC = "fx-many-reviews-sonic-studio-headphones"
_BUDS = "samsung-galaxy-buds-fe"
_PEBBLE = "pebble-mini-bluetooth-speaker"
_BAND = "xiaomi-smart-band-8"
_DURAMO = "adidas-duramo-sl"
_SMASH = "puma-smash-v2"
_AF1 = "nike-air-force-1-07"

REVIEWER_LINES = {
    "r1": (
        L(_SONIC, colour="Black"),
        L(_BUDS, colour="Graphite"),
        L(_PEBBLE, colour="Teal"),
        L(_BAND, colour="Black"),
    ),
    "r2": (
        L(_SONIC, colour="Black"),
        L(_BUDS, colour="Graphite"),
        L(_PEBBLE, colour="Teal"),
        L(_SMASH, colour="Black", size="UK 8"),
    ),
    "r3": (
        L(_SONIC, colour="Black"),
        L(_BUDS, colour="Graphite"),
        L(_DURAMO, colour="Grey", size="UK 8"),
        L(_SMASH, colour="Black", size="UK 8"),
    ),
    "r4": (
        L(_SONIC, colour="Black"),
        L(_BUDS, colour="Graphite"),
        L(_SMASH, colour="Black", size="UK 8"),
    ),
    "r5": (
        L(_SONIC, colour="Black"),
        L(_BAND, colour="Black"),
        L(_AF1, colour="White", size="UK 8"),
    ),
}
# Subtotals (R): r1 6696, r2 6896, r3 7396, r4 6297, r5 6597: all >= R1,000, so fee R60.
_REVIEWER_DAYS = {"r1": 100, "r2": 101, "r3": 102, "r4": 103, "r5": 104}


def _hist(i: int, status: str, day: int, fee: int, *lines: OrderLineSpec) -> OrderSpec:
    return OrderSpec(f"history-{i}", "", "history", status, day, tuple(lines), fee)


_ORDERS_RAW: tuple[OrderSpec, ...] = (
    *(
        OrderSpec(f"{r}-delivered", "", r, "delivered", _REVIEWER_DAYS[r], REVIEWER_LINES[r], 6000)
        for r in ("r1", "r2", "r3", "r4", "r5")
    ),
    # First non-cancelled order, subtotal R638.99 in the free-shipping band -> fee 0 (BR-076).
    _hist(1, "delivered", 190, 0, L(_PEBBLE, colour="Teal"), L("fx-small-goods-ear-tips-set")),
    _hist(2, "shipped", 232, 6000, L(_DURAMO, colour="Grey", size="UK 9")),
    _hist(3, "processing", 257, 6000, L(_BUDS, colour="Graphite")),
    _hist(
        4,
        "confirmed",
        282,
        6000,
        L("apex-gaming-headset-71", colour="Black"),
        L("fx-price-249-99-matchday-fan-scarf", colour="Red"),
    ),
    _hist(5, "cancelled", 290, 6000, L("samsung-galaxy-a15", colour="Blue Black")),
    _hist(6, "pending", 304, 6000, L("pulse-watch-lite", colour="Black")),
)


def orders() -> tuple[OrderSpec, ...]:
    from app.seed.constants import at

    numbered = []
    for index, order in enumerate(_ORDERS_RAW, start=1):
        number = f"NC-{at(order.day):%Y%m%d}-9{index:05d}"
        numbered.append(
            OrderSpec(
                order.key,
                number,
                order.customer,
                order.status,
                order.day,
                order.lines,
                order.shipping_fee_minor,
                order.shipping_code,
            )
        )
    return tuple(numbered)


REVIEWS = (
    # Many reviews: 5 reviews, sum 21 -> 4.2
    ReviewSpec("r1", _SONIC, 5, "Great sound and long battery."),
    ReviewSpec("r2", _SONIC, 5, "Comfortable for long sessions."),
    ReviewSpec("r3", _SONIC, 4, "Solid build."),
    ReviewSpec("r4", _SONIC, 4, "Good value."),
    ReviewSpec("r5", _SONIC, 3, "Okay, ear cups run warm."),
    # Half-up boundary: 4 reviews, sum 17 -> 4.25 -> 4.3
    ReviewSpec("r1", _BUDS, 5, "Fit is great."),
    ReviewSpec("r2", _BUDS, 4, None),
    ReviewSpec("r3", _BUDS, 4, "Noise cancelling is decent."),
    ReviewSpec("r4", _BUDS, 4, None),
    # 2 reviews -> 4.5
    ReviewSpec("r1", _PEBBLE, 5, "Tiny but loud."),
    ReviewSpec("r2", _PEBBLE, 4, "Good for the price."),
    # 1 review -> 3.0
    ReviewSpec("r3", _DURAMO, 3, "Fine for easy runs."),
    # 3 reviews -> 4.0 (ties with 2-review 4.0 below)
    ReviewSpec("r2", _SMASH, 4, None),
    ReviewSpec("r3", _SMASH, 4, 'Comfortable & stylish "clean" look.'),
    ReviewSpec("r4", _SMASH, 4, None),
    # 2 reviews -> 4.0
    ReviewSpec("r1", _BAND, 4, "Battery lasts ages."),
    ReviewSpec("r5", _BAND, 4, None),
    # 1 review -> 5.0
    ReviewSpec("r5", _AF1, 5, "Classic."),
)


def aggregate(ratings: list[int]) -> tuple[Decimal, int]:
    if not ratings:
        return Decimal("0.0"), 0
    mean = Decimal(sum(ratings)) / Decimal(len(ratings))
    return mean.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP), len(ratings)
