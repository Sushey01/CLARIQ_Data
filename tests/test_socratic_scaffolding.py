import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engine.rag.socratic_chatbot import SocraticRAG


def test_stuck_answers_use_progressive_scaffolding():
    rag = SocraticRAG.__new__(SocraticRAG)
    rag.ollama_available = False

    first_hint = rag.get_scaffolded_hint("What do plants need to make food?", "I don't know", ["plant"], attempt=1)
    second_hint = rag.get_scaffolded_hint("What do plants need to make food?", "I don't know", ["plant"], attempt=2)

    assert "Think about what you learned" in first_hint
    assert "Try to connect" in second_hint or "Let's use a clue" in second_hint
