"""
Interactive RAG Chatbot - Ask questions and get answers!
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path
import os

class InteractiveRAG:
    def __init__(self):
        """Initialize the RAG system"""
        print("🚀 Starting Interactive RAG Chatbot...")
        
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
        
        print(f"✅ Connected to {self.collection.count()} indexed documents\n")
    
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
            return
        
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
        
        for idx, i in enumerate(valid_results, 1):
            similarity = round(1 - results["distances"][0][i], 3)
            doc = results["documents"][0][i]
            metadata = results["metadatas"][0][i]
            
            print(f"\n[Result {idx}] Similarity: {similarity*100:.1f}% 🎯")
            print(f"Source: {metadata.get('source_pdf', 'Unknown')} (Page {metadata.get('page', '?')})")
            print(f"Word Count: {metadata.get('word_count', '?')}")
            print("-" * 75)
            print(f"{doc[:500]}...")
            print()
        
        print("=" * 75)
        print("\n💡 TIP: Send the above text to an LLM (GPT/Claude) to generate an answer!\n")
    
    def interactive_chat(self):
        """Interactive chat mode"""
        print("\n" + "="*75)
        print("🤖 INTERACTIVE RAG CHATBOT")
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
                
                print("\n💡 HELP:")
                print("  • Ask any question about the curriculum")
                print("  • System will search and retrieve relevant content")
                print("  • Results show similarity score (0-100%)")
                print("  • Low scores mean topic may not be in curriculum")
                print("  • Use the content to generate answers with an LLM")
                print("  • Type 'quit' to exit\n")
                
                print("\n🔍 Searching curriculum...\n")
                self.search_and_display(query, top_k=3)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    try:
        rag = InteractiveRAG()
        rag.interactive_chat()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you've run: python src/embeddings/build_vector_db.py")
