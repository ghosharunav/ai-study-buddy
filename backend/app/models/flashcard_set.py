from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class FlashcardSet(Base):
    """A generated set of flashcards for spaced-repetition style review."""
    __tablename__ = "flashcard_sets"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    topic = Column(String, nullable=False)
    difficulty_level = Column(String, nullable=False)
    cards_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("StudySession", back_populates="flashcard_sets")
