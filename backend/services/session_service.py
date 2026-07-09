from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException

from ..models.session import Session, SessionEvent
from ..repositories.session_repository import (
    save_session,
    load_session,
    session_exists,
    list_sessions,
    append_event,
)


def start_session(student_id: str, topic: str | None = None) -> Session:
    session_id = str(uuid4())
    started_at = datetime.now(timezone.utc).isoformat()
    session = Session(
        session_id=session_id,
        student_id=student_id,
        topic=topic,
        started_at=started_at,
        events=[],
    )
    save_session(session)
    return session


def record_event(session_id: str, event: SessionEvent) -> Session:
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return append_event(session_id, event)


def get_session(session_id: str) -> Session:
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return load_session(session_id)


def list_all_sessions(student_id: str | None = None) -> list[Session]:
    sessions = list_sessions()
    if student_id:
        sessions = [s for s in sessions if s.student_id == student_id]
    return sessions
