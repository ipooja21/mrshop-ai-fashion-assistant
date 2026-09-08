from uuid import uuid4

import app.orchestrator.conversation_orchestrator as orchestrator_module
from app.memory.memory_service import memory_service
from app.orchestrator.conversation_orchestrator import conversation_orchestrator


def send(conversation_id: int, user_id: str, message: str) -> dict:
    return conversation_orchestrator.process_message(
        user_id=user_id,
        conversation_id=conversation_id,
        message=message,
    )


def test_styling_to_purchase_topic_switch(monkeypatch):
    """Track A's core ambient-context scenario remains deterministic."""
    monkeypatch.setattr(
        orchestrator_module.llm_client,
        "generate",
        lambda _: "Helpful styling response.",
    )
    user_id = f"test_track_a_{uuid4().hex}"
    conversation_id = memory_service.create_conversation(user_id)

    styling = send(
        conversation_id,
        user_id,
        "I have a black kurti. How can I style it?",
    )
    purchase = send(
        conversation_id,
        user_id,
        "I want to buy matching footwear.",
    )

    assert styling["intent"] == "STYLING"
    assert purchase["intent"] == "PURCHASE"
    assert purchase["topic_switch"] is True
    assert purchase["tool_used"] == "search_products"
    assert purchase["tool_result"]
    assert "black kurti" in purchase["memory"]["conversation_summary"]
    assert memory_service.get_wardrobe(user_id)


def test_budget_and_booking_routes_to_tools(monkeypatch):
    monkeypatch.setattr(
        orchestrator_module.llm_client,
        "generate",
        lambda _: "Helpful response.",
    )
    user_id = f"test_track_a_{uuid4().hex}"

    purchase_conversation = memory_service.create_conversation(user_id)
    purchase = send(
        purchase_conversation,
        user_id,
        "Show me sneakers under ₹3,000.",
    )
    assert purchase["intent"] == "PURCHASE"
    assert purchase["tool_used"] == "search_products"
    assert purchase["memory"]["budget"] == 3000

    booking_conversation = memory_service.create_conversation(user_id)
    booking = send(
        booking_conversation,
        user_id,
        "Book a stylist consultation.",
    )
    assert booking["intent"] == "BOOKING"
    assert booking["tool_used"] == "book_stylist"
    assert booking["tool_result"]["success"] is True
