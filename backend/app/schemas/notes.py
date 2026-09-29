import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.note import Note
from app.prompt_engine.output_schemas import ExplanationOutput


class ExplainRequest(BaseModel):
    topic: str = Field(..., examples=["Binary Search Trees"])
    difficulty_level: Literal["beginner", "intermediate", "advanced", "eli5"] = "beginner"


class NoteResponse(BaseModel):
    id: int
    session_id: int
    topic: str
    difficulty_level: str
    content: ExplanationOutput  # the validated, structured explanation
    created_at: datetime

    @classmethod
    def from_note(cls, note: Note) -> "NoteResponse":
        """Builds the API response by re-parsing the stored, already-validated JSON."""
        content = ExplanationOutput.model_validate(json.loads(note.content_json))
        return cls(
            id=note.id,
            session_id=note.session_id,
            topic=note.topic,
            difficulty_level=note.difficulty_level,
            content=content,
            created_at=note.created_at,
        )
