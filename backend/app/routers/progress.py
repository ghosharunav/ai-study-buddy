from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.progress import SessionProgressResponse
from app.services import progress_service
from app.services.session_service import SessionNotFoundError

router = APIRouter(tags=["progress"])


@router.get("/sessions/{session_id}/progress", response_model=SessionProgressResponse)
def get_progress(session_id: int, db: Session = Depends(get_db)):
    """
    Weak-topic detection + adaptive difficulty suggestion, computed from
    every quiz attempt in this session. No LLM call — pure aggregation.
    """
    try:
        return progress_service.compute_session_progress(db, session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
