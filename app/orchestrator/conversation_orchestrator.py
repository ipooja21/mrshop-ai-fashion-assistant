import logging
import re
from typing import Any, Dict

from app.ai.intent_classifier import classifier
from app.ai.llm_client import llm_client
from app.memory.memory_service import memory_service

from app.tools.products import search_products
from app.tools.wardrobe import (
    get_wardrobe,
    save_wardrobe_item,
)
from app.tools.booking import book_stylist


logger = logging.getLogger(__name__)


class ConversationOrchestrator:
    """
    Main conversation brain for Mr.Shop.

    Flow:
    1. Load memory
    2. Classify intent
    3. Detect topic switch
    4. Retrieve relevant context
    5. Route to tools when required
    6. Build contextual LLM prompt
    7. Generate response
    8. Save conversation
    9. Update memory
    10. Return safe system trace
    """

    def process_message(
        self,
        user_id: str,
        conversation_id: int,
        message: str,
    ) -> Dict[str, Any]:

        message = message.strip()

        if not message:
            return {
                "response": "Please enter a message.",
                "intent": "UNKNOWN",
                "confidence": 0.0,
                "classification_method": "validation",
                "detected_entities": {},
                "topic_switch": False,
                "previous_intent": None,
                "current_intent": "UNKNOWN",
                "tool_used": None,
                "memory": memory_service.get_context(user_id),
            }

        # -------------------------------------------------
        # 1. LOAD MEMORY
        # -------------------------------------------------

        context = memory_service.get_context(user_id)

        recent_messages = memory_service.get_recent_messages(
            conversation_id,
            limit=10,
        )

        logger.info(
            "Loaded memory for user=%s",
            user_id,
        )

        # -------------------------------------------------
        # 2. CLASSIFY INTENT
        # -------------------------------------------------

        intent_result = classifier.classify(
            message,
            context=context,
        )

        current_intent = intent_result["intent"]
        confidence = intent_result["confidence"]

        logger.info(
            "Intent=%s confidence=%.2f method=%s",
            current_intent,
            confidence,
            intent_result["classification_method"],
        )

        # -------------------------------------------------
        # 3. TOPIC SWITCH DETECTION
        # -------------------------------------------------

        previous_intent = context.get("current_intent")

        topic_switch = False

        if (
            previous_intent
            and previous_intent != current_intent
            and current_intent != "GENERAL"
        ):
            topic_switch = True

        logger.info(
            "Topic switch=%s previous=%s current=%s",
            topic_switch,
            previous_intent,
            current_intent,
        )

        # -------------------------------------------------
        # 4. SAVE USER MESSAGE
        # -------------------------------------------------

        memory_service.save_message(
            conversation_id=conversation_id,
            role="user",
            content=message,
            intent=current_intent,
        )

        # -------------------------------------------------
        # 5. EXTRACT ENTITIES
        # -------------------------------------------------

        entities = intent_result.get(
            "detected_entities",
            {},
        )

        # -------------------------------------------------
        # 6. UPDATE MEMORY VALUES
        # -------------------------------------------------

        budget = entities.get("budget")

        style_preference = entities.get("style")

        if style_preference is None:
            style_preference = context.get(
                "style_preference"
            )

        if (
            current_intent == "STYLING"
            and entities.get("item")
            and entities.get("category")
            and any(phrase in message.lower() for phrase in ["i have", "i own"])
        ):
            memory_service.add_wardrobe_item(
                user_id=user_id,
                item_name=entities["item"],
                category=entities["category"],
                color=entities.get("color"),
            )

        # -------------------------------------------------
        # 7. TOOL ROUTING
        # -------------------------------------------------

        tool_used = None
        tool_result = None

        try:
            tool_used, tool_result = self._execute_tool(
                user_id=user_id,
                message=message,
                intent=current_intent,
                entities=entities,
                context=context,
            )

        except Exception as exc:
            logger.exception(
                "Tool execution failed user=%s intent=%s error=%s",
                user_id,
                current_intent,
                exc,
            )

            tool_used = None
            tool_result = {
                "success": False,
                "error": "Tool execution failed.",
            }

        # -------------------------------------------------
        # 8. BUILD CONTEXTUAL PROMPT
        # -------------------------------------------------

        prompt = self._build_prompt(
            message=message,
            context=context,
            recent_messages=recent_messages,
            current_intent=current_intent,
            topic_switch=topic_switch,
            entities=entities,
            tool_used=tool_used,
            tool_result=tool_result,
        )

        # -------------------------------------------------
        # 9. CALL LLM
        # -------------------------------------------------

        response = llm_client.generate(prompt)

        if not response:

            response = self._fallback_response(
                current_intent=current_intent,
                tool_used=tool_used,
                tool_result=tool_result,
            )

        # -------------------------------------------------
        # 10. SAVE ASSISTANT MESSAGE
        # -------------------------------------------------

        memory_service.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response,
            intent=current_intent,
        )

        # -------------------------------------------------
        # 11. UPDATE USER CONTEXT
        # -------------------------------------------------

        memory_service.update_context(
            user_id=user_id,
            budget=budget,
            style_preference=style_preference,
            current_intent=current_intent,
            previous_intent=previous_intent,
            conversation_summary=self._build_summary(
                recent_messages,
                message,
            ),
            memory_confidence=confidence,
        )

        # -------------------------------------------------
        # 12. RETURN SYSTEM TRACE
        # -------------------------------------------------

        return {
            "response": response,

            "intent": current_intent,

            "confidence": confidence,

            "classification_method": (
                intent_result["classification_method"]
            ),

            "detected_entities": entities,

            "topic_switch": topic_switch,

            "previous_intent": previous_intent,

            "current_intent": current_intent,

            "tool_used": tool_used,

            "tool_result": tool_result,

            "memory": memory_service.get_context(
                user_id
            ),
        }

    # =====================================================
    # TOOL ROUTER
    # =====================================================

    def _execute_tool(
        self,
        user_id: str,
        message: str,
        intent: str,
        entities: Dict[str, Any],
        context: Dict[str, Any],
    ):
        """
        Decide whether a tool is required for the current
        user request.

        Returns:
            (tool_name, tool_result)
        """

        # -------------------------------------------------
        # PURCHASE
        # -------------------------------------------------

        if intent == "PURCHASE":

            category = (
                entities.get("category")
                or self._extract_category(message)
            )

            max_price = (
                entities.get("budget")
                or context.get("budget")
            )

            style = (
                entities.get("style")
                or context.get("style_preference")
            )

            # If category is unknown, let the LLM ask
            # a clarification question.
            if not category:
                logger.info(
                    "Purchase tool skipped: category missing"
                )
                return None, None

            result = search_products(
                category=category,
                max_price=max_price,
                style=style,
            )

            logger.info(
                "Tool search_products executed category=%s max_price=%s",
                category,
                max_price,
            )

            return "search_products", result

        # -------------------------------------------------
        # WARDROBE
        # -------------------------------------------------

        if intent == "WARDROBE":

            # Detect whether the user wants to save an item.
            save_request = any(
                word in message.lower()
                for word in [
                    "add",
                    "save",
                    "have",
                    "wear",
                    "my new",
                ]
            )

            item_name = entities.get("item")
            category = entities.get("category")
            color = entities.get("color")

            if save_request and item_name and category:

                result = save_wardrobe_item(
                    user_id=user_id,
                    name=item_name,
                    category=category,
                    color=color,
                )

                logger.info(
                    "Tool save_wardrobe_item executed user=%s",
                    user_id,
                )

                return "save_wardrobe_item", result

            result = get_wardrobe(user_id)

            logger.info(
                "Tool get_wardrobe executed user=%s",
                user_id,
            )

            return "get_wardrobe", result

        # -------------------------------------------------
        # BOOKING
        # -------------------------------------------------

        if intent == "BOOKING":

            stylist_id = entities.get(
                "stylist_id"
            )

            result = book_stylist(
                user_id=user_id,
                stylist_id=stylist_id,
            )

            logger.info(
                "Tool book_stylist executed user=%s",
                user_id,
            )

            return "book_stylist", result

        # -------------------------------------------------
        # STYLING
        # -------------------------------------------------

        # Styling does not require an external tool yet.
        # The LLM can generate the recommendation using
        # retrieved wardrobe/context.
        return None, None

    # =====================================================
    # CATEGORY EXTRACTION
    # =====================================================

    def _extract_category(
        self,
        message: str,
    ) -> str | None:

        message_lower = message.lower()

        categories = [
            "sneakers",
            "shoes",
            "jeans",
            "shirt",
            "t-shirt",
            "dress",
            "jacket",
            "trousers",
            "footwear",
            "sandals",
            "heels",
            "kurti",
        ]

        for category in categories:

            if category in message_lower:
                return category

        return None

    # =====================================================
    # PROMPT BUILDER
    # =====================================================

    def _build_prompt(
        self,
        message: str,
        context: Dict[str, Any],
        recent_messages,
        current_intent: str,
        topic_switch: bool,
        entities: Dict[str, Any],
        tool_used: str | None,
        tool_result: Any,
    ) -> str:

        memory_text = f"""
USER MEMORY
-----------
Budget: {context.get("budget")}
Style preference: {context.get("style_preference")}
Previous intent: {context.get("current_intent")}
Memory confidence: {context.get("memory_confidence")}
Conversation summary: {context.get("conversation_summary")}
"""

        history_text = "\n".join(
            [
                f"{item['role']}: {item['content']}"
                for item in recent_messages[-6:]
            ]
        )

        tool_text = "No tool was used."

        if tool_used:
            tool_text = f"""
TOOL USED:
{tool_used}

TOOL RESULT:
{tool_result}
"""

        return f"""
You are Mr.Shop, a conversational AI fashion assistant.

Supported capabilities:

1. WARDROBE
2. STYLING
3. PURCHASE
4. BOOKING

CURRENT INTENT:
{current_intent}

TOPIC SWITCH:
{topic_switch}

DETECTED ENTITIES:
{entities}

{memory_text}

RECENT CONVERSATION:
{history_text}

{tool_text}

CURRENT USER MESSAGE:
{message}

INSTRUCTIONS:

- Respond naturally like a helpful fashion assistant.
- Use relevant information from memory.
- Do not ask the user to repeat information already available.
- If the user changes topic, smoothly follow the new topic.
- Preserve useful preferences such as budget and style.
- If a product search tool returned products, recommend only
  products present in the tool result.
- If no products were found, clearly tell the user.
- Never invent a real booking or purchase confirmation.
- A stylist booking may only be described as confirmed if the
  booking tool returned success=True.
- Do not claim a purchase was completed.
- If required information is missing, ask a concise clarification.
- Do not reveal chain-of-thought or hidden reasoning.
- Keep the response concise but useful.
"""

    # =====================================================
    # FALLBACK RESPONSE
    # =====================================================

    def _fallback_response(
        self,
        current_intent: str,
        tool_used: str | None,
        tool_result: Any,
    ) -> str:

        if (
            tool_used == "search_products"
            and isinstance(tool_result, list)
        ):

            if not tool_result:
                return (
                    "I couldn't find matching products "
                    "within the available options."
                )

            product_names = [
                item.get("name", "Product")
                for item in tool_result[:3]
            ]

            return (
                "I found these options: "
                + ", ".join(product_names)
                + "."
            )

        if (
            tool_used == "book_stylist"
            and isinstance(tool_result, dict)
            and tool_result.get("success")
        ):
            return tool_result.get(
                "message",
                "Your stylist session has been confirmed.",
            )

        if tool_used == "get_wardrobe":
            return (
                "I found your wardrobe items. "
                "You can use them for styling recommendations."
            )

        if current_intent == "PURCHASE":
            return (
                "Sure. Tell me which product category "
                "you want to shop for."
            )

        return (
            "I'm having trouble processing that right now. "
            "Please try again in a moment."
        )

    # =====================================================
    # CONVERSATION SUMMARY
    # =====================================================

    def _build_summary(
        self,
        recent_messages,
        current_message: str,
    ) -> str:

        messages = recent_messages[-4:]

        summary_parts = []

        for item in messages:
            summary_parts.append(
                f"{item['role']}: {item['content']}"
            )

        summary_parts.append(
            f"user: {current_message}"
        )

        return " | ".join(summary_parts)


# Global instance
conversation_orchestrator = ConversationOrchestrator()
