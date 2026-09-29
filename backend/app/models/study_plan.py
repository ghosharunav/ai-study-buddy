from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class StudyPlan(Base):
    """A generated personalized multi-day study plan."""
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    goal = Column(String, nullable=False)
    plan_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("StudySession", back_populates="study_plans")
