# 🤖 RAG Tutor System - Ollama Edition

A lightweight **Retrieval-Augmented Generation (RAG)** chatbot for educational tutoring using **Ollama** (local LLM) and **Chroma** (vector database).

## 🚀 Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Ollama (in one terminal)
ollama serve

# 3. Pull a model (in another terminal)
ollama pull mistral

# 4. Run the chatbot
python src/rag/interactive_chatbot.py

# 5. Ask questions!
❓ Your Question: How does the eye focus?
```

## 📚 What This Does

- ✅ **Searches** 711 curriculum documents using vector embeddings
- ✅ **Retrieves** the 3 most relevant documents
- ✅ **Generates** answers using local Ollama LLM
- ✅ **Works offline** - no API keys needed!

## 📖 Documentation

- **[SETUP_OLLAMA.md](SETUP_OLLAMA.md)** ← **START HERE** - Complete setup guide
- [QUICKSTART.md](docs/QUICKSTART.md) - Quick reference
- [COMPLETE_ARCHITECTURE.md](docs/COMPLETE_ARCHITECTURE.md) - System design
- [CSV_GUIDE.md](docs/CSV_GUIDE.md) - Data formats

## 🗂️ Project Structure

```
TextExtract/
├── src/rag/
│   └── interactive_chatbot.py      ← Main RAG chatbot (RUN THIS)
├── src/embeddings/
│   ├── build_vector_db.py          ← Setup vector database
│   └── search_vector_db.py
├── data/processed/
│   ├── rag_knowledge_base.csv      ← 711 curriculum docs
│   └── question_bank.csv           ← Question library
├── db/chroma_db/                   ← Vector database
├── docs/                           ← Documentation
└── requirements.txt                ← Dependencies
└── .gitignore                         # Git ignore rules

```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Your PDFs

- Place your 15 PDF chapters in `data/pdfs/`

### 3. Extract Text (Step 1: PDFs → Chunks)

```bash
cd src/pipeline
python extract_curriculum.py
# Output: ../../data/raw/curriculum_chunks.json
```

### 4. Create Vector Database (Step 2: Build Embeddings)

```bash
cd ../../src/embeddings
python build_vector_db.py
# Creates: ../../db/chroma_db/
```

### 5. Search & Test (Step 3: Query the System)

```bash
python search_vector_db.py
# Interactive search mode - type your questions!
```

### 6. Run RAG Chatbot (Step 4: Full RAG System)

```bash
cd ../../src/rag
python working_rag_system.py
# Full RAG system with LLM integration
```

## 📊 Data Pipeline

```
PDFs (15 chapters in data/pdfs/)
    ↓
extract_curriculum.py
    ↓
curriculum_chunks.json (data/raw/)
    ↓
build_vector_db.py (creates embeddings)
    ↓
Vector DB (db/chroma_db/)
    ↓
User Question
    ↓
search_vector_db.py (find similar chunks)
    ↓
Relevant Chunks + LLM
    ↓
Answer
```

## ✅ Completed Steps

- ✅ **Extract Text**: Extract text from PDFs (`src/pipeline/extract_curriculum.py`)
- ✅ **Break into Chunks**: Segment text into ~150 word chunks (`extract_curriculum.py`)
- ✅ **Store in CSV**: Save as `data/processed/rag_knowledge_base.csv`
- ✅ **Create Embeddings**: Generate embeddings using Sentence-Transformers (`src/embeddings/build_vector_db.py`)
- ✅ **Vector Database**: Persistent storage in `db/chroma_db/`

## 📝 File Descriptions

### Pipeline Scripts

| File                       | Purpose                    | Input                    | Output                            |
| -------------------------- | -------------------------- | ------------------------ | --------------------------------- |
| `extract_curriculum.py`    | Extract & chunk PDFs       | PDFs from `data/pdfs/`   | `data/raw/curriculum_chunks.json` |
| `json_to_csv.py`           | Convert JSON to CSV        | `curriculum_chunks.json` | `curriculum_paths.csv`            |
| `create_rag_tutor_data.py` | Create tutor-specific data | Raw chunks               | Tutor datasets                    |

### Embeddings Scripts

| File                  | Purpose                              |
| --------------------- | ------------------------------------ |
| `build_vector_db.py`  | Create embeddings & build vector DB  |
| `search_vector_db.py` | Search chunks by semantic similarity |

### RAG Scripts

| File                          | Purpose                 |
| ----------------------------- | ----------------------- |
| `working_rag_system.py`       | Complete RAG chatbot    |
| `rag_tutor_implementation.py` | Tutor-specific features |

## 🔧 Configuration

### PDF Folder Location

Edit `src/pipeline/extract_curriculum.py`:

```python
PDF_FOLDER = "/path/to/your/pdfs"
```

### Embedding Model

Default: `all-MiniLM-L6-v2` (fast, lightweight)

To use a larger model, edit `src/embeddings/build_vector_db.py`:

```python
embedding_model = SentenceTransformer('all-mpnet-base-v2')  # More powerful
```

## 📚 Documentation

- **QUICKSTART.md** - Get started in 5 minutes
- **COMPLETE_ARCHITECTURE.md** - Full system design
- **RAG_WORKING_PROOF.md** - Proof of concept
- **CSV_GUIDE.md** - CSV file formats
- **RAG_TUTOR_SYSTEM.md** - Tutor-specific features

## 🐛 Troubleshooting

### "Vector database not found"

Run `python src/embeddings/build_vector_db.py` first

### "No PDF files found"

Ensure PDFs are in `data/pdfs/` directory

### Memory issues with large PDFs

Edit batch size in `src/embeddings/build_vector_db.py`:

```python
batch_size = 50  # Reduce from 100
```

## 🤝 Contributing

- Follow the folder structure
- Add documentation for new scripts
- Update this README with new features

## 📄 License

Your License Here

---

**Status**: System complete and working ✨
