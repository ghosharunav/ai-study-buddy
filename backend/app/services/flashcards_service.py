from sqlalchemy.orm import Session

from app.models.flashcard_set import FlashcardSet
from app.prompt_engine.chains.flashcards_chain import generate_flashcards
from app.providers.provider_factory import get_llm_provider
from app.services.session_service import get_session_or_raise


class FlashcardSetNotFoundError(Exception):
    pass


def generate_flashcard_set(db: Session, session_id: int, topic: str,
                            difficulty_level: str, num_cards: int) -> FlashcardSet:
    session = get_session_or_raise(db, session_id)
    provider = get_llm_provider()
    result = generate_flashcards(provider, session.subject, topic, difficulty_level, num_cards)

    fset = FlashcardSet(
        session_id=session.id, topic=topic, difficulty_level=difficulty_level,
        cards_json=result.model_dump_json(),
    )
    db.add(fset)
    db.commit()
    db.refresh(fset)
    return fset


def list_flashcard_sets(db: Session, session_id: int) -> list[FlashcardSet]:
    session = get_session_or_raise(db, session_id)
    return session.flashcard_sets


def get_flashcard_set_or_raise(db: Session, set_id: int) -> FlashcardSet:
    fset = db.query(FlashcardSet).filter(FlashcardSet.id == set_id).first()
    if fset is None:
        raise FlashcardSetNotFoundError(f"Flashcard set {set_id} not found")
    return fset
