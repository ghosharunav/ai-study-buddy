"""
STRUCTURED JSON OUTPUT — schema definitions.

These Pydantic models are the exact contract every structured-generation
feature enforces on the LLM's response. They are used by
prompt_engine/chains/validated_generation.py to validate (and, on failure,
trigger a refinement retry for) whatever JSON the model returns.

This is the single source of truth for "what does a valid AI response look
like" for each feature — routers and services never define this shape
themselves, they just import it from here.
"""

from pydantic import BaseModel, Field


class ExplanationOutput(BaseModel):
    """The structured shape required from the topic-explainer feature."""
    topic: str
    difficulty_level: str
    summary: str
    key_points: list[str] = Field(..., min_length=1)
    analogy: str
    common_mistakes: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)


class QuizQuestionOutput(BaseModel):
    """One MCQ. topic_tag is a short sub-topic label (e.g. 'tree-traversal') —
    not shown to the student, but stored so later phases can aggregate which
    sub-topics a student gets wrong most often (weak-topic detection)."""
    question: str
    options: list[str] = Field(..., min_length=4, max_length=4)
    correct_answer_index: int = Field(..., ge=0, le=3)
    explanation: str
    topic_tag: str


class QuizOutput(BaseModel):
    """The structured shape required from the quiz-generator feature."""
    topic: str
    difficulty_level: str
    questions: list[QuizQuestionOutput] = Field(..., min_length=1)


class TermDefinition(BaseModel):
    term: str
    definition: str


class SummaryOutput(BaseModel):
    """The structured shape required from the study-material summarizer."""
    title: str
    overview: str
    key_points: list[str] = Field(..., min_length=1)
    important_terms: list[TermDefinition] = Field(default_factory=list)
    suggested_next_steps: list[str] = Field(default_factory=list)


class PracticeQuestionOutput(BaseModel):
    """One open-ended practice question. ideal_answer_points is a self-check
    checklist, not a single 'model answer' to copy — the student self-grades
    against it, or submits their answer for AI feedback (see PracticeFeedbackOutput)."""
    question: str
    ideal_answer_points: list[str] = Field(..., min_length=1)
    topic_tag: str


class PracticeQuestionSetOutput(BaseModel):
    """The structured shape required from the practice-question generator."""
    topic: str
    difficulty_level: str
    questions: list[PracticeQuestionOutput] = Field(..., min_length=1)


class PracticeFeedbackOutput(BaseModel):
    """AI feedback on a student's written answer to one practice question."""
    covered_points: list[str] = Field(default_factory=list)
    missed_points: list[str] = Field(default_factory=list)
    overall_feedback: str
    score_estimate: int = Field(..., ge=0, le=100)


class FlashcardOutput(BaseModel):
    front: str
    back: str
    topic_tag: str


class FlashcardSetOutput(BaseModel):
    """The structured shape required from the flashcard generator."""
    topic: str
    difficulty_level: str
    cards: list[FlashcardOutput] = Field(..., min_length=1)


class StudyPlanDayOutput(BaseModel):
    day_number: int
    focus_topics: list[str] = Field(..., min_length=1)
    activities: list[str] = Field(..., min_length=1)
    estimated_minutes: int = Field(..., ge=5, le=240)


class StudyPlanOutput(BaseModel):
    """The structured shape required from the study-plan generator."""
    subject: str
    goal: str
    days: list[StudyPlanDayOutput] = Field(..., min_length=1)


class MaterialAnswerOutput(BaseModel):
    """The structured shape required when answering a question grounded in
    uploaded study material (RAG-lite)."""
    answer: str
    grounded: bool  # whether the retrieved excerpts actually contained the answer
    source_chunk_indices: list[int] = Field(default_factory=list)
