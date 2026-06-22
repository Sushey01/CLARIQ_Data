"""
Chat router — Exposes the Socratic tutoring endpoint.

POST /sessions/{session_id}/chat
  Body: { "message": "student question here" }
  Returns: { "reply": "...", "sources": [...], "hint_depth": N }
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.session import SessionEvent
from services.session_service import get_session, record_event
from services.chat_service import generate_socratic_response, reset_hint_depth

router = APIRouter(prefix="/sessions", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class SourceInfo(BaseModel):
    source_pdf: str | None = None
    page: int = 0
    similarity: float = 0.0


class ChatResponse(BaseModel):
    reply: str
    sources: list[SourceInfo] = []
    hint_depth: int = 0
    model_used: str = ""
    fallback: bool = False


@router.post("/{session_id}/chat", response_model=ChatResponse)
def chat(session_id: str, req: ChatRequest):
    """
    Send a student message and receive a Socratic tutor response.

    The endpoint:
    1. Validates the session exists
    2. Searches the curriculum vector DB for relevant context
    3. Generates a Socratic response via Ollama
    4. Logs both student and tutor messages as session events
    5. Returns the tutor response with source citations
    """

    # 1. Validate session
    session = get_session(session_id)

    # 2. Extract conversation history from session events
    events = [ev.model_dump() for ev in session.events]

    # 3. Generate Socratic response
    result = generate_socratic_response(
        session_id=session_id,
        message=req.message,
        events=events,
        topic=session.topic,
    )

    # 4. Log student message as event
    now = datetime.now(timezone.utc).isoformat()
    student_event = SessionEvent(
        timestamp=now,
        role="student",
        content=req.message,
    )
    record_event(session_id, student_event)

    # 5. Log tutor response as event
    tutor_event = SessionEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        role="tutor",
        content=result["reply"],
        metadata={
            "sources": result["sources"],
            "hint_depth": result["hint_depth"],
            "model_used": result["model_used"],
        },
    )
    record_event(session_id, tutor_event)

    return ChatResponse(**result)


@router.post("/{session_id}/chat/reset", status_code=204)
def reset_hints(session_id: str):
    """Reset the hint depth for a session (e.g., student moves to a new topic)."""
    # Validate session exists
    get_session(session_id)
    reset_hint_depth(session_id)
