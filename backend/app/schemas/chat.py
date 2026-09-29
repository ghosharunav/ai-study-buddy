from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    subject: str = Field(..., examples=["Data Structures"])
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    title: str | None = Field(None, examples=["Understanding Binary Trees"])


class SessionResponse(BaseModel):
    id: int
    subject: str
    difficulty_level: str
    title: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # lets this be built directly from an ORM object


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, examples=["What is a binary search tree?"])


class ChatResponse(BaseModel):
    session_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse
