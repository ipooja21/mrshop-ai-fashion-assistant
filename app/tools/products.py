from __future__ import annotations

from typing import Any


PRODUCT_CATALOG = [
    {
        "id": "SNK001",
        "name": "Urban White Low-Top Sneakers",
        "category": "sneakers",
        "price": 2499,
        "style": "casual",
    },
    {
        "id": "SNK002",
        "name": "Classic Black Sneakers",
        "category": "sneakers",
        "price": 1999,
        "style": "casual",
    },
    {
        "id": "SNK003",
        "name": "Minimal Grey Sneakers",
        "category": "sneakers",
        "price": 2999,
        "style": "minimal",
    },
    {
        "id": "TSH001",
        "name": "Classic White T-Shirt",
        "category": "t-shirt",
        "price": 799,
        "style": "casual",
    },
    {
        "id": "JNS001",
        "name": "Slim Black Jeans",
        "category": "jeans",
        "price": 1799,
        "style": "casual",
    },
]


def search_products(
    category: str,
    max_price: int | None = None,
    style: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search the mock Mr.Shop product catalog.

    This is a deterministic demo tool and does not connect
    to any real marketplace.
    """

    category = category.strip().lower()
    category_aliases = {
        "shoe": "sneakers",
        "shoes": "sneakers",
        "footwear": "sneakers",
        "trainers": "sneakers",
    }
    category = category_aliases.get(category, category)

    results = []

    for product in PRODUCT_CATALOG:
        if product["category"].lower() != category:
            continue

        if max_price is not None and product["price"] > max_price:
            continue

        if style and product["style"].lower() != style.lower():
            continue

        results.append(product)

    return results
