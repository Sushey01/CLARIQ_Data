"""
Interactive RAG Chatbot - Ask questions and get answers!
Uses local Ollama for LLM inference
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import os
import requests
from datetime import datetime
import time

class InteractiveRAG:
    def __init__(self, ollama_model="phi:latest", student_id="anonymous"):
        """Initialize the RAG system with Ollama"""
        print("🚀 Starting Interactive RAG Chatbot...\n")
        
        # Ollama configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = ollama_model
        self.ollama_available = self._check_ollama()
        
        # Student tracking for chat history
        self.student_id = student_id
        self.interaction_log_path = os.path.join(os.path.dirname(__file__), '../../data/processed/student_interactions.csv')
        self.interaction_log_path = os.path.abspath(self.interaction_log_path)
        
        # Load knowledge base
        kb_path = os.path.join(os.path.dirname(__file__), '../../data/processed/rag_knowledge_base.csv')
        kb_path = os.path.abspath(kb_path)
        
        self.kb = pd.read_csv(kb_path)
        print(f"✅ Loaded {len(self.kb)} documents from knowledge base")
        
        # Load embedding model
        print("📚 Loading embedding model (this may take 1-2 minutes on first run)...")
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
        
        print("📊 Chat history will be saved to: student_interactions.csv\n")
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_answer(self, question, context_docs):
        """Generate answer using Ollama with retrieved context"""
        if not self.ollama_available:
            print("⚠️  Ollama not running. Start it with: ollama serve")
            return None
        
        # Construct prompt with context
        context = "\n\n".join([doc for doc in context_docs])
        
        prompt = f"""You are a helpful tutor assistant. Answer the following question based ONLY on the provided context.
If the context doesn't contain enough information, say so clearly.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
        
        try:
            print("\n🤖 Generating answer from Ollama...")
            print("⏳ Please wait (may take 30-60 seconds on low-memory systems)...\n")
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": True,
                    "temperature": 0.7
                },
                timeout=180,
                stream=True
            )
            
            if response.status_code == 200:
                answer = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = __import__('json').loads(line)
                            answer += chunk.get("response", "")
                        except:
                            pass
                answer = answer.strip()
                if answer:
                    return answer
                else:
                    print("❌ No response from Ollama")
                    return None
            else:
                print(f"❌ Ollama error: {response.status_code}")
                return None
            
        except Exception as e:
            print(f"❌ Error connecting to Ollama: {e}")
            return None
    
    
    def search_and_display(self, query, top_k=5, similarity_threshold=0.25):
        """Search for relevant documents and display results"""
        
        # Generate embedding
        query_embedding = self.model.encode(query)
        
        # Search (get more results to filter)
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["documents"][0]:
            print("❌ No documents found in curriculum.\n")
            print("💡 Tip: Try different keywords or simpler questions.\n")
            return None, []
        
        # Filter by similarity threshold
        valid_results = []
        for i in range(len(results["documents"][0])):
            similarity = 1 - results["distances"][0][i]
            if similarity >= similarity_threshold:
                valid_results.append(i)
        
        if not valid_results:
            print(f"⚠️  No highly relevant documents found (threshold: {similarity_threshold*100:.0f}%).\n")
            print("📚 Showing available matches:\n")
            valid_results = list(range(min(3, len(results["documents"][0]))))
        
        print(f"\n📚 Found {len(valid_results)} relevant sections:\n")
        print("=" * 75)
        
        context_docs = []
        for idx, i in enumerate(valid_results, 1):
            similarity = round(1 - results["distances"][0][i], 3)
            doc = results["documents"][0][i]
            metadata = results["metadatas"][0][i]
            context_docs.append(doc)
            
            print(f"\n[Result {idx}] Similarity: {similarity*100:.1f}% 🎯")
            print(f"Source: {metadata.get('source_pdf', 'Unknown')} (Page {metadata.get('page', '?')})")
            print(f"Word Count: {metadata.get('word_count', '?')}")
            print("-" * 75)
            print(f"{doc[:500]}...")
            print()
        
        print("=" * 75)
        return context_docs, results
    
    def log_interaction(self, question, answer, num_docs_found, response_time):
        """Log student interaction to CSV for tracking and analysis"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            interaction_id = f"{self.student_id}_INT_{int(time.time() * 1000) % 100000}"
            
            # Prepare data
            interaction_data = {
                'interaction_id': interaction_id,
                'student_id': self.student_id,
                'timestamp': timestamp,
                'question': question,
                'num_documents_found': num_docs_found,
                'answer': answer[:500] if answer else "No answer generated",  # First 500 chars
                'response_time_seconds': round(response_time, 2),
                'model_used': self.ollama_model,
                'success': 'yes' if answer else 'no'
            }
            
            # Append to CSV
            df = pd.DataFrame([interaction_data])
            if os.path.exists(self.interaction_log_path):
                df.to_csv(self.interaction_log_path, mode='a', header=False, index=False)
            else:
                df.to_csv(self.interaction_log_path, mode='w', header=True, index=False)
            
            print("✅ Logged to student_interactions.csv")
            
        except Exception as e:
            print(f"⚠️  Could not log interaction: {e}")
    
    def interactive_chat(self):
        """Interactive chat mode"""
        print("\n" + "="*75)
        print("🤖 INTERACTIVE RAG CHATBOT")
        if self.ollama_available:
            print("(Using Ollama)")
        else:
            print("(Context only mode - Ollama not running)")
        print("="*75)
        print("\nCommands:")
        print("  • Type your question and press Enter")
        print("  • Type 'help' for more options")
        print("  • Type 'quit' to exit\n")
        
        while True:
            try:
                query = input("❓ Your Question: ").strip()
                
                if not query:
                    continue
                
                if query.lower() == 'quit':
                    print("\n👋 Goodbye! Thanks for using the RAG Chatbot!")
                    break
                
                if query.lower() == 'help':
                    print("\n💡 HELP:")
                    print("  • Ask any question about the curriculum")
                    print("  • System will search and retrieve relevant content")
                    print("  • Results show similarity score (0-100%)")
                    print("  • Low scores mean topic may not be in curriculum")
                    if self.ollama_available:
                        print("  • Ollama will generate an answer based on context")
                    else:
                        print("  • Ollama not running - showing context only")
                    print("  • Type 'quit' to exit\n")
                    continue
                
                print("\n🔍 Searching curriculum...\n")
                start_time = time.time()
                context_docs, _ = self.search_and_display(query, top_k=3)
                
                # Generate answer using Ollama
                if context_docs:
                    answer = self.generate_answer(query, context_docs)
                    response_time = time.time() - start_time
                    if answer:
                        print("\n" + "="*75)
                        print("✨ ANSWER FROM OLLAMA:\n")
                        print(answer)
                        print("\n" + "="*75 + "\n")
                        # Log the interaction
                        self.log_interaction(query, answer, len(context_docs), response_time)
                    else:
                        print("\n⚠️  Could not generate answer. Check Ollama status.\n")
                        # Log failed attempt
                        self.log_interaction(query, None, len(context_docs), response_time)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    import sys
    
    # Get model name and student ID from command line args
    model_name = sys.argv[1] if len(sys.argv) > 1 else "mistral"
    student_id = sys.argv[2] if len(sys.argv) > 2 else "anonymous"
    
    try:
        rag = InteractiveRAG(ollama_model=model_name, student_id=student_id)
        rag.interactive_chat()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you've run: python src/embeddings/build_vector_db.py")
        print("💡 And start Ollama with: ollama serve")
