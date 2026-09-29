"""
Service layer for the quiz feature: generation, retrieval, and scoring.

Scoring logic lives here (not in the router) because it's genuine business
logic — comparing submitted answers against the stored answer key and
extracting weak topics is exactly the kind of thing that should be unit-
testable independent of HTTP.
"""

import json

from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.prompt_engine.chains.quiz_chain import generate_quiz as run_quiz_chain
from app.prompt_engine.output_schemas import QuizOutput
from app.providers.provider_factory import get_llm_provider
from app.services.session_service import get_session_or_raise


class QuizNotFoundError(Exception):
    """Raised when a quiz_id doesn't exist in the database."""
    pass


def generate_quiz(db: Session, session_id: int, topic: str,
                   difficulty_level: str, num_questions: int) -> Quiz:
    """
    Raises:
        SessionNotFoundError (from session_service) if session_id is invalid
        JSONGenerationError (from validated_generation) if the LLM can't
            produce valid structured output even after refinement
        ValueError / Exception for provider config or network failures
    """
    session = get_session_or_raise(db, session_id)

    provider = get_llm_provider()
    quiz_output = run_quiz_chain(
        provider=provider,
        subject=session.subject,
        topic=topic,
        difficulty_level=difficulty_level,
        num_questions=num_questions,
    )

    quiz = Quiz(
        session_id=session.id,
        topic=topic,
        difficulty_level=difficulty_level,
        questions_json=quiz_output.model_dump_json(),
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def get_quiz_or_raise(db: Session, quiz_id: int) -> Quiz:
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz is None:
        raise QuizNotFoundError(f"Quiz {quiz_id} not found")
    return quiz


def submit_attempt(db: Session, quiz_id: int, answers: list[int]) -> tuple[QuizAttempt, list[dict]]:
    """
    Scores a submitted attempt against the stored answer key.

    Returns:
        (the saved QuizAttempt row, a list of per-question result dicts
         ready to build QuestionResult schemas from)

    Raises:
        QuizNotFoundError if quiz_id is invalid
        ValueError if the number of answers doesn't match the number of questions
    """
    quiz = get_quiz_or_raise(db, quiz_id)
    quiz_output = QuizOutput.model_validate(json.loads(quiz.questions_json))

    if len(answers) != len(quiz_output.questions):
        raise ValueError(
            f"Expected {len(quiz_output.questions)} answers, got {len(answers)}"
        )

    results = []
    score = 0
    weak_topics: list[str] = []

    for question, selected_index in zip(quiz_output.questions, answers):
        is_correct = selected_index == question.correct_answer_index
        if is_correct:
            score += 1
        else:
            weak_topics.append(question.topic_tag)

        results.append({
            "question": question.question,
            "options": question.options,
            "selected_answer_index": selected_index,
            "correct_answer_index": question.correct_answer_index,
            "is_correct": is_correct,
            "explanation": question.explanation,
            "topic_tag": question.topic_tag,
        })

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        score=score,
        total=len(quiz_output.questions),
        answers_json=json.dumps(answers),
        weak_topics_json=json.dumps(weak_topics),
        results_json=json.dumps([
            {"topic_tag": r["topic_tag"], "is_correct": r["is_correct"]} for r in results
        ]),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt, results
