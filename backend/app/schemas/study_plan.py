import json
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.study_plan import StudyPlan
from app.prompt_engine.output_schemas import StudyPlanOutput


class GenerateStudyPlanRequest(BaseModel):
    goal: str = Field(..., examples=["Pass my midterm on data structures"])
    num_days: int = Field(7, ge=1, le=14)


class StudyPlanDayResponse(BaseModel):
    day_number: int
    focus_topics: list[str]
    activities: list[str]
    estimated_minutes: int


class StudyPlanResponse(BaseModel):
    id: int
    session_id: int
    goal: str
    days: list[StudyPlanDayResponse]
    created_at: datetime

    @classmethod
    def from_plan(cls, plan: StudyPlan) -> "StudyPlanResponse":
        full = StudyPlanOutput.model_validate(json.loads(plan.plan_json))
        return cls(
            id=plan.id, session_id=plan.session_id, goal=plan.goal,
            days=[StudyPlanDayResponse(**d.model_dump()) for d in full.days],
            created_at=plan.created_at,
        )
