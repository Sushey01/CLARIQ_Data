import json
import chromadb
from sentence_transformers import SentenceTransformer
import os
from pathlib import Path

# Get absolute paths based on script location
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parents[1]

# Initialize Chroma client with persistent storage
db_dir = project_root / "db" / "chroma_db"
db_dir.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(db_dir))

# Load the sentence transformer model for embeddings
print("Loading embedding model (this may take a moment)...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, efficient model

# Get or create collection
collection = client.get_or_create_collection(
    name="curriculum",
    metadata={"hnsw:space": "cosine"}
)

# Load curriculum chunks
print("Loading curriculum chunks...")
chunks_file = project_root / "data" / "raw" / "curriculum_chunks.json"
with open(chunks_file, "r") as f:
    chunks = json.load(f)

print(f"Found {len(chunks)} chunks")

# Prepare data for embedding
documents = []
ids = []
metadatas = []

for chunk in chunks:
    documents.append(chunk.get("content", ""))
    ids.append(chunk.get("chunk_id"))
    metadatas.append({
        "source_pdf": chunk.get("source_pdf"),
        "page": str(chunk.get("page")),
        "word_count": str(chunk.get("word_count"))
    })

# Generate embeddings and add to collection
print("Generating embeddings and adding to vector database...")
embeddings = embedding_model.encode(documents, show_progress_bar=True)

# Add to collection in batches to avoid memory issues
batch_size = 100
for i in range(0, len(documents), batch_size):
    batch_end = min(i + batch_size, len(documents))
    collection.add(
        documents=documents[i:batch_end],
        embeddings=embeddings[i:batch_end].tolist(),
        ids=ids[i:batch_end],
        metadatas=metadatas[i:batch_end]
    )
    print(f"Processed {batch_end}/{len(documents)} chunks")

print(f"\n✓ Vector database created successfully!")
print(f"✓ Total chunks indexed: {collection.count()}")
print(f"✓ Database saved to: {db_dir}")
