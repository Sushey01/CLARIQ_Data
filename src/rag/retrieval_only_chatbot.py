"""
Fast RAG Retrieval Chatbot - No LLM Needed!
Just show students the relevant documents from curriculum.
Works perfectly on low-memory systems.
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path
import os

class RetrievalOnlyRAG:
    def __init__(self):
        """Initialize the retrieval-only RAG system"""
        print("🚀 Starting Fast Retrieval Chatbot (No LLM)...\n")
        
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
        print("✅ Ready to search!\n")
    
    def search_documents(self, query, top_k=3):
        """Search for relevant documents - INSTANT results!"""
        
        # Generate embedding
        query_embedding = self.model.encode(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["documents"][0]:
            print("❌ No documents found in curriculum.\n")
            return []
        
        # Format results
        retrieved = []
        for i in range(len(results["documents"][0])):
            similarity = 1 - results["distances"][0][i]
            retrieved.append({
                "content": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source_pdf", "Unknown"),
                "page": results["metadatas"][0][i].get("page", "?"),
                "similarity": round(similarity * 100, 1)
            })
        
        return retrieved
    
    def display_results(self, query, results):
        """Display search results nicely"""
        if not results:
            return
        
        print(f"\n{'='*75}")
        print(f"📚 SEARCH RESULTS FOR: '{query}'")
        print(f"{'='*75}\n")
        
        for idx, result in enumerate(results, 1):
            print(f"[Result {idx}] Match: {result['similarity']}% 🎯")
            print(f"Source: {result['source']} (Page {result['page']})")
            print(f"{'-'*75}")
            print(f"{result['content'][:500]}...")
            print()
        
        print(f"{'='*75}\n")
    
    def interactive_search(self):
        """Interactive search mode"""
        print("\n" + "="*75)
        print("📖 FAST RETRIEVAL CHATBOT")
        print("(Instant document search - no waiting!)")
        print("="*75)
        print("\nCommands:")
        print("  • Type your question and press Enter")
        print("  • Type 'help' for options")
        print("  • Type 'quit' to exit\n")
        
        while True:
            try:
                query = input("❓ Your Question: ").strip()
                
                if not query:
                    continue
                
                if query.lower() == 'quit':
                    print("\n👋 Goodbye! Thanks for using the Retrieval Chatbot!")
                    break
                
                if query.lower() == 'help':
                    print("\n💡 HELP:")
                    print("  • Ask any question about the curriculum")
                    print("  • System instantly shows relevant paragraphs")
                    print("  • Results show match percentage (0-100%)")
                    print("  • Higher % = more relevant to your question")
                    print("  • Type 'quit' to exit\n")
                    continue
                
                print("\n⚡ Searching curriculum...\n")
                results = self.search_documents(query, top_k=3)
                self.display_results(query, results)
                
                # Optional: Show summary of content
                if results:
                    print("💡 TIP: Read these passages carefully!")
                    print("   The system matched these sections to your question.")
                    print("   Look for keywords that relate to your question.\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    try:
        rag = RetrievalOnlyRAG()
        rag.interactive_search()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you've run: python src/embeddings/build_vector_db.py")
