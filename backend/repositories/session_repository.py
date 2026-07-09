from pathlib import Path
import json
from typing import List

from ..models.session import Session, SessionEvent

STORAGE = Path("data/sessions")
STORAGE.mkdir(parents=True, exist_ok=True)


def session_path(session_id: str) -> Path:
    return STORAGE / f"{session_id}.json"


def session_exists(session_id: str) -> bool:
    return session_path(session_id).exists()


def save_session(session: Session) -> None:
    session_path(session.session_id).write_text(session.model_dump_json(indent=2))


def load_session(session_id: str) -> Session:
    data = json.loads(session_path(session_id).read_text())
    return Session(**data)


def list_sessions() -> List[Session]:
    sessions: List[Session] = []
    for p in STORAGE.glob("*.json"):
        try:
            data = json.loads(p.read_text())
            sessions.append(Session(**data))
        except Exception:
            continue
    return sessions


def append_event(session_id: str, event: SessionEvent) -> Session:
    session = load_session(session_id)
    session.events.append(event)
    save_session(session)
    return session
