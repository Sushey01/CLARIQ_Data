import uuid
import time


class SessionManager:
    """Simple in-memory session manager for Socratic sessions.

    This is a lightweight prototype to support the React init flow.
    Replace with persistent store (Redis/DB) for production.
    """

    def __init__(self):
        self.sessions = {}

    def create_session(self, student_id: str):
        sid = str(uuid.uuid4())
        # Basic initial student level and strategy - can be improved
        session = {
            "session_id": sid,
            "student_id": student_id,
            "created_at": int(time.time()),
            "studentLevel": "novice",
            "preferredStrategy": "fact_first",
            "profile": {"skills": {}, "meta": {}},
        }
        self.sessions[sid] = session
        return session

    def get_session(self, session_id: str):
        return self.sessions.get(session_id)

    def update_profile(self, session_id: str, profile_updates: dict):
        session = self.sessions.get(session_id)
        if not session:
            return None
        session_profile = session.setdefault("profile", {})
        session_profile.update(profile_updates)
        return session
