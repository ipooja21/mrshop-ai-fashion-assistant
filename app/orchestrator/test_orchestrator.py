from app.memory.memory_service import memory_service
from app.orchestrator.conversation_orchestrator import (
    conversation_orchestrator,
)


USER_ID = "demo_user"

conversation_id = memory_service.create_conversation(
    USER_ID
)

messages = [
    "I have black jeans. What should I wear?",
    "My budget is 3000",
    "Actually I want to buy sneakers",
    "Something cheaper",
]

for message in messages:

    print("\n" + "=" * 60)
    print("USER:", message)

    result = conversation_orchestrator.process_message(
        user_id=USER_ID,
        conversation_id=conversation_id,
        message=message,
    )

    print("\nAI:", result["response"])

    print("\nSYSTEM TRACE")
    print("Intent:", result["intent"])
    print("Confidence:", result["confidence"])
    print(
        "Classification:",
        result["classification_method"]
    )
    print(
        "Topic Switch:",
        result["topic_switch"]
    )
    print(
        "Previous Intent:",
        result["previous_intent"]
    )
    print(
        "Current Intent:",
        result["current_intent"]
    )
    print(
        "Memory:",
        result["memory"]
    )