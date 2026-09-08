from __future__ import annotations

from typing import Any

from app.memory.memory_service import memory_service


WARDROBE_DATA: dict[str, list[dict[str, Any]]] = {
    "demo_user": [
        {
            "id": "W001",
            "name": "Black Jeans",
            "category": "jeans",
            "color": "black",
        },
        {
            "id": "W002",
            "name": "White Shirt",
            "category": "shirt",
            "color": "white",
        },
    ]
}


def get_wardrobe(user_id: str) -> list[dict[str, Any]]:
    """Return the user's persisted wardrobe, or seeded demo data when empty."""

    saved_items = memory_service.get_wardrobe(user_id)
    if saved_items:
        return [
            {
                "id": f"DB{index:03d}",
                "name": item["item_name"],
                "category": item["category"],
                "color": item["color"],
            }
            for index, item in enumerate(saved_items, start=1)
        ]

    return WARDROBE_DATA.get(user_id, [])


def save_wardrobe_item(
    user_id: str,
    name: str,
    category: str,
    color: str | None = None,
) -> dict[str, Any]:
    """Save a new wardrobe item for a user."""

    memory_service.add_wardrobe_item(
        user_id=user_id,
        item_name=name,
        category=category,
        color=color,
    )

    return {
        "id": f"DB-{user_id}-{name}",
        "name": name,
        "category": category,
        "color": color,
    }
