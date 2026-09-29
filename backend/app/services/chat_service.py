"""
Service layer for the chat feature specifically.

Session creation/lookup now lives in session_service.py (shared across
features) — this file only re-exports what routers/chat.py needs so that
file's imports don't have to change, and focuses on the chat-specific
logic: sending a message and getting a reply.
"""

from sqlalchemy.orm import Session

from app.models.message import Message
from app.prompt_engine.prompt_builder import build_chat_prompt
from app.providers.provider_factory import get_llm_provider
from app.services.session_service import (  # noqa: F401  (re-exported for routers/chat.py)
    SessionNotFoundError,
    create_session,
    list_sessions,
    get_session_or_raise,
)


def get_messages(db: Session, session_id: int) -> list[Message]:
    session = get_session_or_raise(db, session_id)
    return session.messages


def send_message(db: Session, session_id: int, user_text: str) -> tuple[Message, Message]:
    """
    The core of the conversational assistant:
      1. load the session + recent history (context)
      2. persist the student's message immediately (so it's never lost,
         even if the LLM call below fails)
      3. build a role-prompted, context-aware prompt via the prompt engine
      4. call the active LLM provider
      5. persist and return the assistant's reply

    Raises:
        SessionNotFoundError if session_id is invalid
        Whatever the provider raises (ValueError for config issues,
        or a generic Exception for provider/network failures) — the
        router maps these to appropriate HTTP status codes.
    """
    session = get_session_or_raise(db, session_id)
    history = session.messages  # already ordered by created_at via the relationship

    user_message = Message(session_id=session.id, role="user", content=user_text)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    system_instruction, prompt = build_chat_prompt(
        subject=session.subject,
        difficulty_level=session.difficulty_level,
        history=history,
        user_message=user_text,
    )

    provider = get_llm_provider()
    response_text = provider.generate(
        prompt=prompt,
        system_instruction=system_instruction,
        temperature=0.7,
        max_tokens=800,
    )

    assistant_message = Message(session_id=session.id, role="assistant", content=response_text)
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return user_message, assistant_message
