"""Assembles the complete product catalogue and derives text/asset fields."""

from app.seed import (
    products_computers,
    products_football,
    products_phones,
    products_shoes,
    products_wearables,
)
from app.seed.model import ProductSpec
from app.seed.taxonomy import (
    COMPUTERS,
    FOOTBALL,
    PHONES,
    SHOES,
    WEARABLES,
    parent_of,
)

DEMO_NOTICE = "Demo listing: synthetic product data, not a real offer."
FOOTBALL_NOTICE = (
    "Fictional, unofficial demonstration listing. Not endorsed by or affiliated with any club, "
    "national association or brand."
)

# Price bands in minor units (PRD §5.1): budget < lower; mid lower..upper; premium > upper.
BANDS: dict[str, tuple[int, int]] = {
    COMPUTERS: (1_000_000, 3_000_000),
    PHONES: (400_000, 1_500_000),
    WEARABLES: (100_000, 400_000),
    FOOTBALL: (60_000, 150_000),
    SHOES: (120_000, 250_000),
}


def all_products() -> list[ProductSpec]:
    return [
        *products_computers.products(),
        *products_phones.products(),
        *products_wearables.products(),
        *products_football.products(),
        *products_shoes.products(),
    ]


def top_category(product: ProductSpec) -> str:
    return parent_of(product.sub)


def full_description(product: ProductSpec) -> str:
    notice = FOOTBALL_NOTICE if top_category(product) == FOOTBALL else DEMO_NOTICE
    return f"{product.description} {notice}"


def tier(category: str, price_minor: int) -> str:
    low, high = BANDS[category]
    if price_minor < low:
        return "budget"
    return "mid" if price_minor <= high else "premium"


def product_tier(product: ProductSpec) -> str | None:
    """Single tier if every variant is in the same band, else None."""
    tiers = {tier(top_category(product), v.price_minor) for v in product.variants}
    return tiers.pop() if len(tiers) == 1 else None


def asset_keys(product: ProductSpec) -> list[str]:
    keys = [f"products/{product.slug}-main"]
    if product.alt_image or (len(product.variants) > 1 and product.featured):
        keys.append(f"products/{product.slug}-alt")
    return keys


PLACEHOLDER_KEY = "placeholders/product"
