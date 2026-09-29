"""
Service layer for the AI-generated study notes / topic-explainer feature.

Same pattern as chat_service.py: this module knows about the database, the
prompt engine, and the LLM provider; routers/notes.py doesn't need to know
any of that — it just calls these functions and translates results/exceptions
into HTTP responses.
"""

from sqlalchemy.orm import Session

from app.models.note import Note
from app.prompt_engine.chains.explain_chain import generate_explanation
from app.providers.provider_factory import get_llm_provider
from app.services.session_service import get_session_or_raise


def generate_note(db: Session, session_id: int, topic: str, difficulty_level: str) -> Note:
    """
    Generates a new AI explanation for `topic` and persists it as a Note.

    Raises:
        SessionNotFoundError (from session_service) if session_id is invalid
        JSONGenerationError (from validated_generation) if the LLM can't
            produce valid structured output even after a refinement retry
        ValueError / Exception for provider config or network failures
    """
    session = get_session_or_raise(db, session_id)

    provider = get_llm_provider()
    explanation = generate_explanation(
        provider=provider,
        subject=session.subject,
        topic=topic,
        difficulty_level=difficulty_level,
    )

    note = Note(
        session_id=session.id,
        topic=topic,
        difficulty_level=difficulty_level,
        content_json=explanation.model_dump_json(),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def list_notes(db: Session, session_id: int) -> list[Note]:
    session = get_session_or_raise(db, session_id)
    return session.notes
