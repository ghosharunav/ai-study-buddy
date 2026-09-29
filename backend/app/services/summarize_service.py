from sqlalchemy.orm import Session

from app.models.summary import Summary
from app.prompt_engine.chains.summarize_chain import summarize_material
from app.providers.provider_factory import get_llm_provider
from app.services.session_service import get_session_or_raise


def create_summary(db: Session, session_id: int, raw_text: str, difficulty_level: str) -> Summary:
    session = get_session_or_raise(db, session_id)

    provider = get_llm_provider()
    result = summarize_material(
        provider=provider,
        subject=session.subject,
        difficulty_level=difficulty_level,
        raw_text=raw_text,
    )

    summary = Summary(
        session_id=session.id,
        difficulty_level=difficulty_level,
        source_preview=raw_text[:300],
        content_json=result.model_dump_json(),
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


def list_summaries(db: Session, session_id: int) -> list[Summary]:
    session = get_session_or_raise(db, session_id)
    return session.summaries
