import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.embeddings.search_vector_db import CurriculumSearchEngine


class FakeEmbedding:
    def encode(self, query):
        class Vector(list):
            def tolist(self):
                return list(self)

        return Vector([0.1, 0.2, 0.3])


class FakeCollection:
    def __init__(self):
        self.calls = []

    def query(self, query_embeddings, n_results, include):
        self.calls.append({
            "query_embeddings": query_embeddings,
            "n_results": n_results,
            "include": include,
        })
        return {
            "documents": [["first document"]],
            "metadatas": [[{"source_pdf": "test.pdf", "page": 7}]],
            "distances": [[0.15]],
        }


def test_search_uses_chromadb_compatible_query_include():
    engine = CurriculumSearchEngine.__new__(CurriculumSearchEngine)
    engine.embedding_model = FakeEmbedding()
    engine.collection = FakeCollection()

    results = engine.search("What is refraction?", top_k=1)

    assert len(results) == 1
    assert results[0]["content"] == "first document"
    assert results[0]["source_pdf"] == "test.pdf"
    assert results[0]["page"] == 7
    assert results[0]["chunk_id"] == "chunk_0"
    assert engine.collection.calls[0]["include"] == ["documents", "metadatas", "distances"]
