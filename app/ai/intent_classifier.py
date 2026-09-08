import json
import logging
import re
from typing import Any, Dict, Optional

from app.ai.llm_client import llm_client


logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Hybrid intent classifier.

    1. First tries deterministic rule-based classification.
    2. If confidence is low, uses the LLM as a fallback.
    """

    INTENTS = {
        "STYLING",
        "PURCHASE",
        "BOOKING",
        "WARDROBE",
        "GENERAL",
    }

    def __init__(self, llm_threshold: float = 0.5):
        self.llm_threshold = llm_threshold

    # ---------------------------------------------------------
    # PUBLIC METHOD
    # ---------------------------------------------------------

    def classify(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        message = message.strip()

        if not message:
            return {
                "intent": "GENERAL",
                "confidence": 1.0,
                "classification_method": "empty_input",
                "detected_entities": {}
            }

        # First try rules
        rule_result = self._rule_classify(message, context)

        logger.info(
            "Rule classification: intent=%s confidence=%.2f",
            rule_result["intent"],
            rule_result["confidence"]
        )

        # High confidence -> use rules
        if rule_result["confidence"] >= self.llm_threshold:
            return rule_result

        # Low confidence -> LLM fallback
        logger.info("Low confidence. Using LLM fallback.")

        llm_result = self._llm_classify(message, context)

        if llm_result:
            return llm_result

        # If LLM fails, safely return rule result
        logger.warning("LLM fallback failed. Returning rule result.")

        return rule_result

    # ---------------------------------------------------------
    # RULE BASED CLASSIFIER
    # ---------------------------------------------------------

    def _rule_classify(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        text = message.lower()

        entities = self._extract_entities(text)

        scores = {
            "STYLING": 0.0,
            "PURCHASE": 0.0,
            "BOOKING": 0.0,
            "WARDROBE": 0.0,
            "GENERAL": 0.1
        }

        # -------------------------
        # STYLING
        # -------------------------

        styling_keywords = [
            "what should i wear",
            "what to wear",
            "outfit",
            "style",
            "styling",
            "match",
            "go with",
            "wear with",
            "dress for"
        ]

        for keyword in styling_keywords:
            if keyword in text:
                scores["STYLING"] += 0.95
                break

        # -------------------------
        # PURCHASE
        # -------------------------

        purchase_keywords = [
            "buy",
            "purchase",
            "shop",
            "order",
            "price",
            "cost",
            "under",
            "cheaper",
            "product"
        ]

        for keyword in purchase_keywords:
            if keyword in text:
                scores["PURCHASE"] += 0.99
                break

        # -------------------------
        # BOOKING
        # -------------------------

        booking_keywords = [
            "book",
            "booking",
            "appointment",
            "stylist",
            "schedule",
            "tomorrow",
            "available"
        ]

        for keyword in booking_keywords:
            if keyword in text:
                scores["BOOKING"] += 0.8
                break

        # -------------------------
        # WARDROBE
        # -------------------------

        wardrobe_keywords = [
            "wardrobe",
            "my clothes",
            "my dress",
            "my jeans",
            "upload"
        ]

        for keyword in wardrobe_keywords:
            if keyword in text:
                scores["WARDROBE"] += 0.8
                break

        # A user can mention an owned item while asking for styling.  Treat the
        # requested outcome as the intent; the item is still extracted as context.
        if (
            any(phrase in text for phrase in ["how can i style", "style it", "style this"])
            and scores["STYLING"] > 0
        ):
            scores["WARDROBE"] = 0.0

        # -------------------------
        # CONTEXT
        # -------------------------

        if context:
            current_intent = context.get("current_intent")

            # Example:
            # User previously asked about products
            # Then says "something cheaper"

            if (
                current_intent == "PURCHASE"
                and any(
                    phrase in text
                    for phrase in [
                        "something cheaper",
                        "cheaper one",
                        "lower price",
                        "less expensive"
                    ]
                )
            ):
                return {
                    "intent": "PURCHASE",
                    "confidence": 0.85,
                    "classification_method": "context",
                    "detected_entities": entities
                }

        # -------------------------
        # SELECT BEST INTENT
        # -------------------------

        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]

        confidence = min(confidence, 0.99)

        # If no meaningful signal
        if confidence < 0.5:
            best_intent = "GENERAL"
            confidence = 0.35

        return {
            "intent": best_intent,
            "confidence": round(confidence, 2),
            "classification_method": "rule",
            "detected_entities": entities
        }

    # ---------------------------------------------------------
    # ENTITY EXTRACTION
    # ---------------------------------------------------------

    def _extract_entities(self, text: str) -> Dict[str, Any]:

        entities = {}

        # Budget
        budget_patterns = [
            r"(?:under|below|less than|within)\s*[₹rs\.]*\s*([\d,]+)",
            r"₹\s*([\d,]+)",
            r"rs\.?\s*([\d,]+)"
        ]

        for pattern in budget_patterns:
            match = re.search(pattern, text)

            if match:
                entities["budget"] = int(match.group(1).replace(",", ""))
                break

        # Product categories
        categories = [
            "jeans",
            "shirt",
            "shirts",
            "dress",
            "dresses",
            "sneakers",
            "shoes",
            "t-shirt",
            "tshirt",
            "jacket",
            "blazer",
            "trousers",
            "kurti",
            "kurtis",
            "footwear",
            "sandals",
            "heels",
        ]

        for category in categories:
            if category in text:
                entities["category"] = category
                break

        item_match = re.search(
            r"\b(?:i have|i own|my)\s+(?:a |an |the )?((?:black|white|blue|red|green|beige|grey|gray)\s+)?([a-z-]+)",
            text,
        )
        if item_match:
            color = (item_match.group(1) or "").strip() or None
            item = " ".join(
                part for part in [color, item_match.group(2)] if part
            )
            entities["item"] = item
            if color:
                entities["color"] = color

        return entities

    # ---------------------------------------------------------
    # LLM FALLBACK
    # ---------------------------------------------------------

    def _llm_classify(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:

        context_text = json.dumps(
            context or {},
            ensure_ascii=False
        )

        prompt = f"""
You are an intent classification system for a fashion assistant.

Allowed intents:

STYLING
PURCHASE
BOOKING
WARDROBE
GENERAL

Classify the user's message into exactly ONE intent.

Also extract useful entities such as:
- budget
- category
- occasion
- style
- product

Return ONLY valid JSON.

JSON format:

{{
  "intent": "STYLING",
  "confidence": 0.95,
  "detected_entities": {{
    "budget": null,
    "category": null,
    "occasion": null,
    "style": null
  }}
}}

Conversation context:
{context_text}

User message:
{message}
"""

        try:
            response = llm_client.generate(prompt)

            if not response:
                return None

            # Remove accidental markdown fences
            response = response.strip()

            if response.startswith("```"):
                response = re.sub(
                    r"```(?:json)?",
                    "",
                    response
                ).replace("```", "").strip()

            data = json.loads(response)

            intent = data.get("intent", "GENERAL").upper()

            if intent not in self.INTENTS:
                return None

            confidence = float(
                data.get("confidence", 0.7)
            )

            confidence = max(
                0.0,
                min(confidence, 1.0)
            )

            return {
                "intent": intent,
                "confidence": round(confidence, 2),
                "classification_method": "llm_fallback",
                "detected_entities": data.get(
                    "detected_entities",
                    {}
                )
            }

        except Exception as exc:
            logger.exception(
                "LLM intent classification failed: %s",
                exc
            )
            return None


# Global classifier instance
classifier = IntentClassifier()


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    test_messages = [
        "What should I wear with black jeans?",
        "I want to buy sneakers under 3000",
        "Can I book a stylist tomorrow?",
        "I have a blue dress",
        "Something cheaper",
        "I need something nice"
    ]

    context = {
        "current_intent": "PURCHASE",
        "budget": 3000
    }

    for message in test_messages:

        result = classifier.classify(
            message,
            context=context
        )

        print("\nMessage:", message)
        print(
            "Result:",
            json.dumps(
                result,
                indent=2
            )
        )
