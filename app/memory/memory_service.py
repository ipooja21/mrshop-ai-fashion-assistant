import json
import sqlite3
from typing import Optional

from app.config import settings


class MemoryService:
    """Persistent memory and conversation history service."""

    def __init__(self):
        self.db_path = settings.db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    # =========================================================
    # USER
    # =========================================================

    def ensure_user(self, user_id: str, name: Optional[str] = None):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO users (user_id, name)
            VALUES (?, ?)
            """,
            (user_id, name),
        )

        conn.commit()
        conn.close()

    # =========================================================
    # CONVERSATION
    # =========================================================

    def create_conversation(self, user_id: str) -> int:
        self.ensure_user(user_id)

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO conversations (user_id)
            VALUES (?)
            """,
            (user_id,),
        )

        conversation_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return conversation_id

    # =========================================================
    # MESSAGES
    # =========================================================

    def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        intent: Optional[str] = None,
    ):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO messages
            (conversation_id, role, content, intent)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, role, content, intent),
        )

        conn.commit()
        conn.close()

    def get_recent_messages(
        self,
        conversation_id: int,
        limit: int = 10,
    ):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT role, content, intent, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY message_id DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        )

        rows = cursor.fetchall()
        conn.close()

        # Oldest → newest
        rows.reverse()

        return [
            {
                "role": row[0],
                "content": row[1],
                "intent": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

    # =========================================================
    # USER CONTEXT / MEMORY
    # =========================================================

    def get_context(self, user_id: str) -> dict:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                budget,
                style_preference,
                current_intent,
                previous_intent,
                conversation_summary,
                memory_confidence
            FROM user_context
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {}

        return {
            "budget": row[0],
            "style_preference": row[1],
            "current_intent": row[2],
            "previous_intent": row[3],
            "conversation_summary": row[4],
            "memory_confidence": row[5],
        }

    def update_context(
        self,
        user_id: str,
        budget: Optional[float] = None,
        style_preference: Optional[str] = None,
        current_intent: Optional[str] = None,
        previous_intent: Optional[str] = None,
        conversation_summary: Optional[str] = None,
        memory_confidence: float = 1.0,
    ):
        self.ensure_user(user_id)

        # Get existing context first
        existing = self.get_context(user_id)

        budget = (
            budget
            if budget is not None
            else existing.get("budget")
        )

        style_preference = (
            style_preference
            if style_preference is not None
            else existing.get("style_preference")
        )

        previous_intent = (
            previous_intent
            if previous_intent is not None
            else existing.get("current_intent")
        )

        conversation_summary = (
            conversation_summary
            if conversation_summary is not None
            else existing.get("conversation_summary")
        )

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO user_context (
                user_id,
                budget,
                style_preference,
                current_intent,
                previous_intent,
                conversation_summary,
                memory_confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(user_id)
            DO UPDATE SET
                budget = excluded.budget,
                style_preference = excluded.style_preference,
                current_intent = excluded.current_intent,
                previous_intent = excluded.previous_intent,
                conversation_summary = excluded.conversation_summary,
                memory_confidence = excluded.memory_confidence,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                user_id,
                budget,
                style_preference,
                current_intent,
                previous_intent,
                conversation_summary,
                memory_confidence,
            ),
        )

        conn.commit()
        conn.close()

    # =========================================================
    # WARDROBE
    # =========================================================

    def add_wardrobe_item(
        self,
        user_id: str,
        item_name: str,
        category: Optional[str] = None,
        color: Optional[str] = None,
    ):
        self.ensure_user(user_id)

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO wardrobe_items
            (user_id, item_name, category, color)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, item_name, category, color),
        )

        conn.commit()
        conn.close()

    def get_wardrobe(self, user_id: str):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT item_name, category, color
            FROM wardrobe_items
            WHERE user_id = ?
            ORDER BY item_id DESC
            """,
            (user_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "item_name": row[0],
                "category": row[1],
                "color": row[2],
            }
            for row in rows
        ]

    # =========================================================
    # RECOMMENDATIONS
    # =========================================================

    def save_recommendation(
        self,
        user_id: str,
        product_name: str,
        reason: str,
    ):
        self.ensure_user(user_id)

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO recommendations
            (user_id, product_name, reason)
            VALUES (?, ?, ?)
            """,
            (user_id, product_name, reason),
        )

        conn.commit()
        conn.close()

    # =========================================================
    # TOOL EVENTS
    # =========================================================

    def save_tool_event(
        self,
        user_id: str,
        tool_name: str,
        arguments: dict,
        result: str,
    ):
        self.ensure_user(user_id)

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tool_events
            (user_id, tool_name, arguments, result)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                tool_name,
                json.dumps(arguments),
                result,
            ),
        )

        conn.commit()
        conn.close()

    # =========================================================
    # RESET
    # =========================================================

    def reset_user(self, user_id: str):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM messages WHERE conversation_id IN "
            "(SELECT conversation_id FROM conversations WHERE user_id = ?)",
            (user_id,),
        )

        cursor.execute(
            "DELETE FROM conversations WHERE user_id = ?",
            (user_id,),
        )

        cursor.execute(
            "DELETE FROM user_context WHERE user_id = ?",
            (user_id,),
        )

        cursor.execute(
            "DELETE FROM wardrobe_items WHERE user_id = ?",
            (user_id,),
        )

        cursor.execute(
            "DELETE FROM recommendations WHERE user_id = ?",
            (user_id,),
        )

        cursor.execute(
            "DELETE FROM tool_events WHERE user_id = ?",
            (user_id,),
        )

        conn.commit()
        conn.close()


memory_service = MemoryService()