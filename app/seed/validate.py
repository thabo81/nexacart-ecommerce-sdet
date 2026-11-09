"""Static, database-free checks of the dataset against DATA-002 rules."""

import re
from collections import Counter

from app.seed import catalogue, people
from app.seed.model import ProductSpec, options_key, variant_sku
from app.seed.taxonomy import WEARABLES, build_categories

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REQUIRED_PRICES = {99999, 100000, 50000, 25000, 24999, 80000, 80001}


def validate_dataset() -> list[str]:
    errors: list[str] = []
    products = catalogue.all_products()
    cats = build_categories()
    tops = [c for c in cats if c.parent_slug is None]
    if len(tops) != 5:
        errors.append(f"expected 5 top-level categories, found {len(tops)}")
    for top in tops:
        subs = [c for c in cats if c.parent_slug == top.slug]
        if len(subs) < 2:
            errors.append(f"{top.slug}: fewer than 2 subcategories")
        mine = [p for p in products if catalogue.top_category(p) == top.slug]
        if len(mine) < 12:
            errors.append(f"{top.slug}: {len(mine)} products (<12)")
        tiers = Counter(catalogue.product_tier(p) for p in mine)
        for t in ("budget", "mid", "premium"):
            if tiers[t] < 3:
                errors.append(f"{top.slug}: only {tiers[t]} {t} products")
        if None in tiers:
            errors.append(f"{top.slug}: product with variants spanning price tiers")
    if len(products) < 60:
        errors.append(f"only {len(products)} products")
    if sum(len(p.variants) > 1 for p in products) * 2 < len(products):
        errors.append("fewer than 50% of products have multiple variants")
    for name, items in (
        ("slug", [p.slug for p in products]),
        ("sku", [p.base_sku for p in products]),
        ("variant sku", [variant_sku(p.base_sku, v.options) for p in products for v in p.variants]),
    ):
        dup = [k for k, n in Counter(items).items() if n > 1]
        if dup:
            errors.append(f"duplicate {name}: {dup[:3]}")
    for p in products:
        if not SLUG.match(p.slug) or len(p.slug) > 160:
            errors.append(f"bad slug {p.slug}")
        if len(p.name) > 200 or len(catalogue.full_description(p)) > 5000 or len(p.brand) > 100:
            errors.append(f"field limit exceeded: {p.slug}")
        if len(f"{p.name} — alternate view") > 250:
            errors.append(f"alt text too long: {p.slug}")
        keys = [options_key(v.options) for v in p.variants]
        if len(set(keys)) != len(keys):
            errors.append(f"duplicate option set: {p.slug}")
        if any(v.is_default for v in p.variants) and len(p.variants) != 1:
            errors.append(f"default variant mixed with others: {p.slug}")
        if any(v.price_minor <= 0 or v.stock < 0 for v in p.variants):
            errors.append(f"invalid price/stock: {p.slug}")
    prices = {v.price_minor for p in products for v in p.variants}
    if not prices >= REQUIRED_PRICES:
        errors.append(f"missing boundary prices: {sorted(REQUIRED_PRICES - prices)}")
    by_fix: dict[str, list[ProductSpec]] = {}
    for p in products:
        if p.fixture:
            by_fix.setdefault(p.fixture, []).append(p)
    for need in (
        "out-of-stock",
        "single-unit",
        "low-stock-boundary",
        "inactive",
        "partial-availability",
        "single-variant",
        "no-reviews",
        "many-reviews",
        "small-goods",
        "non-small-goods",
        "long-name",
    ):
        if need not in by_fix:
            errors.append(f"missing fixture {need}")
    if by_fix.get("out-of-stock") and any(
        v.stock for p in by_fix["out-of-stock"] for v in p.variants if v.active
    ):
        errors.append("out-of-stock fixture has stock")
    if by_fix.get("low-stock-boundary") and {
        v.stock for p in by_fix["low-stock-boundary"] for v in p.variants
    } != {5, 6}:
        errors.append("low-stock fixture must have exactly stocks 5 and 6")
    if by_fix.get("inactive") and any(p.active for p in by_fix["inactive"]):
        errors.append("inactive fixture is active")
    for p in by_fix.get("partial-availability", []):
        if {v.stock == 0 for v in p.variants} != {True, False}:
            errors.append("partial-availability fixture needs one zero and one in-stock variant")
    for p in by_fix.get("single-variant", []):
        if len(p.variants) != 1 or not p.variants[0].is_default:
            errors.append("single-variant fixture must have exactly one default variant")
    for p in by_fix.get("single-unit", []):
        if [v.stock for v in p.variants] != [1]:
            errors.append("single-unit fixture must have stock 1")
    for p in by_fix.get("small-goods", []):
        if (
            catalogue.top_category(p) != WEARABLES
            or max(v.price_minor for v in p.variants) * 4 >= 25000
            or min(v.stock for v in p.variants) < 4
        ):
            errors.append(f"small-goods fixture invalid: {p.slug}")
    for p in by_fix.get("non-small-goods", []):
        if catalogue.top_category(p) == WEARABLES or any(
            v.price_minor >= 25000 for v in p.variants
        ):
            errors.append(f"non-small-goods fixture invalid: {p.slug}")
    for p in by_fix.get("long-name", []):
        if not (
            190 <= len(p.name) <= 200 and "&" in p.name and '"' in p.name and not p.name.isascii()
        ):
            errors.append("long-name fixture must be near 200 chars with &, quotes, non-ASCII")
    no_review = by_fix["no-reviews"][0].slug if by_fix.get("no-reviews") else ""
    if any(r.product_slug == no_review for r in people.REVIEWS):
        errors.append("no-reviews fixture has reviews")
    many = by_fix["many-reviews"][0].slug if by_fix.get("many-reviews") else ""
    ratings = [r.rating for r in people.REVIEWS if r.product_slug == many]
    if len(ratings) < 5:
        errors.append("many-reviews fixture needs >= 5 reviews")
    slugs = {p.slug for p in products}
    for r in people.REVIEWS:
        if r.product_slug not in slugs:
            errors.append(f"review on unknown product {r.product_slug}")
    if len({(r.reviewer, r.product_slug) for r in people.REVIEWS}) != len(people.REVIEWS):
        errors.append("duplicate customer/product review")
    for order in people.orders():
        if len({line.product_slug for line in order.lines}) != len(order.lines):
            errors.append(f"duplicate product line in {order.key}")
    return errors
