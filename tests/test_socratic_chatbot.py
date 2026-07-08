from pathlib import Path
import importlib.util


def test_socratic_rag_has_interactive_chat_method():
    module_path = Path(__file__).resolve().parents[1] / "ai_engine" / "rag" / "socratic_chatbot.py"
    spec = importlib.util.spec_from_file_location("socratic_chatbot", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert hasattr(module.SocraticRAG, "interactive_chat")
