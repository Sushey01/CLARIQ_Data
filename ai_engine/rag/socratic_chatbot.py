"""
Socratic Chatbot - Guide students to discover answers through questions.
Uses the Socratic method: asking guiding questions to stimulate critical thinking.
"""

import os
import sys
import time
import re
from datetime import datetime

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
        print("📊 Socratic method enabled - Learning through questions!\n")

    def _check_ollama(self):
        """Check if Ollama is running."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def generate_socratic_prompt(self, question, context_docs):
        """Create a friendly guiding question for the student."""
        if not question:
            return "What do you already understand about this topic, and what feels unclear?"

        # Provide a short topic-aware example hint when possible
        example_hint = self._get_topic_example_hint(question)

        return (
            f"I want to understand your thinking about '{question}'. "
            f"{example_hint} "
            "In your own words, what do you think the question is asking you to explain?"
        )

    def _get_topic_example_hint(self, question):
        """Return a short topic-specific example hint when we can infer the topic."""
        normalized_question = (question or "").lower()

        example_map = [
            ("photosynthesis", "For example, think about a plant using sunlight, water, and air to make food."),
            ("force", "For example, think about pushing a door open or pulling a drawer."),
            ("energy", "For example, think about food giving you energy or a battery lighting a torch."),
            ("motion", "For example, think about a ball rolling or a bicycle moving forward."),
            ("heredity", "For example, think about children sharing features with their parents."),
        ]

        for keyword, hint in example_map:
            if keyword in normalized_question:
                return hint

        return "For example, think of one simple situation from daily life that shows the same idea."

    def get_scaffolded_hint(self, question, student_answer, context_docs, attempt=1):
        """Generate a progressive hint for a stuck student."""
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

    def generate_followup_prompt(self, question, student_answer, context_docs, attempt=2):
        """Create the next Socratic question when more support is needed."""
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

    def _is_answer_sufficient(self, question, student_answer, context_docs):
        """Simple heuristic to decide if the student's answer shows understanding.

        This is intentionally lightweight: keyword checks for common curriculum
        topics and a small overlap heuristic against retrieved context.
        """
        if not student_answer:
            return False

        ans = student_answer.lower()
        q = (question or "").lower()

        keyword_map = {
            "force": ["push", "pull", "force", "apply force"],
            "photosynthesis": ["sunlight", "water", "carbon", "make food", "chlorophyll"],
            "energy": ["energy", "battery", "food", "heat"],
            "motion": ["move", "moving", "speed", "velocity", "accelerat"],
        }

        for topic, keys in keyword_map.items():
            if topic in q:
                for k in keys:
                    if k in ans:
                        return True

        # Fallback: check overlap with context docs
        import re
        ctx = "\n\n".join(context_docs).lower()
        ans_words = set(re.findall(r"\w{3,}", ans))
        ctx_words = set(re.findall(r"\w{3,}", ctx))
        if not ans_words or not ctx_words:
            return False
        overlap = ans_words & ctx_words
        if len(overlap) >= 3:
            return True

        if len(ans_words) >= 6 and len(overlap) >= 2:
            return True

        return False

    def _is_full_answer_request(self, query):
        """Detect whether the user explicitly asked for a full explanation.

        Matches common phrasings like 'explain', 'make me understand', 'fully',
        or 'in your words'. This is intentionally permissive.
        """
        if not query:
            return False
        q = query.lower()
        triggers = [
            "make me understand",
            "make me understand fully",
            "explain fully",
            "fully explain",
            "in your words",
            "explain",
            "full explanation",
            "now explain",
        ]
        return any(t in q for t in triggers)

    def generate_socratic_feedback(self, question, student_answer, context_docs):
        """Generate friendly feedback and a follow-up question based on the student's answer."""
        # If the student's answer already demonstrates understanding,
        # return a short confirmation and stop further scaffolding.
        if self._is_answer_sufficient(question, student_answer, context_docs):
            return "✅ Good explanation — you understand the idea. <TOPIC_COMPLETE>"

        if not self.ollama_available:
            return (
                "I appreciate your answer. Try to explain the main idea in simpler terms, "
                "then ask yourself what part of it you are unsure about."
            )

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
            return f"Ollama error: {response.status_code}"
        except Exception as exc:
            return f"Error generating feedback: {exc}"

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

                # If the student explicitly asked for a full explanation, return the answer.
                if self._is_full_answer_request(query):
                    answer = self.generate_answer(query, context_docs)
                    response_time = time.time() - start_time
                    if answer:
                        print("\n" + "=" * 75)
                        print("✨ FULL EXPLANATION:\n")
                        print(answer)
                        print("\n" + "=" * 75 + "\n")
                        self.log_interaction(query, answer, len(context_docs), response_time)
                    else:
                        print("\n⚠️  Could not generate a full explanation right now.\n")
                    continue

                self.question_depth += 1
                prompt = self.generate_socratic_prompt(query, context_docs)
                print("\n" + "=" * 75)
                print("🧠 SOCRATIC QUESTION:\n")
                print(prompt)
                print("\n" + "=" * 75 + "\n")

                student_response = input("🧑 Your answer: ").strip()
                if not student_response:
                    print("\n⚠️ Please type your answer so I can help you further.\n")
                    continue

                feedback = self.generate_socratic_feedback(query, student_response, context_docs)
                # Handle topic-complete sentinel
                completed = False
                if "<TOPIC_COMPLETE>" in feedback:
                    completed = True
                    feedback = feedback.replace("<TOPIC_COMPLETE>", "").strip()

                print("\n" + "=" * 75)
                print("💬 Tutor Feedback:\n")
                print(feedback)
                if completed:
                    print("\n➡️ Topic complete — moving to the next question.\n")
                print("\n" + "=" * 75 + "\n")

                self.log_interaction(query, feedback, len(context_docs), time.time() - start_time)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as exc:
                print(f"\n❌ Error: {exc}\n")


if __name__ == "__main__":
    import sys

    model_name = sys.argv[1] if len(sys.argv) > 1 else "mistral"
    student_id = sys.argv[2] if len(sys.argv) > 2 else "anonymous"

    try:
        rag = SocraticRAG(ollama_model=model_name, student_id=student_id)
        rag.interactive_chat()
    except Exception as exc:
        print(f"❌ Error: {exc}")
        print("💡 Make sure you've run: python ai_engine/rag/interactive_chatbot.py")
        print("💡 And start Ollama with: ollama serve")
