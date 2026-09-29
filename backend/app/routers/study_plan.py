from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.study_plan import GenerateStudyPlanRequest, StudyPlanResponse
from app.services import study_plan_service
from app.services.session_service import SessionNotFoundError
from app.prompt_engine.chains.validated_generation import JSONGenerationError

router = APIRouter(tags=["study-plan"])


@router.post("/sessions/{session_id}/study-plan", response_model=StudyPlanResponse)
def generate_plan(session_id: int, payload: GenerateStudyPlanRequest, db: Session = Depends(get_db)):
    """Generates a personalized study plan, automatically informed by this session's weak topics."""
    try:
        plan = study_plan_service.create_study_plan(db, session_id, payload.goal, payload.num_days)
        return StudyPlanResponse.from_plan(plan)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except JSONGenerationError as e:
        raise HTTPException(status_code=502, detail=f"AI response validation failed: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")


@router.get("/sessions/{session_id}/study-plans", response_model=list[StudyPlanResponse])
def list_plans(session_id: int, db: Session = Depends(get_db)):
    try:
        plans = study_plan_service.list_study_plans(db, session_id)
        return [StudyPlanResponse.from_plan(p) for p in plans]
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
