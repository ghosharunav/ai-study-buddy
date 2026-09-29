from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import (
    CreateSessionRequest,
    SessionResponse,
    MessageResponse,
    ChatRequest,
    ChatResponse,
)
from app.services import chat_service
from app.services import session_service

router = APIRouter(tags=["chat"])


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Fetch one session's details (subject, difficulty, title) — used by the frontend header."""
    try:
        return session_service.get_session_or_raise(db, session_id)
    except session_service.SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions", response_model=SessionResponse)
def create_session(payload: CreateSessionRequest, db: Session = Depends(get_db)):
    """Start a new study session (a subject + difficulty combo the student is working on)."""
    session = chat_service.create_session(
        db, subject=payload.subject,
        difficulty_level=payload.difficulty_level,
        title=payload.title,
    )
    return session


@router.get("/sessions", response_model=list[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    """Study history: all past and current sessions, most recently active first."""
    return chat_service.list_sessions(db)


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    """Full transcript for one session — used to reload a chat when reopened."""
    try:
        return chat_service.get_messages(db, session_id)
    except chat_service.SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/chat", response_model=ChatResponse)
def chat(session_id: int, payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message to the AI tutor within a session. The prompt sent to the
    LLM is built by the prompt engine using this session's subject,
    difficulty, and prior message history — see prompt_engine/prompt_builder.py.
    """
    try:
        user_message, assistant_message = chat_service.send_message(db, session_id, payload.message)
        return ChatResponse(
            session_id=session_id,
            user_message=user_message,
            assistant_message=assistant_message,
        )
    except chat_service.SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        # config issue, e.g. missing API key — bubbled up from the provider
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # provider/network failure — the user's message is already saved,
        # so nothing is lost; they can just retry
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")
