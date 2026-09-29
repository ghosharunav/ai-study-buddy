from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Note(Base):
    """
    An AI-generated study note — the persisted result of the topic-explainer
    feature. content_json stores the validated ExplanationOutput as a JSON
    string, so what's in the database is guaranteed to already be
    schema-valid (validation happens before this row is ever created).
    """
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    topic = Column(String, nullable=False)
    difficulty_level = Column(String, nullable=False)
    content_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("StudySession", back_populates="notes")
