"""
Socratic Chatbot - Guide students to discover answers through questions.
Uses the Socratic method: asking guiding questions to stimulate critical thinking.
"""

import os
import re
import sys
import time

import requests

if __package__ in {None, ""}:
    sys.path.insert(0, os.path.dirname(__file__))
    from interactive_chatbot import InteractiveRAG
else:
    from .interactive_chatbot import InteractiveRAG


class SocraticRAG(InteractiveRAG):
    def __init__(self, ollama_model="phi:latest", student_id="anonymous"):
        """Initialize the Socratic RAG system with Ollama."""
        print("🚀 Starting Socratic RAG Chatbot...\n")
        super().__init__(ollama_model=ollama_model, student_id=student_id)

        self.conversation_history = []
        self.question_depth = 0
        self.max_hints = 3
        self.scaffold_attempts = {}
        print("📊 Socratic method enabled - Learning through questions!\n")

    def _check_ollama(self):
        """Check if Ollama is running."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def _looks_stuck(self, student_answer):
        """Return True when the student appears to be blocked and needs scaffolding."""
        if not student_answer:
            return True

        normalized = re.sub(r"\s+", " ", student_answer.strip().lower())
        stuck_phrases = [
            "i don't know",
            "i do not know",
            "idk",
            "not sure",
            "not sure yet",
            "im stuck",
            "i'm stuck",
            "can't think",
            "can't remember",
            "no idea",
            "help",
        ]
        return any(phrase in normalized for phrase in stuck_phrases)

    def _get_scaffold_attempt(self, question):
        """Track how many times the same question has been scaffolded."""
        key = (question or "").strip().lower()
        current = self.scaffold_attempts.get(key, 0) + 1
        self.scaffold_attempts[key] = current
        return current

    def get_scaffolded_hint(self, question, student_answer, context_docs, attempt=1):
        """Generate a progressive hint sequence for a student who is stuck."""
        if not question:
            return "Think about what you learned in today's lesson. What do you already know that could help you start?"

        if attempt == 1:
            return (
                "Think about what you learned in today's lesson. "
                f"What idea from class seems most relevant to '{question}'?"
            )

        if attempt == 2:
            return (
                "Try to connect the question to a key concept from the lesson. "
                "What important clue or word in the question helps you start?"
            )

        if attempt == 3:
            return (
                "Let's use a clue: think about the main process or material involved. "
                "Which part of the lesson gives you the best starting point?"
            )

        return (
            "You are very close. Use the key idea and one detail from the lesson to narrow it down, "
            "then try your best answer again."
        )

    def generate_socratic_prompt(self, question, context_docs):
        """Create a friendly guiding question for the student."""
        if not question:
            return "What do you already understand about this topic, and what feels unclear?"

        return (
            f"I want to understand your thinking about '{question}'. "
            "In your own words, what do you think the question is asking you to explain?"
        )

    def generate_followup_prompt(self, question, student_answer, context_docs, attempt=2):
        """Generate the next Socratic question when the student needs more support."""
        if not question:
            return self.generate_socratic_prompt(question, context_docs)

        answer_snippet = (student_answer or "").strip().rstrip(".")
        if answer_snippet:
            answer_snippet = answer_snippet[:120]

        if attempt == 2:
            return (
                f"You mentioned '{answer_snippet}' earlier. Can you name one role, property, or use of this topic?"
            )

        if attempt == 3:
            return (
                "Can you give a practical example from daily life that matches your idea?"
            )

        return (
            "What would change if this idea or object were not there?"
        )

    def generate_socratic_feedback(self, question, student_answer, context_docs):
        """Generate friendly feedback and a follow-up question based on the student's answer."""
        if self._looks_stuck(student_answer):
            attempt = self._get_scaffold_attempt(question)
            return self.get_scaffolded_hint(question, student_answer, context_docs, attempt=attempt)

        if not self.ollama_available:
            attempt = self._get_scaffold_attempt(question)
            return self.get_scaffolded_hint(question, student_answer, context_docs, attempt=attempt)

        context = "\n\n".join(context_docs)
        prompt = f"""You are a supportive, conversational Socratic tutor for a Grade 10 student.
The student asked: {question}
The student answered: {student_answer}
Use the context below to decide if the answer is on the right track.
If it is mostly correct, praise the reasoning and ask one follow-up question to deepen the student's understanding.
If it is incomplete or slightly wrong, gently point out the key misconception and ask them to reconsider or clarify.
Do not simply repeat the context. Keep the tone friendly and helpful.

CONTEXT:
{context}

RESPONSE:"""

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": True,
                    "temperature": 0.7,
                },
                timeout=180,
                stream=True,
            )
            if response.status_code == 200:
                answer = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = __import__("json").loads(line)
                            answer += chunk.get("response", "")
                        except Exception:
                            pass
                return answer.strip() or "I couldn't generate feedback right now. Try again."
            attempt = self._get_scaffold_attempt(question)
            return self.get_scaffolded_hint(question, student_answer, context_docs, attempt=attempt)
        except Exception:
            attempt = self._get_scaffold_attempt(question)
            return self.get_scaffolded_hint(question, student_answer, context_docs, attempt=attempt)

    def interactive_chat(self):
        """Run an interactive Socratic tutoring loop."""
        print("\n" + "=" * 75)
        print("🧠 SOCRATIC RAG CHATBOT")
        if self.ollama_available:
            print("(Using Ollama)")
        else:
            print("(Context only mode - Ollama not running)")
        print("=" * 75)
        print("\nCommands:")
        print("  • Type your question and press Enter")
        print("  • Type 'help' for more options")
        print("  • Type 'quit' to exit\n")

        while True:
            try:
                query = input("❓ Your Question: ").strip()

                if not query:
                    continue

                if query.lower() in {"quit", "exit"}:
                    print("\n👋 Goodbye! Thanks for using the Socratic chatbot!")
                    break

                if query.lower() == "help":
                    print("\n💡 HELP:")
                    print("  • Ask any question about the curriculum")
                    print("  • The system will guide you with one reflective question at a time")
                    print("  • Type 'quit' to exit\n")
                    continue

                print("\n🔍 Searching curriculum...\n")
                start_time = time.time()
                context_docs, _ = self.search_and_display(query, top_k=3)

                if not context_docs:
                    print("\n⚠️  No relevant context was found. Try a different question.\n")
                    continue

                self.question_depth += 1
                current_query = query
                current_turn = 1

                while True:
                    if current_turn == 1:
                        prompt = self.generate_socratic_prompt(current_query, context_docs)
                    else:
                        prompt = self.generate_followup_prompt(
                            current_query,
                            student_response,
                            context_docs,
                            attempt=current_turn,
                        )

                    print("\n" + "=" * 75)
                    print(f"🧠 SOCRATIC QUESTION (turn {current_turn}):\n")
                    print(prompt)
                    print("\n" + "=" * 75 + "\n")

                    student_response = input("🧑 Your answer (type 'next' only when you want a new topic): ").strip()
                    if not student_response:
                        print("\n⚠️ Please type your answer so I can help you further.\n")
                        continue

                    if student_response.lower() in {"quit", "exit"}:
                        print("\n👋 Goodbye! Thanks for using the Socratic chatbot!")
                        return

                    if student_response.lower() in {"next", "skip", "new topic"}:
                        print("\n➡️ Moving to the next question.\n")
                        break

                    feedback = self.generate_socratic_feedback(current_query, student_response, context_docs)
                    print("\n" + "=" * 75)
                    print("💬 Tutor Feedback:\n")
                    print(feedback)
                    print("\n" + "=" * 75 + "\n")

                    self.conversation_history.append(
                        {
                            "question": current_query,
                            "answer": student_response,
                            "feedback": feedback,
                            "turn": current_turn,
                        }
                    )
                    self.log_interaction(current_query, feedback, len(context_docs), time.time() - start_time)

                    current_turn += 1

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as exc:
                print(f"\n❌ Error: {exc}\n")


if __name__ == "__main__":
    import sys

    model_name = sys.argv[1] if len(sys.argv) > 1 else "phi:latest"
    student_id = sys.argv[2] if len(sys.argv) > 2 else "anonymous"

    try:
        rag = SocraticRAG(ollama_model=model_name, student_id=student_id)
        rag.interactive_chat()
    except Exception as exc:
        print(f"❌ Error: {exc}")
        print("💡 Make sure you've run: python ai_engine/rag/interactive_chatbot.py")
        print("💡 And start Ollama with: ollama serve")
