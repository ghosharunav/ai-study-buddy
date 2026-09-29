from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Message(Base):
    """
    A single chat turn. role is either "user" or "assistant".
    This table IS the conversation memory — the prompt engine reads recent
    rows from here to build context-aware prompts (see prompt_engine/prompt_builder.py).
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("StudySession", back_populates="messages")
