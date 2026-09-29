from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.quiz import (
    GenerateQuizRequest,
    QuizResponse,
    SubmitQuizAttemptRequest,
    QuizAttemptResponse,
    QuestionResult,
)
from app.services import quiz_service
from app.services.session_service import SessionNotFoundError
from app.prompt_engine.chains.validated_generation import JSONGenerationError

router = APIRouter(tags=["quiz"])


@router.post("/sessions/{session_id}/quiz", response_model=QuizResponse)
def generate_quiz(session_id: int, payload: GenerateQuizRequest, db: Session = Depends(get_db)):
    """
    Generates a new quiz for this session. The response deliberately does NOT
    include correct answers or explanations — see /quizzes/{quiz_id}/submit.
    """
    try:
        quiz = quiz_service.generate_quiz(
            db, session_id, payload.topic, payload.difficulty_level, payload.num_questions
        )
        return QuizResponse.from_quiz(quiz)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except JSONGenerationError as e:
        raise HTTPException(status_code=502, detail=f"AI response validation failed: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Re-fetch a previously generated quiz (e.g. if the student reloads the page)."""
    try:
        quiz = quiz_service.get_quiz_or_raise(db, quiz_id)
        return QuizResponse.from_quiz(quiz)
    except quiz_service.QuizNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizAttemptResponse)
def submit_quiz(quiz_id: int, payload: SubmitQuizAttemptRequest, db: Session = Depends(get_db)):
    """
    Scores the submitted answers against the stored answer key and returns
    the full breakdown — correct answers, explanations, and which sub-topics
    the student got wrong (weak_topics).
    """
    try:
        attempt, results = quiz_service.submit_attempt(db, quiz_id, payload.answers)
        return QuizAttemptResponse(
            id=attempt.id,
            quiz_id=attempt.quiz_id,
            score=attempt.score,
            total=attempt.total,
            weak_topics=list(dict.fromkeys(  # dedupe while preserving order
                r["topic_tag"] for r in results if not r["is_correct"]
            )),
            results=[QuestionResult(**r) for r in results],
            created_at=attempt.created_at,
        )
    except quiz_service.QuizNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
