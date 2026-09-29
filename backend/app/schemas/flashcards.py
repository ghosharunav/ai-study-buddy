import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.flashcard_set import FlashcardSet
from app.prompt_engine.output_schemas import FlashcardSetOutput


class GenerateFlashcardsRequest(BaseModel):
    topic: str = Field(..., examples=["Binary Search Trees"])
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    num_cards: int = Field(10, ge=1, le=20)


class FlashcardResponse(BaseModel):
    front: str
    back: str
    topic_tag: str


class FlashcardSetResponse(BaseModel):
    id: int
    session_id: int
    topic: str
    difficulty_level: str
    cards: list[FlashcardResponse]
    created_at: datetime

    @classmethod
    def from_set(cls, fset: FlashcardSet) -> "FlashcardSetResponse":
        full = FlashcardSetOutput.model_validate(json.loads(fset.cards_json))
        return cls(
            id=fset.id, session_id=fset.session_id, topic=fset.topic,
            difficulty_level=fset.difficulty_level,
            cards=[FlashcardResponse(**c.model_dump()) for c in full.cards],
            created_at=fset.created_at,
        )
