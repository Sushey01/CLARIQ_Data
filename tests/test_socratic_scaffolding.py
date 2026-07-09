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

def test_topic_prompt_uses_a_topic_specific_example():
    rag = SocraticRAG.__new__(SocraticRAG)

    prompt = rag.generate_socratic_prompt("photosynthesis", ["Plants make food using sunlight."])

    assert "plant using sunlight, water, and air to make food" in prompt
    assert "photosynthesis" in prompt

def test_generate_feedback_short_circuits_on_sufficient_answer():
    rag = SocraticRAG.__new__(SocraticRAG)
    rag.ollama_available = True

    feedback = rag.generate_socratic_feedback(
        "what is force?",
        "It's a push or a pull that changes motion",
        ["Force is a push or pull on an object that can change its motion."]
    )

    assert "TOPIC_COMPLETE" in feedback or feedback.startswith("✅ Good explanation")


def test_is_full_answer_request_detector():
    rag = SocraticRAG.__new__(SocraticRAG)

    assert rag._is_full_answer_request("now make me understand fully in your words")
    assert rag._is_full_answer_request("please explain force")
    assert rag._is_full_answer_request("give me a full explanation")
    assert not rag._is_full_answer_request("")
