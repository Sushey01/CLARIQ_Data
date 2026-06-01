"""
Socratic Chatbot - Guide students to discover answers through questions
Uses the Socratic method: questioning to stimulate critical thinking
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import os
import requests
from datetime import datetime
import time
import json

class SocraticRAG:
    def __init__(self, ollama_model="phi:latest", student_id="anonymous"):
        """Initialize the Socratic RAG system with Ollama"""
        print("🚀 Starting Socratic RAG Chatbot...\n")
        
        # Ollama configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = ollama_model
        self.ollama_available = self._check_ollama()
        
        # Student tracking
        self.student_id = student_id
        self.interaction_log_path = os.path.join(os.path.dirname(__file__), '../../data/processed/student_interactions.csv')
        self.interaction_log_path = os.path.abspath(self.interaction_log_path)
        
        # Track conversation state
        self.conversation_history = []
        self.question_depth = 0  # Track how many hints given
        self.max_hints = 3  # Max guiding questions before showing answer
        
        # Load knowledge base
        kb_path = os.path.join(os.path.dirname(__file__), '../../data/processed/rag_knowledge_base.csv')
        kb_path = os.path.abspath(kb_path)
        
        self.kb = pd.read_csv(kb_path)
        print(f"✅ Loaded {len(self.kb)} documents from knowledge base")
        
        # Load embedding model
        print("📚 Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded")
        
        # Connect to Chroma database
        db_path = os.path.join(os.path.dirname(__file__), '../../db/chroma_db')
        db_path = os.path.abspath(db_path)
        
        print("💾 Connecting to vector database...")
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.client.get_collection(name="curriculum")
        
        print(f"✅ Connected to {self.collection.count()} indexed documents")
        if self.ollama_available:
            print(f"✅ Ollama is running (model: {self.ollama_model})")
        else:
            print("⚠️  Ollama not available - start it with: ollama serve")
        
        print("📊 Socratic method enabled - Learning through questions!\n")
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def search_and_display(self, query, top_k=5, similarity_threshold=0.25):
        """Search for relevant documents"""
        query_embedding = self.model.encode(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["documents"][0]:
            return None, []
        
        # Filter by similarity
        valid_results = []
        for i in range(len(results["documents"][0])):
            similarity = 1 - results["distances"][0][i]
            if similarity >= similarity_threshold:
                valid_results.append(i)
        
        # Check if match is too poor (< 40% similarity)
        if valid_results:
            best_similarity = 1 - results["distances"][0][valid_results[0]]
            if best_similarity < 0.40:
                print("\n⚠️  Warning: Low relevance match detected (below 40% similarity)")
                print("    This topic might not be well-covered in our curriculum.")
                print("    The answer may be inaccurate.\n")
        
        if not valid_results:
            valid_results = list(range(min(3, len(results["documents"][0]))))
        
        context_docs = []
        for i in valid_results:
            doc = results["documents"][0][i]
            context_docs.append(doc)
        
        return context_docs, results
    
    def generate_socratic_questions(self, original_question, context_docs, hint_level=1):
        """
        Generate guiding questions using fact-based Socratic method
        Start with interesting facts, then guide student through discovery
        hint_level: 1=fact, 2=what do you think, 3=explain, 4=full answer
        """
        if not self.ollama_available:
            return None
        
        context = "\n\n".join([doc[:200] for doc in context_docs])
        
        prompts = {
            1: f"""Start with an interesting FACT or observation related to this question.
Question: {original_question}
Context: {context}

Generate ONE interesting fact about this topic (1-2 sentences max). 
Example for photosynthesis: "Did you know that plants are green because of chlorophyll?"
Answer with just the fact, starting with 'Did you know that...' or 'Interesting fact:'""",

            2: f"""Ask what the student thinks this fact means or what happens because of it.
Question: {original_question}
Original fact context: {context}

Generate ONE simple follow-up question (1-2 sentences max) like "What do you think this means?"
Keep it simple and direct.""",

            3: f"""Guide them to explain or connect the idea.
Question: {original_question}
Context: {context}

Generate ONE explanation or connection statement (1-2 sentences max).
Example: "That's because the chlorophyll captures light energy from the sun."
Make it educational but simple.""",

            4: f"""Provide a clear, practical explanation.
Question: {original_question}
Context: {context}

Give a concise, understandable explanation (3-5 sentences max).
Make it relatable and practical for a bachelor student."""
        }
        
        if hint_level > 4:
            hint_level = 4
        
        prompt = prompts[hint_level]
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": True,
                    "temperature": 0.6
                },
                timeout=180,
                stream=True
            )
            
            if response.status_code == 200:
                text = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            text += chunk.get("response", "")
                        except:
                            pass
                
                text = text.strip()
                
                # Trim to reasonable length
                max_lengths = {1: 180, 2: 150, 3: 150, 4: 300}
                max_len = max_lengths.get(hint_level, 200)
                
                if len(text) > max_len:
                    text = text[:max_len].rsplit(' ', 1)[0] + "..."
                
                return text
        except Exception as e:
            print(f"Error generating response: {e}")
        
        return None
    
    def socratic_interaction(self, question):
        """
        Handle a single Socratic interaction using fact-based approach
        Returns: tuple (response_text, should_continue)
        """
        self.conversation_history.append({"role": "student", "question": question})
        
        print("\n🔍 Searching for relevant information...")
        context_docs, _ = self.search_and_display(question)
        
        if not context_docs:
            print("❌ No relevant information found in curriculum.")
            return None, False
        
        self.question_depth += 1
        
        # Guide through facts and discovery
        if self.question_depth == 1:
            # Start with interesting fact
            print(f"\n✨ Interesting Fact (Step 1/{self.max_hints}):\n")
            response = self.generate_socratic_questions(question, context_docs, hint_level=1)
            
            if response:
                self.conversation_history.append({"role": "tutor", "response": response})
                return response, True
        
        elif self.question_depth == 2:
            # Ask what they think
            print(f"\n🤔 What Do You Think? (Step 2/{self.max_hints}):\n")
            response = self.generate_socratic_questions(question, context_docs, hint_level=2)
            
            if response:
                self.conversation_history.append({"role": "tutor", "response": response})
                return response, True
        
        elif self.question_depth == 3:
            # Explain the connection
            print(f"\n💡 Here's Why (Step 3/{self.max_hints}):\n")
            response = self.generate_socratic_questions(question, context_docs, hint_level=3)
            
            if response:
                self.conversation_history.append({"role": "tutor", "response": response})
                return response, True
        
        else:
            # Full explanation if they want more
            print("\n📚 Full Explanation:\n")
            response = self.generate_socratic_questions(question, context_docs, hint_level=4)
            
            if response:
                self.conversation_history.append({"role": "tutor", "answer": response})
                self.question_depth = 0  # Reset for next question
                return response, False
        
        return None, False
    
    def show_context_snippets(self, question):
        """Show relevant snippets without revealing full answer"""
        context_docs, results = self.search_and_display(question)
        
        if not context_docs:
            print("No relevant documents found.")
            return
        
        print("\n📖 Relevant Context Snippets (Read carefully!):\n")
        print("=" * 75)
        
        for idx, doc in enumerate(context_docs[:3], 1):  # Show top 3
            print(f"\n[Snippet {idx}]")
            print("-" * 75)
            print(doc[:400] + "...")
            print()
    
    def log_interaction(self, question, response, depth_used):
        """Log Socratic interaction to CSV"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            interaction_id = f"{self.student_id}_SOC_{int(time.time() * 1000) % 100000}"
            
            interaction_data = {
                'interaction_id': interaction_id,
                'student_id': self.student_id,
                'timestamp': timestamp,
                'question': question,
                'socratic_depth': depth_used,
                'response': response[:500] if response else "",
                'method': 'socratic',
                'model_used': self.ollama_model
            }
            
            df = pd.DataFrame([interaction_data])
            if os.path.exists(self.interaction_log_path):
                df.to_csv(self.interaction_log_path, mode='a', header=False, index=False)
            else:
                df.to_csv(self.interaction_log_path, mode='w', header=True, index=False)
            
            print("\n✅ Interaction logged")
            
        except Exception as e:
            print(f"⚠️  Could not log interaction: {e}")
    
    def interactive_socratic_chat(self):
        """Interactive Socratic chat mode"""
        print("\n" + "="*75)
        print("🧠 SOCRATIC LEARNING CHATBOT - Fact-Based Discovery")
        print("Learn by exploring interesting facts and making connections")
        print("="*75)
        print("\nHow it works:")
        print("  1️⃣  Ask a question (e.g., 'What is photosynthesis?')")
        print("  2️⃣  See an interesting fact about the topic")
        print("  3️⃣  Think and explore through guided steps")
        print("  4️⃣  Discover the answer yourself!")
        print("\nCommands: 'hint' | 'context' | 'answer' | 'new' | 'quit'\n")
        
        current_question = None
        context_docs = None
        
        while True:
            try:
                user_input = input("🧑‍🎓 ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    print("\n👋 Great learning session! Keep exploring!\n")
                    break
                
                if user_input.lower() == 'help':
                    print("""
🎯 COMMANDS:
  • 'hint' - Continue to next step
  • 'context' - Read relevant material
  • 'answer' - Get full explanation (use when ready!)
  • 'new' - Start a new question
  • 'quit' - Exit
                    """)
                    continue
                
                if user_input.lower() == 'new':
                    current_question = None
                    context_docs = None
                    self.question_depth = 0
                    print("🔄 Ready for a new question!\n")
                    continue
                
                # Handle commands for active question
                if current_question:
                    if user_input.lower() == 'hint':
                        response, _ = self.socratic_interaction(current_question)
                        if response:
                            print(f"\n{response}\n")
                        print("👉 Type: 'hint' for next step, 'context' to read, 'answer' for full explanation\n")
                        continue
                    
                    elif user_input.lower() == 'context':
                        self.show_context_snippets(current_question)
                        print("👉 Type: 'hint' for next step, 'answer' for full explanation\n")
                        continue
                    
                    elif user_input.lower() == 'answer':
                        context_docs, _ = self.search_and_display(current_question)
                        response = self.generate_socratic_questions(
                            current_question, 
                            context_docs if context_docs else ["No context available"], 
                            hint_level=4
                        )
                        if response:
                            print(f"\n📚 FULL EXPLANATION:\n{response}\n")
                            self.log_interaction(current_question, response, self.question_depth)
                        current_question = None
                        context_docs = None
                        self.question_depth = 0
                        print("🔄 Ask another question or type 'quit'\n")
                        continue
                    
                    else:
                        # User gave any other response - keep them engaged
                        print("\n💡 Here are your options:")
                        print("   • Type 'hint' - Continue exploring")
                        print("   • Type 'context' - Read background material")
                        print("   • Type 'answer' - Get full explanation")
                        print("   • Type 'new' - Ask a different question\n")
                        continue
                
                # New question - start the discovery process
                current_question = user_input
                self.question_depth = 0
                
                # Search for context
                print("\n🔍 Searching curriculum...")
                context_docs, results = self.search_and_display(current_question)
                
                if not context_docs:
                    print("\n❌ Topic not found in curriculum!")
                    print("   Your curriculum covers: Light, Optics, Human Eye, Vision")
                    print("   Try asking about these topics instead.\n")
                    current_question = None
                    context_docs = None
                    continue
                
                # Check similarity score
                if results["distances"][0]:
                    best_similarity = 1 - results["distances"][0][0]
                    if best_similarity < 0.35:
                        print("\n⚠️  This topic might not be in our curriculum!")
                        print(f"    Best match similarity: {best_similarity*100:.0f}%")
                        print("    The answer may be inaccurate or off-topic.\n")
                        print("    Continue? (type 'yes' to proceed, 'new' to try another question)\n")
                        confirm = input("🧑‍🎓 ").strip().lower()
                        if confirm != 'yes':
                            current_question = None
                            context_docs = None
                            continue
                
                # Generate first fact
                print("\n✨ Here's an interesting fact to start:\n")
                response, _ = self.socratic_interaction(current_question)
                
                if response:
                    print(f"{response}\n")
                    print("👉 Type: 'hint' to continue, 'context' to read more, 'answer' for full explanation\n")
                else:
                    print("⚠️  Could not generate content. Try asking another way.\n")
                    current_question = None
                    context_docs = None
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
                continue


if __name__ == "__main__":
    socratic_bot = SocraticRAG(student_id="student_001")
    socratic_bot.interactive_socratic_chat()
