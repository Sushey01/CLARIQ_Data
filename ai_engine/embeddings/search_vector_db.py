import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

class CurriculumSearchEngine:
    def __init__(self):
        """Initialize the search engine with vector database and embedding model."""
        # Connect to existing vector database
        project_root = Path(__file__).resolve().parents[2]
        db_dir = project_root / "db" / "chroma_db"
        if not db_dir.exists():
            raise FileNotFoundError(
                "Vector database not found! Run 'python ai_engine/embeddings/build_vector_db.py' first."
            )
        
        self.client = chromadb.PersistentClient(path=str(db_dir))
        self.collection = self.client.get_collection(name="curriculum")
        
        # Load the same embedding model used for indexing
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def search(self, query, top_k=5):
        """
        Search for relevant curriculum chunks using semantic similarity.
        """
        # Generate embedding for the query
        query_embedding = self.embedding_model.encode(query)
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances", "ids"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "content": results["documents"][0][i],
                "source_pdf": results["metadatas"][0][i].get("source_pdf"),
                "page": int(results["metadatas"][0][i].get("page", 0)),
                "chunk_id": results["ids"][0][i],
                "similarity_score": round(1 - results["distances"][0][i], 3)  # Convert distance to similarity
            })
        
        return formatted_results
    
    def search_interactive(self):
        """Interactive search mode - query until user exits."""
        print("\n" + "="*60)
        print("CURRICULUM VECTOR SEARCH ENGINE")
        print("="*60)
        print(f"Total chunks indexed: {self.collection.count()}")
        print("Type 'quit' to exit\n")
        
        while True:
            query = input("Ask a question: ").strip()
            
            if query.lower() == 'quit':
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            print("\n" + "-"*60)
            results = self.search(query, top_k=5)
            
            if results:
                for idx, result in enumerate(results, 1):
                    print(f"\n[Result {idx}] (Similarity: {result['similarity_score']})")
                    print(f"Source: {result['source_pdf']} (Page {result['page']})")
                    print(f"Chunk ID: {result['chunk_id']}")
                    print(f"Content: {result['content'][:300]}...")
            else:
                print("No results found.")
            
            print("-"*60 + "\n")


def main():
    """Run the search engine."""
    try:
        search_engine = CurriculumSearchEngine()
        search_engine.search_interactive()
    except FileNotFoundError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
