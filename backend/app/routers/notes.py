from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.notes import ExplainRequest, NoteResponse
from app.services import notes_service
from app.services.session_service import SessionNotFoundError
from app.prompt_engine.chains.validated_generation import JSONGenerationError

router = APIRouter(tags=["notes"])


@router.post("/sessions/{session_id}/explain", response_model=NoteResponse)
def explain_topic(session_id: int, payload: ExplainRequest, db: Session = Depends(get_db)):
    """
    Generates an AI explanation of `topic` at the requested difficulty level
    (beginner / intermediate / advanced / eli5) and saves it as a study note
    on this session.
    """
    try:
        note = notes_service.generate_note(db, session_id, payload.topic, payload.difficulty_level)
        return NoteResponse.from_note(note)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except JSONGenerationError as e:
        # The model never produced valid structured output, even after
        # one refinement attempt — surfaced distinctly from a plain
        # network/provider failure so the frontend/dev can tell them apart.
        raise HTTPException(status_code=502, detail=f"AI response validation failed: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")


@router.get("/sessions/{session_id}/notes", response_model=list[NoteResponse])
def list_notes(session_id: int, db: Session = Depends(get_db)):
    """All study notes generated so far in this session, oldest first."""
    try:
        notes = notes_service.list_notes(db, session_id)
        return [NoteResponse.from_note(n) for n in notes]
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
