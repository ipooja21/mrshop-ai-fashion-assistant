from __future__ import annotations

from typing import Any


STYLISTS = [
    {
        "id": "S001",
        "name": "Aarav",
        "specialization": "Casual Styling",
        "available": True,
    },
    {
        "id": "S002",
        "name": "Meera",
        "specialization": "Minimal & Modern",
        "available": True,
    },
]


def book_stylist(
    user_id: str,
    stylist_id: str | None = None,
) -> dict[str, Any]:
    """
    Create a mock stylist booking.

    No real payment or external booking service is used.
    """

    available_stylists = [
        stylist for stylist in STYLISTS
        if stylist["available"]
    ]

    if not available_stylists:
        return {
            "success": False,
            "message": "No stylists are currently available.",
        }

    stylist = None

    if stylist_id:
        for item in available_stylists:
            if item["id"] == stylist_id:
                stylist = item
                break

        if stylist is None:
            return {
                "success": False,
                "message": "Requested stylist is not available.",
            }
    else:
        stylist = available_stylists[0]

    return {
        "success": True,
        "booking_id": f"B-{user_id}-001",
        "user_id": user_id,
        "stylist_id": stylist["id"],
        "stylist_name": stylist["name"],
        "specialization": stylist["specialization"],
        "status": "CONFIRMED",
        "message": (
            f"Stylist session booked with {stylist['name']} "
            f"for {stylist['specialization']}."
        ),
    }


def get_available_stylists() -> list[dict[str, Any]]:
    """Return currently available mock stylists."""

    return [
        stylist
        for stylist in STYLISTS
        if stylist["available"]
    ]