from models.session import SessionEvent
from services.session_service import start_session, record_event, get_session
import repositories.session_repository as session_repo


def test_start_and_get_session(tmp_path, monkeypatch):
    storage = tmp_path / "sessions"
    monkeypatch.setattr(session_repo, "STORAGE", storage)
    storage.mkdir(parents=True)

    s = start_session("student123", "algebra")
    assert s.student_id == "student123"
    assert s.topic == "algebra"

    loaded = get_session(s.session_id)
    assert loaded.session_id == s.session_id


def test_record_event(tmp_path, monkeypatch):
    storage = tmp_path / "sessions"
    monkeypatch.setattr(session_repo, "STORAGE", storage)
    storage.mkdir(parents=True)

    s = start_session("studentX", None)
    ev = SessionEvent(timestamp="2026-01-01T00:00:00Z", role="tutor", content="Q1")
    updated = record_event(s.session_id, ev)
    assert len(updated.events) == 1
    assert updated.events[0].content == "Q1"
