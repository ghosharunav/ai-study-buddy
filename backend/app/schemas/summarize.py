import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.summary import Summary
from app.prompt_engine.output_schemas import SummaryOutput


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=50, examples=["Paste your lecture notes or textbook excerpt here..."])
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = "beginner"


class SummaryResponse(BaseModel):
    id: int
    session_id: int
    difficulty_level: str
    content: SummaryOutput
    created_at: datetime

    @classmethod
    def from_summary(cls, summary: Summary) -> "SummaryResponse":
        content = SummaryOutput.model_validate(json.loads(summary.content_json))
        return cls(
            id=summary.id,
            session_id=summary.session_id,
            difficulty_level=summary.difficulty_level,
            content=content,
            created_at=summary.created_at,
        )
