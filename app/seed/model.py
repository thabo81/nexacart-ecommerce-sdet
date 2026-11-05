"""Plain dataclasses describing seed data (no database imports)."""

import json
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CategorySpec:
    slug: str
    name: str
    description: str
    sort_order: int
    parent_slug: str | None = None
    small_goods: bool = False


@dataclass(frozen=True)
class VariantSpec:
    price_minor: int
    stock: int  # baseline (final) stock visible to tests
    options: tuple[tuple[str, str], ...] = ()
    active: bool = True

    @property
    def is_default(self) -> bool:
        return not self.options


@dataclass(frozen=True)
class ProductSpec:
    code: str  # stable product code, e.g. CMP-001 (base SKU = NC-<code>)
    sub: str  # subcategory slug
    slug: str
    name: str
    brand: str
    description: str
    specs: tuple[tuple[str, str], ...]
    variants: tuple[VariantSpec, ...]
    featured: bool = False
    active: bool = True
    fixture: str | None = None
    alt_image: bool = False

    @property
    def base_sku(self) -> str:
        return f"NC-{self.code}"


def V(price_minor: int, stock: int, *, active: bool = True, **options: str) -> VariantSpec:
    return VariantSpec(price_minor, stock, tuple(sorted(options.items())), active)


def options_key(options: tuple[tuple[str, str], ...]) -> str:
    """Canonical, whitespace-normalised, key-sorted JSON; '{}' for the default variant."""
    normalised = {k.strip().lower(): v.strip() for k, v in options}
    return json.dumps(normalised, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def variant_sku(base_sku: str, options: tuple[tuple[str, str], ...]) -> str:
    if not options:
        return f"{base_sku}-DEF"
    parts = []
    for _, value in options:
        cleaned = "".join(ch if ch.isalnum() else "" for ch in value.upper())
        parts.append(cleaned)
    return f"{base_sku}-{'-'.join(parts)}"


def variant_label(options: tuple[tuple[str, str], ...]) -> str:
    if not options:
        return "Default"
    return ", ".join(f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in options)


@dataclass(frozen=True)
class ReviewSpec:
    reviewer: str  # reviewer key, e.g. "r1"
    product_slug: str
    rating: int
    comment: str | None = None


@dataclass(frozen=True)
class OrderLineSpec:
    product_slug: str
    options: tuple[tuple[str, str], ...]
    quantity: int


@dataclass(frozen=True)
class OrderSpec:
    key: str
    number: str  # NC-YYYYMMDD-NNNNNN (seed range 9xxxxx)
    customer: str  # account key
    status: str
    day: float  # placed_at = epoch + day
    lines: tuple[OrderLineSpec, ...]
    shipping_fee_minor: int
    shipping_code: str = "standard"


@dataclass(frozen=True)
class AccountSpec:
    key: str
    email: str
    name: str
    role: str
    phone: str | None
    password_var: str  # SeedSettings attribute holding the local/test password
    has_address: bool = False


@dataclass
class Dataset:
    categories: list[CategorySpec] = field(default_factory=list)
    products: list[ProductSpec] = field(default_factory=list)
