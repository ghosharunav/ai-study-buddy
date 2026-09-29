from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class StudySession(Base):
    """
    One StudySession = one ongoing 'study thread' for a subject at a
    difficulty level. All chat messages, and later notes/quizzes/flashcards,
    hang off a session_id — this is what gives the assistant memory and
    what powers the 'study history' feature on the dashboard.
    """
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False, index=True)
    difficulty_level = Column(String, nullable=False, default="beginner")
    title = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    notes = relationship(
        "Note",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Note.created_at",
    )

    quizzes = relationship(
        "Quiz",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Quiz.created_at",
    )

    summaries = relationship(
        "Summary",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Summary.created_at",
    )

    practice_sets = relationship(
        "PracticeQuestionSet",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="PracticeQuestionSet.created_at",
    )

    flashcard_sets = relationship(
        "FlashcardSet",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="FlashcardSet.created_at",
    )

    study_plans = relationship(
        "StudyPlan",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="StudyPlan.created_at",
    )

    study_materials = relationship(
        "StudyMaterial",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="StudyMaterial.created_at",
    )
