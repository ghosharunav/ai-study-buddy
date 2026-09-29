from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.providers.provider_factory import get_llm_provider
from app.database import Base, engine
from app.routers import chat as chat_router
from app.routers import notes as notes_router
from app.routers import quiz as quiz_router
from app.routers import summarize as summarize_router
from app.routers import practice as practice_router
from app.routers import flashcards as flashcards_router
from app.routers import progress as progress_router
from app.routers import study_plan as study_plan_router
from app.routers import materials as materials_router

# Importing app.models (even though unused directly here) registers the
# StudySession and Message classes with Base.metadata, so create_all below
# actually knows to create their tables.
import app.models  # noqa: F401

app = FastAPI(
    title="AI Study Buddy API",
    description="Backend for the AI Study Buddy generative-AI tutoring app.",
    version="0.1.0",
)

# Allow the React frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Creates SQLite tables on first run. Safe to call every startup —
    it only creates tables that don't already exist, never touches existing data."""
    Base.metadata.create_all(bind=engine)


app.include_router(chat_router.router, prefix="/api")
app.include_router(notes_router.router, prefix="/api")
app.include_router(quiz_router.router, prefix="/api")
app.include_router(summarize_router.router, prefix="/api")
app.include_router(practice_router.router, prefix="/api")
app.include_router(flashcards_router.router, prefix="/api")
app.include_router(progress_router.router, prefix="/api")
app.include_router(study_plan_router.router, prefix="/api")
app.include_router(materials_router.router, prefix="/api")


@app.get("/api/health")
def health_check():
    """Quick check that the server is up and which LLM provider is configured."""
    return {
        "status": "ok",
        "active_llm_provider": settings.llm_provider,
    }


class TestLLMRequest(BaseModel):
    prompt: str = "Say hello to a student and tell them you're ready to help them study."


@app.post("/api/test-llm")
def test_llm(payload: TestLLMRequest):
    """
    Phase 0 sanity check: proves the full chain works —
    FastAPI route -> provider factory -> real LLM API call -> response.

    Nothing here is study-buddy-specific yet. Phase 1+ will replace this
    with real endpoints (/api/chat, /api/quiz, etc.) that go through the
    prompt-engineering layer instead of a raw prompt like this.
    """
    try:
        provider = get_llm_provider()
        response_text = provider.generate(
            prompt=payload.prompt,
            system_instruction="You are a friendly, encouraging AI study tutor.",
            temperature=0.7,
            max_tokens=300,
        )
        return {
            "provider": provider.provider_name,
            "response": response_text,
        }
    except ValueError as e:
        # Config issues (e.g. missing API key) -> clear 400, not a crash
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Provider/network errors -> 502 so the frontend can distinguish
        # "your fault" (400) from "the AI service failed" (502)
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")
