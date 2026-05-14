# 🚀 RAG Tutor System - Ollama Setup Guide

## ✅ What You Have (Already Setup)

- **Curriculum Vector Database**: `db/chroma_db/` (711 documents indexed)
- **RAG Chatbot**: `src/rag/interactive_chatbot.py` (Ollama-only)
- **Knowledge Base**: `data/processed/rag_knowledge_base.csv`
- **Question Bank**: `data/processed/question_bank.csv`

---

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running locally

### Install Ollama
```bash
# On Linux/Mac:
curl -fsSL https://ollama.ai/install.sh | sh

# On Windows:
# Download from https://ollama.ai/download/windows
```

### Start Ollama Server
```bash
ollama serve
# This starts Ollama on http://localhost:11434
```

### Pull a Model (First Time Only)
```bash
# In a new terminal, pull the mistral model:
ollama pull mistral

# OR use any other Ollama model:
ollama pull llama2
ollama pull neural-chat
ollama pull orca-mini
```

---

## 🔧 Installation

### 1. Install Python Dependencies
```bash
cd /home/shekhar/Documents/FYP/TextExtract
pip install -r requirements.txt
```

### 2. Build Vector Database (First Time Only)
```bash
# If Chroma DB doesn't exist yet:
python src/embeddings/build_vector_db.py
```

---

## 🎯 Running the Chatbot

### Basic Usage
```bash
# Use default model (mistral):
python src/rag/interactive_chatbot.py

# Use a different model:
python src/rag/interactive_chatbot.py llama2
python src/rag/interactive_chatbot.py neural-chat
```

### Example Session
```
🚀 Starting Interactive RAG Chatbot...

✅ Loaded 711 documents from knowledge base
✅ Embedding model loaded
✅ Connected to 711 indexed documents
✅ Ollama is running (model: mistral)

🤖 INTERACTIVE RAG CHATBOT
(Using Ollama)
===========================================================================

Commands:
  • Type your question and press Enter
  • Type 'help' for more options
  • Type 'quit' to exit

❓ Your Question: How does the human eye focus on objects?

🔍 Searching curriculum...

📚 Found 3 relevant sections:

[Result 1] Similarity: 89.5% 🎯
Source: jesc110.pdf (Page 1)
Word Count: 147
───────────────────────────────────────────────────────────────────────────
The human eye is a complex optical system...

🤖 Generating answer from Ollama...

===============================================================================
✨ ANSWER FROM OLLAMA:

Based on the provided context, the human eye focuses on objects through a 
process called accommodation. The eye lens changes shape to adjust the focus...

===============================================================================
```

---

## 🐛 Troubleshooting

### "Ollama not running"
```bash
# Make sure Ollama server is started in another terminal:
ollama serve
```

### "Model not found"
```bash
# Pull the model first:
ollama pull mistral
ollama pull llama2
```

### "Chroma database connection failed"
```bash
# Rebuild the vector database:
python src/embeddings/build_vector_db.py
```

### Poor Answer Quality
- Try a different model: `python src/rag/interactive_chatbot.py llama2`
- Increase model size: `ollama pull llama2:7b` (larger = better quality but slower)

---

## 📊 System Architecture

```
Question Input
    ↓
Embed Question (SentenceTransformer)
    ↓
Search Chroma DB (Vector Database)
    ↓
Retrieve Top 3 Documents
    ↓
Send to Ollama LLM (Local)
    ↓
Generate Answer
    ↓
Display to User
```

---

## 🗂️ File Structure (Cleaned Up)

```
TextExtract/
├── src/
│   ├── rag/
│   │   └── interactive_chatbot.py  ← RUN THIS
│   ├── embeddings/
│   │   ├── build_vector_db.py
│   │   └── search_vector_db.py
│   └── pipeline/
│       ├── extract_curriculum.py    (for reference)
│       ├── create_rag_tutor_data.py (for reference)
│       └── json_to_csv.py           (for reference)
├── data/
│   ├── processed/
│   │   ├── rag_knowledge_base.csv
│   │   └── question_bank.csv
│   ├── pdfs/
│   │   └── (curriculum PDFs)
│   └── raw/
│       └── curriculum_chunks.json
├── db/
│   └── chroma_db/  ← Vector Database
│       ├── chroma.sqlite3
│       └── [collections...]
├── docs/
│   ├── COMPLETE_ARCHITECTURE.md
│   ├── CSV_GUIDE.md
│   ├── RAG_TUTOR_SYSTEM.md
│   ├── RAG_WORKING_PROOF.md
│   └── QUICKSTART.md
├── requirements.txt
├── README.md
└── SETUP_OLLAMA.md  ← YOU ARE HERE
```

---

## 💡 Quick Commands Reference

```bash
# Start Ollama (in one terminal)
ollama serve

# Install dependencies
pip install -r requirements.txt

# Build vector database (first time only)
python src/embeddings/build_vector_db.py

# Run the chatbot
python src/rag/interactive_chatbot.py

# List available Ollama models
ollama list

# Pull a new model
ollama pull mistral
```

---

## ✨ Features

✅ Local Ollama integration (no API keys needed)  
✅ Fast semantic search using Chroma DB  
✅ 711 curriculum documents indexed  
✅ Multiple Ollama model support  
✅ Interactive Q&A interface  
✅ Shows similarity scores and sources  

---

## 🎓 Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Start Ollama: `ollama serve`
3. ✅ Run chatbot: `python src/rag/interactive_chatbot.py`
4. ✅ Ask questions!

Enjoy your RAG tutor! 🚀
