import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services import chat_service


class _FakeSearchEngine:
    def search(self, query, top_k=3):
        return [
            {
                "source_pdf": "science.pdf",
                "page": 4,
                "similarity_score": 0.9,
                "content": "Force is a push or pull that can change motion.",
            }
        ]


def test_generate_socratic_response_switches_to_explanation_on_confusion(monkeypatch):
    chat_service._hint_depth.clear()

    monkeypatch.setattr(chat_service, "_get_search_engine", lambda: _FakeSearchEngine())
    monkeypatch.setattr(chat_service, "_check_ollama", lambda: True)

    captured_prompts = []

    def fake_call_ollama(prompt):
        captured_prompts.append(prompt)
        return ("Tutor reply", "mock-model")

    monkeypatch.setattr(chat_service, "_call_ollama", fake_call_ollama)

    first = chat_service.generate_socratic_response(
        session_id="sess-1",
        message="what is force?",
        events=[],
        topic="force",
    )
    second = chat_service.generate_socratic_response(
        session_id="sess-1",
        message="i don't know",
        events=[{"role": "student", "content": "what is force?"}],
        topic="force",
    )

    assert first["mode"] == "socratic"
    assert second["mode"] == "explain"
    assert "CURRENT MODE: EXPLAIN" in captured_prompts[-1]
    assert second["reply"] == "Tutor reply"


def test_call_ollama_prefers_installed_model(monkeypatch):
    monkeypatch.setattr(chat_service, "OLLAMA_MODEL", "mistral:latest")
    monkeypatch.setattr(chat_service, "OLLAMA_FALLBACK_MODELS", ["orca-mini:latest", "phi:latest"])
    monkeypatch.setattr(chat_service, "_get_installed_ollama_models", lambda: ["orca-mini:latest", "phi:latest"])

    seen_models = []

    class _FakeResponse:
        status_code = 200

        def json(self):
            return {"response": "ok"}

    def fake_post(url, json, timeout):
        seen_models.append(json["model"])
        return _FakeResponse()

    monkeypatch.setattr(chat_service.requests, "post", fake_post)

    reply, model_used = chat_service._call_ollama("Explain force")

    assert reply == "ok"
    assert model_used == "orca-mini:latest"
    assert seen_models[0] == "orca-mini:latest"