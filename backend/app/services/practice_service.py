import json

from sqlalchemy.orm import Session

from app.models.practice_set import PracticeQuestionSet
from app.prompt_engine.chains.practice_chain import generate_practice_questions, get_practice_feedback
from app.prompt_engine.output_schemas import PracticeQuestionSetOutput, PracticeFeedbackOutput
from app.providers.provider_factory import get_llm_provider
from app.services.session_service import get_session_or_raise


class PracticeSetNotFoundError(Exception):
    """Raised when a practice question set_id doesn't exist."""
    pass


def generate_practice_set(db: Session, session_id: int, topic: str,
                           difficulty_level: str, num_questions: int) -> PracticeQuestionSet:
    session = get_session_or_raise(db, session_id)

    provider = get_llm_provider()
    result = generate_practice_questions(
        provider=provider,
        subject=session.subject,
        topic=topic,
        difficulty_level=difficulty_level,
        num_questions=num_questions,
    )

    pset = PracticeQuestionSet(
        session_id=session.id,
        topic=topic,
        difficulty_level=difficulty_level,
        questions_json=result.model_dump_json(),
    )
    db.add(pset)
    db.commit()
    db.refresh(pset)
    return pset


def get_practice_set_or_raise(db: Session, set_id: int) -> PracticeQuestionSet:
    pset = db.query(PracticeQuestionSet).filter(PracticeQuestionSet.id == set_id).first()
    if pset is None:
        raise PracticeSetNotFoundError(f"Practice question set {set_id} not found")
    return pset


def get_feedback(db: Session, set_id: int, question_index: int, student_answer: str) -> PracticeFeedbackOutput:
    pset = get_practice_set_or_raise(db, set_id)
    full = PracticeQuestionSetOutput.model_validate(json.loads(pset.questions_json))

    if question_index < 0 or question_index >= len(full.questions):
        raise ValueError(
            f"question_index {question_index} out of range (0-{len(full.questions) - 1})"
        )

    question = full.questions[question_index]
    provider = get_llm_provider()
    return get_practice_feedback(
        provider=provider,
        subject=pset.session.subject,
        question=question.question,
        ideal_answer_points=question.ideal_answer_points,
        student_answer=student_answer,
    )
