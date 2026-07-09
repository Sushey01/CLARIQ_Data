"""
Chat Service — Connects RAG retrieval (ChromaDB) with Ollama LLM
to generate Socratic tutoring responses.

Flow:
  student message → search ChromaDB → build Socratic prompt → Ollama → response
"""

import json
import sys
import os
import random
import requests
from pathlib import Path
from typing import Any, Optional

# Add project root to path so we can import ai_engine modules
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Ollama configuration
# ---------------------------------------------------------------------------
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "orca-mini:latest")
OLLAMA_FALLBACK_MODELS = [
    model.strip()
    for model in os.environ.get("OLLAMA_FALLBACK_MODELS", "phi:latest").split(",")
    if model.strip()
]

# ---------------------------------------------------------------------------
# In-memory hint-depth tracker  (session_id → depth int)
# Resets when the topic/question changes substantially.
# ---------------------------------------------------------------------------
_hint_depth: dict[str, int] = {}
MAX_HINTS = 3

# ---------------------------------------------------------------------------
# Lazy-loaded search engine singleton
# ---------------------------------------------------------------------------
_search_engine: Optional[Any] = None


def _get_search_engine() -> Any:
    """Lazy-load the search engine so model loading only happens on first call."""
    global _search_engine
    if _search_engine is None:
        from ai_engine.embeddings.search_vector_db import CurriculumSearchEngine

        _search_engine = CurriculumSearchEngine()
    return _search_engine


def _check_ollama() -> bool:
    """Return True if Ollama is reachable."""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def _get_installed_ollama_models() -> list[str]:
    """Return the list of locally installed Ollama model tags."""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=3)
        if resp.status_code != 200:
            return []
        data = resp.json()
        models = []
        for item in data.get("models", []):
            name = item.get("name")
            if name:
                models.append(name)
        return models
    except Exception:
        return []


def _select_available_model(preferred_models: list[str]) -> str:
    """Pick the first preferred model that exists locally, or the first preferred entry."""
    installed = set(_get_installed_ollama_models())
    for model_name in preferred_models:
        if model_name in installed:
            return model_name
    return preferred_models[0] if preferred_models else OLLAMA_MODEL


def _normalize_text(text: str) -> str:
    return " ".join((text or "").lower().split())


def _is_confused_message(message: str) -> bool:
    normalized = _normalize_text(message)
    if not normalized:
        return False

    confused_phrases = [
        "i don't know",
        "i do not know",
        "idk",
        "not sure",
        "still confused",
        "confused",
        "no idea",
        "help me",
        "i am stuck",
        "i'm stuck",
    ]
    return any(phrase in normalized for phrase in confused_phrases)


def _is_full_answer_request(message: str) -> bool:
    normalized = _normalize_text(message)
    if not normalized:
        return False

    triggers = [
        "make me understand",
        "full explanation",
        "explain fully",
        "fully explain",
        "give me the answer",
        "tell me directly",
        "answer directly",
        "in your words",
        "now explain",
    ]
    return any(trigger in normalized for trigger in triggers)


def _split_previous_exchange(events: list[dict]) -> tuple[str, str]:
    """Return the most recent student answer and tutor reply if available."""
    last_student = ""
    last_tutor = ""
    for event in reversed(events):
        role = event.get("role")
        content = event.get("content", "")
        if role == "student" and not last_student:
            last_student = content
        elif role == "tutor" and not last_tutor:
            last_tutor = content
        if last_student and last_tutor:
            break
    return last_student, last_tutor


def _select_response_mode(session_id: str, message: str, events: list[dict]) -> str:
    """Choose the tutoring mode for this turn.

    Modes:
    - socratic: start with a simple guiding question
    - clarify: one stronger hint when the student seems unsure
    - explain: direct explanation after repeated confusion or explicit request
    """
    depth = _hint_depth.get(session_id, 0)
    if _is_full_answer_request(message):
        return "explain"
    if depth >= 2:
        return "explain"

    if _is_confused_message(message):
        if depth >= 1:
            return "explain"
        return "clarify"

    last_student, _ = _split_previous_exchange(events)
    if last_student and _normalize_text(last_student) == _normalize_text(message):
        return "clarify" if depth == 0 else "explain"

    return "socratic"


# ---------------------------------------------------------------------------
# Socratic prompt templates
# ---------------------------------------------------------------------------

SOCRATIC_SYSTEM_PROMPT = """You are a Socratic tutor helping students learn from their curriculum.
Your teaching style follows the Socratic method:

RULES:
1. NEVER give the answer directly on the first attempt.
2. Ask guiding questions that lead the student to discover the answer themselves.
3. Use the provided CONTEXT from the curriculum to ground your questions.
4. Be encouraging and patient.
5. If the student is clearly stuck (hint_depth >= {max_hints}), gently reveal the key concept.
6. Keep responses concise (2-4 sentences).
7. Reference specific concepts from the CONTEXT when asking questions.

HINT DEPTH: {hint_depth}/{max_hints}
- Depth 0: Ask an open-ended question to probe understanding
- Depth 1: Give a small hint and ask a more focused question
- Depth 2: Provide a stronger hint with a near-answer clue
- Depth 3+: Explain the concept clearly, then ask a follow-up to confirm understanding

EXAMPLES OF GOOD SOCRATIC RESPONSES:
Student: "Why does this phenomenon occur?"
Tutor: "That's a great question! Let's look at the evidence. If we observe X happening, what must be true about Y?"

Student: "Can you explain how this works?"
Tutor: "I love that you're asking! Instead of me just telling you, let's experiment mentally. If you had to explain this to a younger student, what simple analogy would you use?"

Student: "What are the main characteristics?"
Tutor: "You're on the right track. To help you connect the dots, can you remember a similar concept we studied earlier? How might the rules from that concept apply here?"

Student: "Is there a rule that governs this?"
Tutor: "Interesting perspective. Let's test that hypothesis. If your assumption is correct, what other phenomena in the natural world must also be true? Do we observe those?"
"""

PROMPT_TEMPLATE = """{system_prompt}

SOCrATIC EXAMPLES:
{examples}

CONTEXT FROM CURRICULUM:
{context}

CONVERSATION HISTORY:
{history}

STUDENT MESSAGE: {message}

TUTOR RESPONSE:"""


def _build_history_text(events: list[dict]) -> str:
    """Format the last few session events into a readable conversation string."""
    # Keep only the last 6 events to avoid exceeding context window
    recent = events[-6:] if len(events) > 6 else events
    lines = []
    for ev in recent:
        role = ev.get("role", "unknown").capitalize()
        content = ev.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "(no previous conversation)"


def _load_socratic_examples(limit: int = 3) -> str:
    """Load a few examples from the Socratic fine-tuning dataset for prompt steering."""
    dataset_path = PROJECT_ROOT / "socratic_finetuning_data.jsonl"
    if not dataset_path.exists():
        return "(no Socratic dataset examples available)"

    examples: list[str] = []
    try:
        all_examples: list[str] = []
        with dataset_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                student_input = item.get("input", "")
                tutor_output = item.get("output", "")
                if student_input and tutor_output:
                    all_examples.append(f"Student: {student_input}\nTutor: {tutor_output}")

        if not all_examples:
            return "(no Socratic dataset examples available)"

        if len(all_examples) <= limit:
            examples = all_examples
        else:
            examples = random.sample(all_examples, k=limit)
    except Exception:
        return "(no Socratic dataset examples available)"

    return "\n\n".join(examples) if examples else "(no Socratic dataset examples available)"


def _call_ollama(prompt: str) -> tuple[Optional[str], Optional[str]]:
    """Send prompt to Ollama and return the generated text and the model used."""
    preferred_models = [OLLAMA_MODEL, *OLLAMA_FALLBACK_MODELS]
    models_to_try = [_select_available_model(preferred_models)]
    for model_name in preferred_models:
        if model_name not in models_to_try:
            models_to_try.append(model_name)

    for model_name in models_to_try:
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 300,
                    },
                },
                timeout=180,
            )

            if response.status_code == 200:
                data = response.json()
                reply = data.get("response", "").strip()
                if reply:
                    return reply, model_name
        except Exception:
            continue

    return None, None


def generate_socratic_response(
    session_id: str,
    message: str,
    events: list[dict],
    topic: Optional[str] = None,
) -> dict:
    """
    Generate a Socratic tutor response for a student message.

    Args:
        session_id: Current session ID (used for hint depth tracking)
        message: The student's message
        events: List of previous SessionEvent dicts from this session
        topic: Optional session topic for context

    Returns:
        dict with keys: reply, sources, hint_depth, model_used, fallback
    """

    # 1. Track hint depth for this session and decide how much guidance to give.
    depth = _hint_depth.get(session_id, 0)
    mode = _select_response_mode(session_id, message, events)
    global OLLAMA_MODEL

    # 2. Search curriculum for relevant context
    search_engine = _get_search_engine()
    search_query = f"{topic}: {message}" if topic else message
    search_results = search_engine.search(search_query, top_k=3)

    context_text = "\n\n".join(
        f"[Source: {r['source_pdf']}, Page {r['page']}]\n{r['content']}"
        for r in search_results
    )
    sources = [
        {
            "source_pdf": r["source_pdf"],
            "page": r["page"],
            "similarity": r["similarity_score"],
        }
        for r in search_results
    ]

    # 3. Build the Socratic prompt
    if mode == "socratic":
        response_style = (
            "Start with one simple Socratic question. "
            "Use one short example from the curriculum, but do not repeat the same example more than once. "
            "Do not explain the full answer yet."
        )
    elif mode == "clarify":
        response_style = (
            "Give one clearer hint and one concrete example. "
            "If the student seems uncertain, move one step closer to the answer instead of asking the same type of question again."
        )
    else:
        response_style = (
            "Give the direct explanation in simple words, then add one short example and one checking question. "
            "Do not keep the student in an endless question loop."
        )

    system_prompt = SOCRATIC_SYSTEM_PROMPT.format(
        hint_depth=depth,
        max_hints=MAX_HINTS,
    ) + f"\n\nCURRENT MODE: {mode.upper()}\nINSTRUCTIONS: {response_style}"
    history_text = _build_history_text(events)

    examples_text = _load_socratic_examples()
    full_prompt = PROMPT_TEMPLATE.format(
        system_prompt=system_prompt,
        examples=examples_text,
        context=context_text if context_text else "(no relevant curriculum content found)",
        history=history_text,
        message=message,
    )

    # 4. Check Ollama and generate
    fallback = False
    reply = ""
    used_model: Optional[str] = None
    if not _check_ollama():
        reply = (
            "I'm having trouble connecting to my language model right now. "
            "Please make sure Ollama is running (`ollama serve`) and try again."
        )
        fallback = True
    else:
        reply, used_model = _call_ollama(full_prompt)
        if not reply:
            reply = (
                "I couldn't generate a response. The model might be loading — "
                "please try again in a moment."
            )
            fallback = True
        else:
            if used_model:
                OLLAMA_MODEL = used_model

    # 5. Increment hint depth only while staying in Socratic/clarify mode.
    if not fallback:
        if mode == "socratic":
            _hint_depth[session_id] = min(depth + 1, MAX_HINTS)
        elif mode == "clarify":
            _hint_depth[session_id] = min(depth + 1, MAX_HINTS)
        else:
            _hint_depth[session_id] = MAX_HINTS

    return {
        "reply": reply,
        "sources": sources,
        "hint_depth": depth,
        "model_used": used_model or OLLAMA_MODEL,
        "fallback": fallback,
        "mode": mode,
    }



def reset_hint_depth(session_id: str) -> None:
    """Reset the hint depth for a session (e.g., when the student asks a new topic)."""
    _hint_depth.pop(session_id, None)
