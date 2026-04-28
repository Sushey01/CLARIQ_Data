# 🗂️ TextExtract - Folder Structure Guide

## One-Line Summary

```
PDFs → Extract Text → Break into Chunks → Create Embeddings → RAG Chatbot
 📂     🔍              ✂️                   🧠                 💬
```

---

## 📂 Folder Breakdown

### `data/` - All Data Files

```
data/
├── pdfs/          ← Place your 15 PDF chapters here
├── raw/           ← Extracted JSON & initial data
│   ├── curriculum_chunks.json    (5000+ text chunks)
│   └── curriculum_paths.csv
└── processed/     ← Ready for ML/RAG
    ├── rag_knowledge_base.csv    (Main knowledge base)
    ├── question_bank.csv          (Q&A pairs)
    ├── dataset_*.csv              (7 ML datasets)
    └── student_*.csv              (Student data)
```

**When to use each:**

- **`data/pdfs/`**: Your source material
- **`data/raw/`**: Step 1 output (after extraction)
- **`data/processed/`**: Step 2-3 output (ready for RAG/ML)

---

### `src/` - Source Code (Organized by Function)

#### `src/pipeline/` - Extract & Process

```
extract_curriculum.py      Step 1: PDFs → curriculum_chunks.json
├─ Reads from:     data/pdfs/
├─ Outputs:        data/raw/curriculum_chunks.json
└─ Purpose:        Extract text, split into ~150 word chunks

json_to_csv.py             Convert JSON to CSV format
└─ Used by:        Other scripts that need CSV

create_rag_tutor_data.py   Create tutor-specific datasets
└─ Purpose:        Prepare data for tutoring system
```

**How to use:**

```bash
cd src/pipeline
python extract_curriculum.py
```

---

#### `src/embeddings/` - Vector Database

```
build_vector_db.py         Step 2: Create embeddings & index
├─ Reads from:     data/raw/curriculum_chunks.json
├─ Creates:        db/chroma_db/ (vector database)
└─ Purpose:        Turn text into numbers (embeddings)

search_vector_db.py        Step 3: Search similar chunks
├─ Uses:           db/chroma_db/
├─ Input:          Questions (text)
└─ Output:         Similar chunks (ranked by relevance)
```

**How to use:**

```bash
cd src/embeddings
python build_vector_db.py    # Build the database first
python search_vector_db.py   # Then search
```

---

#### `src/rag/` - RAG Chatbot

```
working_rag_system.py      Step 4: Full RAG system
├─ Reads from:     data/processed/rag_knowledge_base.csv
├─ Uses:           db/chroma_db/
└─ Purpose:        Answer questions using searched chunks

rag_tutor_implementation.py Tutor-specific features
└─ Purpose:        Student interaction tracking
```

**How to use:**

```bash
cd src/rag
python working_rag_system.py
```

---

#### `src/ml/` - Machine Learning Datasets

```
create_labeled_datasets.py          Create labeled data
create_proper_ml_datasets.py        Format for ML models
create_training_csv.py              Create training CSVs
```

**These create files in `data/processed/dataset_*.csv`**

---

### `db/` - Vector Database

```
db/
└── chroma_db/        ← Persistent storage for embeddings
    └── (auto-generated files)
```

**What is this?**

- Stores embeddings (numbers) for all text chunks
- Enables fast semantic search
- Created by `build_vector_db.py`

---

### `docs/` - Documentation

```
docs/
├── README.md                      ← Main guide (read this first!)
├── QUICKSTART.md                  ← 5-minute setup
├── COMPLETE_ARCHITECTURE.md       ← System design
├── RAG_WORKING_PROOF.md           ← Proof it works
├── CSV_GUIDE.md                   ← CSV formats
├── RAG_TUTOR_SYSTEM.md            ← Tutor features
└── ... (other guides)
```

**Start with:** `README.md` or `QUICKSTART.md`

---

## 🔄 Full Pipeline

```
1️⃣  PDFs in data/pdfs/
    ↓
2️⃣  python src/pipeline/extract_curriculum.py
    ↓ (Creates: data/raw/curriculum_chunks.json)
3️⃣  python src/embeddings/build_vector_db.py
    ↓ (Creates: db/chroma_db/)
4️⃣  python src/embeddings/search_vector_db.py
    ↓ (Search works! Interactive mode)
5️⃣  python src/rag/working_rag_system.py
    ↓ (Full RAG chatbot ready)
✅  Done!
```

---

## 📝 File Locations Reference

| Task             | Script                               | Input                                   | Output                            |
| ---------------- | ------------------------------------ | --------------------------------------- | --------------------------------- |
| Extract PDFs     | `src/pipeline/extract_curriculum.py` | `data/pdfs/`                            | `data/raw/curriculum_chunks.json` |
| Build Embeddings | `src/embeddings/build_vector_db.py`  | `data/raw/curriculum_chunks.json`       | `db/chroma_db/`                   |
| Search           | `src/embeddings/search_vector_db.py` | User query                              | Search results                    |
| Run RAG          | `src/rag/working_rag_system.py`      | `data/processed/rag_knowledge_base.csv` | AI answers                        |

---

## 💡 Key Concepts

### Why this structure?

1. **Clear separation**: Each folder has one job
2. **Easy to find**: Search for embeddings? Look in `src/embeddings/`
3. **Scalable**: Easy to add new features
4. **Collaborative**: Others understand the layout instantly

### Data Flow

```
RAW DATA (PDFs)
    ↓
PROCESSED DATA (CSVs, JSONs)
    ↓
EMBEDDINGS (Vector DB)
    ↓
SEARCH & RAG (Answers)
```

---

## 🚀 Common Tasks

### "I want to extract PDFs again"

```bash
python src/pipeline/extract_curriculum.py
```

### "I want to search for something"

```bash
python src/embeddings/search_vector_db.py
```

### "I want to ask the RAG system questions"

```bash
python src/rag/working_rag_system.py
```

### "I need to use the data in a script"

```python
import pandas as pd
# Read the knowledge base
kb = pd.read_csv('data/processed/rag_knowledge_base.csv')
```

---

## ⚠️ Important Notes

- **Always run from project root**: Not from inside `src/`
- **PDFs go in `data/pdfs/`**: The extract script looks there
- **Vector DB gets created automatically**: Don't manually edit `db/chroma_db/`
- **Docs are for reference**: Check them before running scripts

---

**Status**: ✅ System ready to use! Start with `README.md`
