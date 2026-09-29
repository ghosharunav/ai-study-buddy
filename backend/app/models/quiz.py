from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Quiz(Base):
    """
    A generated quiz. questions_json stores the FULL validated QuizOutput,
    including correct_answer_index and explanation for every question.

    Important: this full payload is never sent to the frontend until AFTER
    a student submits their answers (see schemas/quiz.py's QuizQuestionResponse,
    which is deliberately a sanitized subset) — otherwise the answers would
    just be sitting in the browser's network tab.
    """
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    topic = Column(String, nullable=False)
    difficulty_level = Column(String, nullable=False)
    questions_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("StudySession", back_populates="quizzes")
    attempts = relationship(
        "QuizAttempt",
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="QuizAttempt.created_at",
    )
