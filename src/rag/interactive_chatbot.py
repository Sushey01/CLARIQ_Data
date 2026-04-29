"""
Interactive RAG Chatbot - Ask questions and get answers!
Uses local Ollama for LLM inference
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path
import os
import requests
import json

class InteractiveRAG:
    def __init__(self, ollama_model="mistral"):
        """Initialize the RAG system with Ollama integration"""
        print("🚀 Starting Interactive RAG Chatbot with Ollama...\n")
        
        # Ollama configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = ollama_model
        self.ollama_available = self._check_ollama()
        
        # Load knowledge base
        kb_path = os.path.join(os.path.dirname(__file__), '../../data/processed/rag_knowledge_base.csv')
        kb_path = os.path.abspath(kb_path)
        
        self.kb = pd.read_csv(kb_path)
        print(f"✅ Loaded {len(self.kb)} documents from knowledge base")
        
        # Load embedding model
        print("📚 Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
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
            print("⚠️  Ollama not available - showing context only\n")
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
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
            print("\n🤖 Generating answer from Ollama...\n")
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                return answer
            else:
                print(f"❌ Ollama error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Ollama request timed out. Try shorter context or check Ollama is running.")
            return None
        except Exception as e:
            print(f"❌ Error calling Ollama: {e}")
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
    
    def interactive_chat(self):
        """Interactive chat mode"""
        print("\n" + "="*75)
        print("🤖 INTERACTIVE RAG CHATBOT with OLLAMA")
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
                    print("  • Ollama will generate an answer based on context")
                    print("  • Type 'quit' to exit\n")
                    continue
                
                print("\n🔍 Searching curriculum...\n")
                context_docs, _ = self.search_and_display(query, top_k=3)
                
                # Generate answer using Ollama
                if context_docs:
                    answer = self.generate_answer(query, context_docs)
                    if answer:
                        print("\n" + "="*75)
                        print("✨ ANSWER FROM OLLAMA:\n")
                        print(answer)
                        print("\n" + "="*75 + "\n")
                    else:
                        print("\n⚠️  Could not generate answer. Check Ollama status.\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    import sys
    
    # Get model name from command line args (default: mistral)
    model_name = sys.argv[1] if len(sys.argv) > 1 else "mistral"
    
    try:
        rag = InteractiveRAG(ollama_model=model_name)
        rag.interactive_chat()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you've run: python src/embeddings/build_vector_db.py")
        print("💡 And start Ollama with: ollama serve")
