import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.practice_set import PracticeQuestionSet


class GeneratePracticeRequest(BaseModel):
    topic: str = Field(..., examples=["Binary Search Trees"])
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    num_questions: int = Field(5, ge=1, le=10)


class PracticeQuestionResponse(BaseModel):
    """
    Unlike the quiz's sanitized response, ideal_answer_points ARE shown
    upfront — there's no single correct index to leak with open-ended
    questions, and the checklist itself is useful study material.
    """
    question: str
    ideal_answer_points: list[str]
    topic_tag: str


class PracticeSetResponse(BaseModel):
    id: int
    session_id: int
    topic: str
    difficulty_level: str
    questions: list[PracticeQuestionResponse]
    created_at: datetime

    @classmethod
    def from_set(cls, pset: PracticeQuestionSet) -> "PracticeSetResponse":
        from app.prompt_engine.output_schemas import PracticeQuestionSetOutput
        full = PracticeQuestionSetOutput.model_validate(json.loads(pset.questions_json))
        return cls(
            id=pset.id,
            session_id=pset.session_id,
            topic=pset.topic,
            difficulty_level=pset.difficulty_level,
            questions=[
                PracticeQuestionResponse(
                    question=q.question,
                    ideal_answer_points=q.ideal_answer_points,
                    topic_tag=q.topic_tag,
                )
                for q in full.questions
            ],
            created_at=pset.created_at,
        )


class SubmitPracticeAnswerRequest(BaseModel):
    question_index: int = Field(..., ge=0)
    answer: str = Field(..., min_length=1)


class PracticeFeedbackResponse(BaseModel):
    covered_points: list[str]
    missed_points: list[str]
    overall_feedback: str
    score_estimate: int
