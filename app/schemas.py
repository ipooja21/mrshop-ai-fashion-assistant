from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    conversation_id: int
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    success: bool
    user_id: str
    conversation_id: int
    response: str
    intent: str
    confidence: float
    classification_method: str
    detected_entities: dict
    topic_switch: bool
    previous_intent: str | None = None
    current_intent: str
    tool_used: str | None = None
    tool_result: list | dict | None = None