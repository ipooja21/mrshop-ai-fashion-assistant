from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.memory.memory_service import memory_service
from app.schemas import ChatRequest, ChatResponse
from app.orchestrator.conversation_orchestrator import (
    conversation_orchestrator,
)


router = APIRouter(prefix="/api", tags=["Mr.Shop"])


# =========================================================
# REQUEST MODELS
# =========================================================

class CreateConversationRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    name: str | None = None


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "Mr.Shop API",
    }


# =========================================================
# CREATE CONVERSATION
# =========================================================

@router.post("/conversations")
def create_conversation(
    request: CreateConversationRequest,
) -> Dict[str, Any]:

    try:
        conversation_id = memory_service.create_conversation(
            request.user_id
        )

        return {
            "success": True,
            "user_id": request.user_id,
            "conversation_id": conversation_id,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not create conversation: {exc}",
        )


# =========================================================
# SEND MESSAGE
# =========================================================

@router.post("/messages")
def send_message(
    request: ChatRequest,
) -> Dict[str, Any]:

    try:
        result = conversation_orchestrator.process_message(
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            message=request.message,
        )

        return {
            "success": True,
            "user_id": request.user_id,
            "conversation_id": request.conversation_id,
            **result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Message processing failed: {exc}",
        )


# =========================================================
# GET CONVERSATION HISTORY
# =========================================================

@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
) -> Dict[str, Any]:

    try:
        messages = memory_service.get_recent_messages(
            conversation_id,
            limit=50,
        )

        return {
            "success": True,
            "conversation_id": conversation_id,
            "messages": messages,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not load messages: {exc}",
        )


# =========================================================
# GET USER MEMORY
# =========================================================

@router.get("/users/{user_id}/memory")
def get_user_memory(
    user_id: str,
) -> Dict[str, Any]:

    try:
        context = memory_service.get_context(user_id)

        return {
            "success": True,
            "user_id": user_id,
            "memory": context,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not load memory: {exc}",
        )
        # =========================================================
# CHAT ENDPOINT
# =========================================================

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> Dict[str, Any]:

    try:
        result = conversation_orchestrator.process_message(
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            message=request.message,
        )

        return {
            "success": True,
            "user_id": request.user_id,
            "conversation_id": request.conversation_id,
            **result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {exc}",
        )


# =========================================================
# RESET USER MEMORY
# =========================================================

@router.post("/reset")
def reset_memory(user_id: str) -> Dict[str, Any]:

    try:
        memory_service.update_context(
            user_id=user_id,
            budget=None,
            style_preference=None,
            current_intent=None,
            previous_intent=None,
            conversation_summary="",
            memory_confidence=0.0,
        )

        return {
            "success": True,
            "message": "User memory reset successfully.",
            "user_id": user_id,
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not reset memory.",
        )


# =========================================================
# MEMORY ENDPOINT
# =========================================================

@router.get("/memory/{user_id}")
def get_memory(user_id: str) -> Dict[str, Any]:

    try:
        context = memory_service.get_context(user_id)

        return {
            "success": True,
            "user_id": user_id,
            "memory": context,
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not load memory.",
        )

