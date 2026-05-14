# 🚀 QUICK START - RAG Tutor with Ollama

## ⚡ 5-Minute Setup

```bash
# 1. Install Python packages
pip install -r requirements.txt

# 2. Start Ollama server (Terminal 1)
ollama serve

# 3. Pull a model (Terminal 2)
ollama pull mistral

# 4. Run chatbot (Terminal 2)
python src/rag/interactive_chatbot.py

# 5. Start asking!
❓ Your Question: How does photosynthesis work?
```

---

## 🔥 Available Ollama Models

**Smallest/Fastest:**
```bash
ollama pull mistral          # Good balance (7B)
ollama pull neural-chat      # Fast & decent (7B)
ollama pull orca-mini        # Very fast (3B)
```

**Larger/Better Quality:**
```bash
ollama pull llama2           # Popular (7B)
ollama pull llama2:13b       # Better answers but slower
ollama pull dolphin-mixtral  # Good quality (8x7B)
```

**Usage:**
```bash
python src/rag/interactive_chatbot.py mistral
python src/rag/interactive_chatbot.py llama2
python src/rag/interactive_chatbot.py orca-mini
```

---

## 📚 What's Inside

| Component | Location | Purpose |
|-----------|----------|---------|
| **Main Chatbot** | `src/rag/interactive_chatbot.py` | Run this! |
| **Vector DB Setup** | `src/embeddings/build_vector_db.py` | One-time setup |
| **Knowledge Base** | `data/processed/rag_knowledge_base.csv` | 711 documents |
| **Questions** | `data/processed/question_bank.csv` | Question library |
| **Vector DB** | `db/chroma_db/` | Search engine (pre-indexed) |

---

## ⚙️ System Architecture

```
Your Question
     ↓
Embed (SentenceTransformer)
     ↓
Search Chroma DB (Fast!)
     ↓
Retrieve 3 Docs
     ↓
Send to Ollama LLM
     ↓
Get Answer
     ↓
Display
```

---

## 🐛 Common Issues

| Issue | Fix |
|-------|-----|
| "Ollama not running" | Terminal 1: `ollama serve` |
| "Model not found" | Terminal 2: `ollama pull mistral` |
| "Connection refused" | Check if Ollama is on port 11434 |
| "No documents found" | Rebuild DB: `python src/embeddings/build_vector_db.py` |
| "Slow responses" | Use smaller model: `python src/rag/interactive_chatbot.py orca-mini` |

---

## 📖 Full Documentation

- **[SETUP_OLLAMA.md](SETUP_OLLAMA.md)** - Complete setup guide
- **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - What was cleaned up
- **[README.md](README.md)** - Project overview
- **[docs/COMPLETE_ARCHITECTURE.md](docs/COMPLETE_ARCHITECTURE.md)** - Technical details

---

## 💡 Tips

✅ **First time?** Start with `mistral` - good balance  
✅ **Want better answers?** Use `llama2:13b` (slower but better)  
✅ **Want speed?** Use `orca-mini` (3B, very fast)  
✅ **Running on laptop?** Use `orca-mini` or `mistral`  
✅ **Running on GPU?** Use larger models like `llama2:13b`  

---

**Ready? Run this:**
```bash
python src/rag/interactive_chatbot.py
```

Enjoy! 🎓
