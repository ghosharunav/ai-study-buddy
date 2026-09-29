from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class StudyMaterial(Base):
    """
    Uploaded study material, pre-chunked for retrieval. chunks_json stores a
    JSON list of text chunks — see utils/text_chunking.py for how they're
    produced and utils/retrieval.py for how relevant ones are found later.
    """
    __tablename__ = "study_materials"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    chunks_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("StudySession", back_populates="study_materials")
