from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class QuizAttempt(Base):
    """
    One scored attempt at a quiz. answers_json is the student's raw selected
    option indices (in question order); weak_topics_json is the deduped list
    of topic_tags the student got wrong on THIS attempt; results_json is the
    full per-question breakdown ({"topic_tag": ..., "is_correct": ...} for
    every question) — this is what progress_service.py aggregates ACROSS all
    attempts in a session to compute real topic-level mastery percentages,
    not just "wrong at least once."
    """
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    answers_json = Column(Text, nullable=False)
    weak_topics_json = Column(Text, nullable=False)
    results_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    quiz = relationship("Quiz", back_populates="attempts")
