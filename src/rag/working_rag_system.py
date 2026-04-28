"""
WORKING RAG SYSTEM - No Model Training Required!
Uses pre-trained embeddings (sentence-transformers)
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from sklearn.metrics.pairwise import cosine_similarity

class SimpleRAGSystem:
    """
    RAG system that works IMMEDIATELY without training.
    Uses pre-trained embeddings.
    """
    
    def __init__(self, knowledge_base_csv):
        """Initialize RAG with existing knowledge base"""
        
        print("🚀 Initializing RAG System...")
        
        # Load knowledge base
        self.kb = pd.read_csv(knowledge_base_csv)
        print(f"✅ Loaded {len(self.kb)} documents")
        
        # Load pre-trained embedding model (no training needed!)
        print("📚 Loading embedding model (pre-trained)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Chroma vector database (you already have this!)
        print("💾 Setting up Chroma vector database...")
        self.client = chromadb.EphemeralClient()
        
        # Create collection
        self.collection = self.client.get_or_create_collection(
            name="science_curriculum",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Add documents to Chroma
        self._index_documents()
        
        print("✅ RAG System Ready!\n")
    
    def _index_documents(self):
        """Add all documents to vector database"""
        
        print("🔗 Indexing documents...")
        
        documents = self.kb['content'].tolist()
        doc_ids = self.kb['doc_id'].tolist()
        
        # Generate embeddings (pre-trained model does this)
        embeddings = self.model.encode(documents, show_progress_bar=True)
        
        # Add to Chroma in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))
            
            self.collection.add(
                ids=doc_ids[i:batch_end],
                embeddings=embeddings[i:batch_end].tolist(),
                documents=documents[i:batch_end],
                metadatas=[
                    {
                        'topic': self.kb.iloc[j]['topic'],
                        'difficulty': self.kb.iloc[j]['difficulty'],
                        'page': str(self.kb.iloc[j]['page']),
                        'source': self.kb.iloc[j]['source_pdf']
                    }
                    for j in range(i, batch_end)
                ]
            )
            print(f"  Indexed {batch_end}/{len(documents)} documents")
        
        print("✅ All documents indexed!\n")
    
    def retrieve(self, query, top_k=3, difficulty=None):
        """
        Retrieve relevant documents for a query (THE RAG RETRIEVAL!)
        
        This is the "R" in RAG - Retrieval Augmented Generation
        """
        
        print(f"\n🔍 Query: '{query}'")
        
        # Encode the query (using pre-trained model)
        query_embedding = self.model.encode(query)
        
        # Search in Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where={"difficulty": difficulty} if difficulty else None
        )
        
        # Format results
        retrieved_docs = []
        
        print(f"\n📚 Retrieved {len(results['ids'][0])} documents:\n")
        
        for i, (doc_id, document, metadata) in enumerate(
            zip(results['ids'][0], results['documents'][0], results['metadatas'][0])
        ):
            retrieved_docs.append({
                'rank': i + 1,
                'doc_id': doc_id,
                'content': document,
                'topic': metadata['topic'],
                'difficulty': metadata['difficulty'],
                'source': metadata['source']
            })
            
            print(f"  [{i+1}] {metadata['topic']} ({metadata['difficulty']}) - Page {metadata['page']}")
            print(f"       {document[:100]}...\n")
        
        return retrieved_docs
    
    def answer_question(self, question, difficulty=None):
        """
        Answer a question using RAG
        
        Steps:
        1. Retrieve relevant documents
        2. Show what was found
        3. User can use this info to answer
        """
        
        print("\n" + "="*70)
        print("RAG QUESTION ANSWERING")
        print("="*70)
        
        # Step 1: Retrieve (the RAG part)
        docs = self.retrieve(question, top_k=3, difficulty=difficulty)
        
        # Step 2: Display for user/LLM
        print("\n📖 CONTEXT FROM CURRICULUM:")
        print("-" * 70)
        for doc in docs:
            print(f"\nFrom: {doc['source']} (Page {doc['topic']})")
            print(f"Content: {doc['content']}")
        
        print("\n" + "-" * 70)
        print("✅ Use the above context to answer the question!")
        print("   (In production, this context would go to GPT/LLaMA)")
        
        return docs
    
    def score_answer(self, student_answer, question):
        """
        Score a student's answer by comparing similarity
        to relevant documents
        """
        
        print(f"\n{'='*70}")
        print("SCORING STUDENT ANSWER")
        print(f"{'='*70}")
        
        # Get relevant documents
        docs = self.retrieve(question, top_k=2)
        
        # Encode student answer
        answer_emb = self.model.encode(student_answer)
        
        # Compare with document embeddings
        doc_embs = self.model.encode([doc['content'] for doc in docs])
        
        # Calculate similarity
        from sklearn.metrics.pairwise import cosine_similarity
        
        similarities = cosine_similarity([answer_emb], doc_embs)[0]
        avg_similarity = np.mean(similarities)
        
        print(f"\n📝 Student Answer: '{student_answer}'")
        print(f"\n✅ Similarity Score: {avg_similarity:.2%}")
        
        if avg_similarity > 0.75:
            print("Rating: ⭐⭐⭐ EXCELLENT")
            return 'excellent', avg_similarity
        elif avg_similarity > 0.55:
            print("Rating: ⭐⭐ GOOD")
            return 'good', avg_similarity
        elif avg_similarity > 0.35:
            print("Rating: ⭐ POOR")
            return 'poor', avg_similarity
        else:
            print("Rating: ❌ INCORRECT")
            return 'incorrect', avg_similarity

def main():
    """
    DEMO: Working RAG system with curriculum data
    No model training required!
    """
    
    # Initialize RAG
    import os
    kb_path = os.path.join(os.path.dirname(__file__), '../../data/processed/rag_knowledge_base.csv')
    kb_path = os.path.abspath(kb_path)
    rag = SimpleRAGSystem(kb_path)
    
    print("\n" + "="*70)
    print("DEMO 1: Answer a Question (Retrieval)")
    print("="*70)
    
    # Example 1: Ask about the eye
    rag.answer_question("How does the human eye work?")
    
    print("\n" + "="*70)
    print("DEMO 2: Score a Student Answer")
    print("="*70)
    
    # Example 2: Score student answer
    student_answer = "The eye is an organ that uses light and enables us to see"
    rag.score_answer(student_answer, "What is the human eye?")
    
    print("\n" + "="*70)
    print("DEMO 3: Filtered Retrieval (Easy Level)")
    print("="*70)
    
    # Example 3: Retrieve only easy documents
    rag.retrieve("What is light?", top_k=2, difficulty="easy")
    
    print("\n" + "="*70)
    print("✅ RAG SYSTEM WORKING!")
    print("="*70)

if __name__ == "__main__":
    main()
