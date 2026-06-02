"""
Build a Socratic dataset JSONL from processed CSV sources.

Reads:
 - data/processed/question_bank.csv
 - data/processed/rag_knowledge_base.csv

Writes:
 - data/socratic_dataset.jsonl (one JSON object per line)

This is a simple, reproducible extractor useful for prototyping. It
pairs questions with the matching RAG chunk (by doc_id) when available
and preserves provenance.
"""
import csv
import json
from pathlib import Path
from typing import Dict


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)


def load_rag_index(rag_csv_path: Path) -> Dict[str, Dict]:
    mapping = {}
    if not rag_csv_path.exists():
        return mapping
    with rag_csv_path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            doc_id = row.get("doc_id")
            if not doc_id:
                continue
            mapping[doc_id] = {
                "source_pdf": row.get("source_pdf"),
                "page": row.get("page"),
                "topic": row.get("topic"),
                "subtopic": row.get("subtopic"),
                "difficulty": row.get("difficulty"),
                "content": row.get("content"),
                "word_count": row.get("word_count"),
            }
    return mapping


def build_dataset(question_csv: Path, rag_index: Dict[str, Dict], out_path: Path, limit: int = None):
    written = 0
    missing = 0
    with question_csv.open("r", encoding="utf-8") as f, out_path.open("w", encoding="utf-8") as out:
        r = csv.DictReader(f)
        for i, row in enumerate(r):
            if limit and written >= limit:
                break
            qid = row.get("question_id") or f"q_{i}"
            related = row.get("related_doc_id")
            evidence = None
            source = None
            if related and related in rag_index:
                evidence = rag_index[related].get("content")
                source = related
            else:
                missing += 1

            item = {
                "id": qid,
                "topic": row.get("topic"),
                "prompt": row.get("question_text"),
                "question_type": row.get("question_type"),
                "difficulty": row.get("difficulty"),
                "source_doc": source,
                "evidence": evidence or row.get("expected_answer_context"),
                "expected_answer_context": row.get("expected_answer_context"),
                "raw": {k: row.get(k) for k in row},
            }
            out.write(json.dumps(item, ensure_ascii=False) + "\n")
            written += 1

    print(f"Wrote {written} items to {out_path}. Missing evidence for {missing} items.")


def main():
    question_csv = PROCESSED / "question_bank.csv"
    rag_csv = PROCESSED / "rag_knowledge_base.csv"
    out_path = OUT / "socratic_dataset.jsonl"

    if not question_csv.exists():
        print("question_bank.csv not found in data/processed/ — aborting")
        return

    rag_index = load_rag_index(rag_csv)
    build_dataset(question_csv, rag_index, out_path, limit=None)


if __name__ == "__main__":
    main()
