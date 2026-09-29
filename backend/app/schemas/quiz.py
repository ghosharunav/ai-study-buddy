import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.quiz import Quiz
from app.prompt_engine.output_schemas import QuizOutput


class GenerateQuizRequest(BaseModel):
    topic: str = Field(..., examples=["Binary Search Trees"])
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    num_questions: int = Field(5, ge=1, le=10)


class QuizQuestionResponse(BaseModel):
    """
    Deliberately SANITIZED — no correct_answer_index, no explanation.
    This is what the student sees while taking the quiz; the full answer
    key only comes back after they submit (see QuestionResult below).
    """
    question: str
    options: list[str]
    topic_tag: str


class QuizResponse(BaseModel):
    id: int
    session_id: int
    topic: str
    difficulty_level: str
    questions: list[QuizQuestionResponse]
    created_at: datetime

    @classmethod
    def from_quiz(cls, quiz: Quiz) -> "QuizResponse":
        full = QuizOutput.model_validate(json.loads(quiz.questions_json))
        sanitized = [
            QuizQuestionResponse(question=q.question, options=q.options, topic_tag=q.topic_tag)
            for q in full.questions
        ]
        return cls(
            id=quiz.id,
            session_id=quiz.session_id,
            topic=quiz.topic,
            difficulty_level=quiz.difficulty_level,
            questions=sanitized,
            created_at=quiz.created_at,
        )


class SubmitQuizAttemptRequest(BaseModel):
    answers: list[int] = Field(
        ...,
        description="Selected option index (0-3) for each question, in the same order as the quiz's questions.",
    )


class QuestionResult(BaseModel):
    """The full reveal, shown only after submission."""
    question: str
    options: list[str]
    selected_answer_index: int
    correct_answer_index: int
    is_correct: bool
    explanation: str
    topic_tag: str


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    score: int
    total: int
    weak_topics: list[str]
    results: list[QuestionResult]
    created_at: datetime
