from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Summary(Base):
    """An AI-generated summary of pasted study material."""
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    difficulty_level = Column(String, nullable=False)
    # First ~300 chars of the original text, for display in history — we
    # don't store the full raw material long-term to keep the DB lean.
    source_preview = Column(Text, nullable=False)
    content_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("StudySession", back_populates="summaries")
