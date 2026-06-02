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

    # (keep the rest of methods unchanged - truncated here for brevity in patch)
