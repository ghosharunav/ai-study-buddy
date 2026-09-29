from sqlalchemy.orm import Session

from app.models.study_plan import StudyPlan
from app.prompt_engine.chains.study_plan_chain import generate_study_plan
from app.providers.provider_factory import get_llm_provider
from app.services.session_service import get_session_or_raise
from app.services.progress_service import compute_session_progress


def create_study_plan(db: Session, session_id: int, goal: str, num_days: int) -> StudyPlan:
    session = get_session_or_raise(db, session_id)

    # Pulls REAL weak-topic data (see progress_service.py) into the prompt —
    # this is what makes the plan "personalized" rather than generic advice.
    progress = compute_session_progress(db, session_id)
    weak_topics = progress["weak_topics"]

    provider = get_llm_provider()
    result = generate_study_plan(
        provider, session.subject, session.difficulty_level, goal, weak_topics, num_days
    )

    plan = StudyPlan(session_id=session.id, goal=goal, plan_json=result.model_dump_json())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def list_study_plans(db: Session, session_id: int) -> list[StudyPlan]:
    session = get_session_or_raise(db, session_id)
    return session.study_plans
