from fastapi import APIRouter
from typing import List, Optional

from pydantic import BaseModel

from ..models.session import Session, SessionEvent
from ..services.session_service import (
    start_session as start_session_service,
    record_event as record_event_service,
    get_session as get_session_service,
    list_all_sessions as list_sessions_service,
)


class StartSessionRequest(BaseModel):
    student_id: str
    topic: Optional[str] = None


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=Session)
def start_session(req: StartSessionRequest):
    return start_session_service(req.student_id, req.topic)


@router.post("/{session_id}/events", response_model=Session)
def post_event(session_id: str, event: SessionEvent):
    return record_event_service(session_id, event)


@router.get("/{session_id}", response_model=Session)
def get_session(session_id: str):
    return get_session_service(session_id)


@router.get("/", response_model=List[Session])
def list_sessions(student_id: Optional[str] = None):
    return list_sessions_service(student_id)
