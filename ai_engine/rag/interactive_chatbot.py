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
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
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