from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.summarize import SummarizeRequest, SummaryResponse
from app.services import summarize_service
from app.services.session_service import SessionNotFoundError
from app.prompt_engine.chains.validated_generation import JSONGenerationError

router = APIRouter(tags=["summarize"])


@router.post("/sessions/{session_id}/summarize", response_model=SummaryResponse)
def summarize_text(session_id: int, payload: SummarizeRequest, db: Session = Depends(get_db)):
    """
    Summarizes pasted study material. Long text is automatically chunked and
    summarized piece-by-piece before being combined into one structured summary.
    """
    try:
        summary = summarize_service.create_summary(db, session_id, payload.text, payload.difficulty_level)
        return SummaryResponse.from_summary(summary)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except JSONGenerationError as e:
        raise HTTPException(status_code=502, detail=f"AI response validation failed: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")


@router.get("/sessions/{session_id}/summaries", response_model=list[SummaryResponse])
def list_summaries(session_id: int, db: Session = Depends(get_db)):
    try:
        summaries = summarize_service.list_summaries(db, session_id)
        return [SummaryResponse.from_summary(s) for s in summaries]
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
