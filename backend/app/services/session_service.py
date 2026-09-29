"""
Shared session lookup/creation logic.

Every feature (chat, notes, quiz, flashcards, ...) hangs off a session_id,
so this lives in its own module rather than being duplicated — or worse,
subtly reimplemented differently — in each feature's service file.
"""

from sqlalchemy.orm import Session

from app.models.session import StudySession


class SessionNotFoundError(Exception):
    """Raised when a session_id doesn't exist in the database."""
    pass


def create_session(db: Session, subject: str, difficulty_level: str,
                    title: str | None = None) -> StudySession:
    session = StudySession(
        subject=subject,
        difficulty_level=difficulty_level,
        title=title or f"{subject} ({difficulty_level})",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: Session) -> list[StudySession]:
    """Powers the 'study history' dashboard list — most recently active first."""
    return db.query(StudySession).order_by(StudySession.updated_at.desc()).all()


def get_session_or_raise(db: Session, session_id: int) -> StudySession:
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if session is None:
        raise SessionNotFoundError(f"Session {session_id} not found")
    return session
