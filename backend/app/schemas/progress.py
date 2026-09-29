from pydantic import BaseModel


class TopicMastery(BaseModel):
    topic_tag: str
    attempts: int
    correct: int
    accuracy: float


class SessionProgressResponse(BaseModel):
    session_id: int
    subject: str
    current_difficulty: str
    total_quizzes_taken: int
    total_questions_answered: int
    overall_accuracy: float | None
    topic_mastery: list[TopicMastery]
    weak_topics: list[str]
    suggested_difficulty: str | None
