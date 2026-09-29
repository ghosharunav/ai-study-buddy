from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.practice import (
    GeneratePracticeRequest,
    PracticeSetResponse,
    SubmitPracticeAnswerRequest,
    PracticeFeedbackResponse,
)
from app.services import practice_service
from app.services.session_service import SessionNotFoundError
from app.prompt_engine.chains.validated_generation import JSONGenerationError

router = APIRouter(tags=["practice"])


@router.post("/sessions/{session_id}/practice", response_model=PracticeSetResponse)
def generate_practice(session_id: int, payload: GeneratePracticeRequest, db: Session = Depends(get_db)):
    """Generates a set of open-ended practice questions with self-check checklists."""
    try:
        pset = practice_service.generate_practice_set(
            db, session_id, payload.topic, payload.difficulty_level, payload.num_questions
        )
        return PracticeSetResponse.from_set(pset)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except JSONGenerationError as e:
        raise HTTPException(status_code=502, detail=f"AI response validation failed: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")


@router.get("/practice/{set_id}", response_model=PracticeSetResponse)
def get_practice_set(set_id: int, db: Session = Depends(get_db)):
    try:
        pset = practice_service.get_practice_set_or_raise(db, set_id)
        return PracticeSetResponse.from_set(pset)
    except practice_service.PracticeSetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/practice/{set_id}/feedback", response_model=PracticeFeedbackResponse)
def submit_practice_answer(set_id: int, payload: SubmitPracticeAnswerRequest, db: Session = Depends(get_db)):
    """Submit a written answer to one practice question and get AI feedback against its checklist."""
    try:
        feedback = practice_service.get_feedback(db, set_id, payload.question_index, payload.answer)
        return PracticeFeedbackResponse(**feedback.model_dump())
    except practice_service.PracticeSetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except JSONGenerationError as e:
        raise HTTPException(status_code=502, detail=f"AI response validation failed: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")
