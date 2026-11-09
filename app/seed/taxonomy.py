"""Five top-level categories and subcategories (PRD §5.1); Wearables and Audio is small goods."""

from app.seed.model import CategorySpec

COMPUTERS = "computers-and-technology"
PHONES = "smartphones"
WEARABLES = "wearables-and-audio"
FOOTBALL = "football-shirts-and-apparel"
SHOES = "shoes-and-sneakers"

_TOP = [
    (COMPUTERS, "Computers and Technology", "PCs, laptops, monitors, peripherals and components."),
    (PHONES, "Smartphones", "Flagship, mid-range and entry-level smartphones."),
    (WEARABLES, "Wearables and Audio", "Earbuds, headphones, speakers, smartwatches and bands."),
    (
        FOOTBALL,
        "Football Shirts and Apparel",
        "Fictional, unofficial demo football shirts and sportswear.",
    ),
    (SHOES, "Shoes and Sneakers", "Running, casual, training and sports footwear."),
]

_SUBS: dict[str, list[tuple[str, str]]] = {
    COMPUTERS: [
        ("desktop-pcs", "Desktop PCs"),
        ("gaming-pcs", "Gaming PCs"),
        ("custom-built-pcs", "Custom-built PCs"),
        ("laptops", "Laptops"),
        ("monitors", "Monitors"),
        ("keyboards-and-mice", "Keyboards and Mice"),
        ("gaming-accessories", "Gaming Accessories"),
        ("pc-components", "PC Components"),
    ],
    PHONES: [
        ("apple-iphones", "Apple iPhones"),
        ("samsung-galaxy-phones", "Samsung Galaxy"),
        ("xiaomi-phones", "Xiaomi"),
        ("google-pixel-phones", "Google Pixel"),
        ("entry-level-phones", "Entry-level Phones"),
    ],
    WEARABLES: [
        ("earbuds", "Earbuds"),
        ("headphones-and-gaming-headsets", "Headphones and Gaming Headsets"),
        ("bluetooth-speakers", "Bluetooth Speakers"),
        ("smartwatches", "Smartwatches"),
        ("fitness-bands", "Fitness Bands"),
    ],
    FOOTBALL: [
        ("club-shirts", "Club Shirts"),
        ("national-team-shirts", "National Team Shirts"),
        ("training-tops-and-sportswear", "Training Tops and Sportswear"),
    ],
    SHOES: [
        ("running-shoes", "Running Shoes"),
        ("casual-sneakers", "Casual Sneakers"),
        ("training-shoes", "Training Shoes"),
        ("sports-shoes", "Sports Shoes"),
    ],
}


def build_categories() -> list[CategorySpec]:
    result: list[CategorySpec] = []
    for index, (slug, name, description) in enumerate(_TOP):
        small = slug == WEARABLES
        result.append(CategorySpec(slug, name, description, index, None, small))
        for sub_index, (sub_slug, sub_name) in enumerate(_SUBS[slug]):
            # BR-077: subcategories inherit the small-goods designation.
            result.append(
                CategorySpec(sub_slug, sub_name, f"{sub_name} in {name}.", sub_index, slug, small)
            )
    return result


def parent_of(sub_slug: str) -> str:
    for parent, subs in _SUBS.items():
        if any(slug == sub_slug for slug, _ in subs):
            return parent
    raise KeyError(sub_slug)
