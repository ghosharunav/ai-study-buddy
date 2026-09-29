from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class PracticeQuestionSet(Base):
    """A generated set of open-ended practice questions."""
    __tablename__ = "practice_question_sets"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    topic = Column(String, nullable=False)
    difficulty_level = Column(String, nullable=False)
    questions_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("StudySession", back_populates="practice_sets")
