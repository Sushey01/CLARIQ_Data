# ✅ Working Ollama Chatbot - Quick Start

## Current Status
✅ **RAG System:** Fully functional  
✅ **Document Search:** Working (high-quality results: 68%+ similarity)  
✅ **Ollama API:** Working (returns streaming responses)  
✅ **Chat Logging:** Saves to CSV automatically  

## Known Issue
**Memory Pressure:** Your system has limited RAM (507MB free / 7.5GB total)
- phi model: 1.6GB
- orca-mini model: 2.0GB
- Result: Responses are slow but DO work

## How to Use

### Option 1: Use PHI (Smaller, Faster) - RECOMMENDED
```bash
cd /home/shekhar/Documents/FYP/TextExtract
python src/rag/interactive_chatbot.py phi student_id
```

### Option 2: Use ORCA-MINI (Larger, Better Quality)
```bash
cd /home/shekhar/Documents/FYP/TextExtract
python src/rag/interactive_chatbot.py orca-mini student_id
```

## What to Expect
- **Document Search:** 2-3 seconds (fast ✅)
- **Answer Generation:** 
  - phi: 30-60 seconds  
  - orca-mini: 60-120 seconds (may timeout if system is slow)
  
## If It Hangs
1. Reboot: `sudo reboot`
2. Close other applications before running
3. Don't run other heavy programs

## Chat History
All interactions saved to: `data/processed/student_interactions.csv`

## To Verify Everything Works
```bash
# Check if models are installed
ollama list

# Quick API test
curl -s http://localhost:11434/api/generate -d '{"model":"phi","prompt":"test"}' | head -c 100
```

## Next Steps for Supervisor
Tell your supervisor:
- ✅ Ollama integration complete (no Gemini)
- ✅ RAG system working (documents retrieved correctly)
- ✅ Chat logging implemented
- 🔧 Note: System is memory-constrained, responses take 30-120 seconds
- 📌 FastAPI can be added later if needed for multi-user access

---
**System Specs:**
- RAM: 7.5GB (507MB free)
- Swap: 4GB (almost full)
- CPU: Intel i5-8350U
- Models: phi (1.6GB), orca-mini (2.0GB)
