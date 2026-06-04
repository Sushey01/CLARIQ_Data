import json
import urllib.request
import urllib.error
from typing import Optional


class SocraticEngine:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base = base_url.rstrip("")

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            raise RuntimeError(e.read().decode())

    def create_profile(self, name: str, grade: Optional[str] = None) -> dict:
        payload = {"name": name}
        if grade:
            payload["grade"] = grade
        return self._post("/onboarding/create", payload)

    def start_session(self, student_id: str, topic: Optional[str] = None) -> dict:
        return self._post("/sessions/start", {"student_id": student_id, "topic": topic})

    def post_event(self, session_id: str, role: str, content: str, timestamp: str) -> dict:
        return self._post(f"/sessions/{session_id}/events", {"timestamp": timestamp, "role": role, "content": content})


def repl(base_url: str = "http://127.0.0.1:8000"):
    eng = SocraticEngine(base_url)
    print("Socratic Engine CLI — will call backend at", base_url)
    name = input("Student name: ").strip()
    prof = eng.create_profile(name)
    sid = prof["student_id"]
    print("Created student_id:", sid)
    topic = input("Topic to study (optional): ").strip() or None
    session = eng.start_session(sid, topic)
    session_id = session["session_id"]
    print("Started session:", session_id)

    try:
        while True:
            msg = input("You (student) > ").strip()
            if not msg:
                continue
            # send student message
            from datetime import datetime, timezone

            ts = datetime.now(timezone.utc).isoformat()
            eng.post_event(session_id, "student", msg, ts)

            # placeholder tutor response — echo question prompt
            tutor_reply = f"Why do you think '{msg}' is challenging?"
            ts2 = datetime.now(timezone.utc).isoformat()
            eng.post_event(session_id, "tutor", tutor_reply, ts2)
            print("Tutor >", tutor_reply)
    except KeyboardInterrupt:
        print("\nExiting")


if __name__ == "__main__":
    repl()
