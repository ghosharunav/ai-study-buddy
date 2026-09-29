import json
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.study_material import StudyMaterial


class MaterialResponse(BaseModel):
    id: int
    session_id: int
    filename: str
    num_chunks: int
    created_at: datetime

    @classmethod
    def from_material(cls, material: StudyMaterial) -> "MaterialResponse":
        return cls(
            id=material.id, session_id=material.session_id, filename=material.filename,
            num_chunks=len(json.loads(material.chunks_json)), created_at=material.created_at,
        )


class AskMaterialRequest(BaseModel):
    question: str = Field(..., min_length=1)


class AskMaterialResponse(BaseModel):
    answer: str
    grounded: bool
    source_chunk_indices: list[int]
