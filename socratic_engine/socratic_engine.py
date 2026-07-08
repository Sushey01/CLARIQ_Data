import os
import json
import urllib.request
import urllib.error
from typing import Optional


class SocraticEngine:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        # Normalize base URL by removing any trailing slash so paths like
        # "/sessions/start" concatenate correctly.
        self.base = base_url.rstrip("/")

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            raise RuntimeError(e.read().decode())

    def _post_no_body(self, path: str) -> None:
        """POST with no response body (e.g. 204 endpoints)."""
        url = f"{self.base}{path}"
        req = urllib.request.Request(url, data=b"", headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                pass
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

    def chat(self, session_id: str, message: str) -> dict:
        """Send a student message and get a Socratic tutor response via RAG + Ollama."""
        return self._post(f"/sessions/{session_id}/chat", {"message": message})

    def reset_hints(self, session_id: str) -> None:
        """Reset the hint depth for the session (e.g. when changing topic)."""
        self._post_no_body(f"/sessions/{session_id}/chat/reset")

    def ingest_url(self, url: str, clear_existing: bool = False) -> dict:
        """Start background ingestion of a PDF url."""
        return self._post("/pipeline/ingest-url", {"url": url, "clear_existing": clear_existing})

    def get_pipeline_status(self) -> dict:
        """Check pipeline status."""
        url = f"{self.base}/pipeline/status"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            raise RuntimeError(e.read().decode())


def repl(base_url: str = "http://127.0.0.1:8000"):
    eng = SocraticEngine(base_url)
    print("\n" + "=" * 60)
    print("  🎓 CLARIQ — Socratic Tutor CLI")
    print("=" * 60)
    print(f"Backend: {base_url}")
    print("Commands: /topic <new topic>  /reset  /ingest <url>  /status  /quit\n")

    name = input("Student name: ").strip()
    # Allow empty grade but fallback to BACKEND_DEFAULT_GRADE env or '10'
    grade = input("Grade (e.g., 10, 11) — press Enter to use default: ").strip()
    if not grade:
        grade = os.environ.get("BACKEND_DEFAULT_GRADE", "10")
        print(f"Using default grade: {grade}")

    try:
        prof = eng.create_profile(name, grade)
    except Exception as e:
        print(f"Failed to create profile: {e}")
        return
    sid = prof["student_id"]
    print(f"✅ Created student: {name} (ID: {sid})")

    topic = input("Topic to study (optional): ").strip() or None
    session = eng.start_session(sid, topic)
    session_id = session["session_id"]
    print(f"✅ Started session: {session_id}")
    if topic:
        print(f"📚 Topic: {topic}")
    print("\n" + "-" * 60)
    print("Ask a question about your curriculum!")
    print("-" * 60 + "\n")

    try:
        while True:
            msg = input("You > ").strip()
            if not msg:
                continue

            # Handle CLI commands
            if msg.lower() == "/quit":
                print("👋 Goodbye! Happy learning!")
                break
            if msg.lower() == "/reset":
                eng.reset_hints(session_id)
                print("🔄 Hint depth reset.\n")
                continue
            if msg.lower().startswith("/topic "):
                new_topic = msg[7:].strip()
                if new_topic:
                    topic = new_topic
                    session = eng.start_session(sid, topic)
                    session_id = session["session_id"]
                    print(f"📚 Switched to topic: {topic}")
                    print(f"✅ New session: {session_id}\n")
                continue
            if msg.lower().startswith("/ingest "):
                url = msg[8:].strip()
                if url:
                    print(f"🚀 Starting background ingestion for {url}")
                    try:
                        res = eng.ingest_url(url, clear_existing=True)
                        print(f"✅ {res.get('message', 'Started')}")
                        print("Type /status to check progress.")
                    except Exception as e:
                        print(f"❌ Failed to start ingestion: {e}")
                continue
            if msg.lower() == "/status":
                try:
                    status = eng.get_pipeline_status()
                    is_running = status.get("is_running", False)
                    print("\n📊 Pipeline Status:")
                    print(f"   Running: {'Yes ⏳' if is_running else 'No ✅'}")
                    if status.get("last_url"):
                        print(f"   Last URL: {status['last_url']}")
                    if status.get("last_error"):
                        print(f"   Last Error: {status['last_error']}")
                    print()
                except Exception as e:
                    print(f"❌ Failed to get status: {e}")
                continue

            # Send message and get Socratic response
            print("⏳ Thinking...")
            try:
                response = eng.chat(session_id, msg)
                reply = response.get("reply", "(no response)")
                hint_depth = response.get("hint_depth", 0)
                sources = response.get("sources", [])
                fallback = response.get("fallback", False)

                print(f"\n🎓 Tutor > {reply}")

                # Show metadata
                if not fallback and sources:
                    src_info = ", ".join(
                        f"{s.get('source_pdf', '?')} p.{s.get('page', '?')}"
                        for s in sources[:2]
                    )
                    print(f"   📖 Sources: {src_info}")
                    print(f"   💡 Hint depth: {hint_depth}/3")
                print()

            except Exception as e:
                print(f"❌ Error: {e}\n")

    except KeyboardInterrupt:
        print("\n👋 Goodbye! Happy learning!")


if __name__ == "__main__":
    repl()
