from fastapi.testclient import TestClient

from main import app
import repositories.profile_repository as profile_repo
import repositories.session_repository as session_repo


def test_end_to_end(tmp_path, monkeypatch):
    # redirect storage to temp dirs
    monkeypatch.setattr(profile_repo, "STORAGE", tmp_path / "profiles")
    monkeypatch.setattr(session_repo, "STORAGE", tmp_path / "sessions")
    (tmp_path / "profiles").mkdir()
    (tmp_path / "sessions").mkdir()

    client = TestClient(app)

    # health
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"

    # create profile
    r = client.post(
        "/onboarding/create",
        json={"name": "Integration Student", "grade": "11"},
    )
    assert r.status_code == 200
    profile = r.json()
    sid = profile["student_id"]

    # list profiles
    r = client.get("/onboarding/")
    assert r.status_code == 200
    assert any(p["student_id"] == sid for p in r.json())

    # start session
    r = client.post("/sessions/start", json={"student_id": sid, "topic": "algebra"})
    assert r.status_code == 200
    sess = r.json()
    session_id = sess["session_id"]

    # post event
    ev = {"timestamp": "2026-06-04T00:00:00Z", "role": "student", "content": "I have trouble with algebra."}
    r = client.post(f"/sessions/{session_id}/events", json=ev)
    assert r.status_code == 200
    res = r.json()
    assert len(res.get("events", [])) == 1

    # get session
    r = client.get(f"/sessions/{session_id}")
    assert r.status_code == 200
    s = r.json()
    assert s["student_id"] == sid
