import os
import urllib.request
import urllib.error
from pathlib import Path
import sys

# Add project root to sys.path to allow importing from ai_engine
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.pipeline.extract_curriculum import extract_and_chunk_pdfs
from ai_engine.pipeline.create_rag_tutor_data import create_rag_knowledge_base, create_question_bank
from ai_engine.embeddings.build_vector_db import rebuild_vector_db

def download_pdf(url: str, dest_dir: Path) -> str:
    """Download a PDF from the given URL into dest_dir. Returns the filename."""
    try:
        filename = url.split("/")[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"
            
        dest_path = dest_dir / filename
        
        print(f"Downloading PDF from {url} to {dest_path}...")
        
        # Add basic User-Agent to avoid 403 Forbidden on some hosts
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
            out_file.write(response.read())
            
        print("Download successful.")
        return filename
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        raise e

def run_ingestion_pipeline(url: str = None, file_path: Path = None, clear_existing: bool = False):
    """
    End-to-end pipeline to download PDF (or use uploaded), extract chunks, build CSVs and rebuild Vector DB.
    """
    print(f"Starting ingestion pipeline (url={url}, file={file_path}, clear_existing={clear_existing})")
    
    # 1. Paths Setup
    pdf_dir = PROJECT_ROOT / "data" / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    json_chunks_file = PROJECT_ROOT / "data" / "raw" / "curriculum_chunks.json"
    
    # 2. Download or Prepare the PDF
    if clear_existing:
        print("Clearing existing PDFs from data/pdfs/...")
        for f in pdf_dir.glob("*.pdf"):
            # Don't delete the newly uploaded file if it was just saved there
            if file_path and f.resolve() == file_path.resolve():
                continue
            f.unlink()

    if url:
        download_pdf(url, pdf_dir)
        
    # 3. Extract Curriculum
    print("\n--- Phase 1: Extracting PDFs to Chunks ---")
    extract_and_chunk_pdfs(str(pdf_dir), str(json_chunks_file))
    
    # 4. Build CSVs
    print("\n--- Phase 2: Building CSV Knowledge Base ---")
    rag_csv = PROJECT_ROOT / "data" / "processed" / "rag_knowledge_base.csv"
    qb_csv = PROJECT_ROOT / "data" / "processed" / "question_bank.csv"
    
    create_rag_knowledge_base(str(json_chunks_file), str(rag_csv))
    create_question_bank(str(json_chunks_file), str(qb_csv))
    
    # 5. Rebuild Vector DB
    print("\n--- Phase 3: Rebuilding Vector DB ---")
    # if clear_existing is False, we might still want to clear the DB and re-embed EVERYTHING 
    # because extract_curriculum.py re-extracted everything.
    # Actually, if we re-extract everything, we MUST clear the DB to avoid duplicates.
    # But wait, build_vector_db does unique constraint check, but it's safer to just clear it.
    # The clear_existing flag passed by user means "Clear old PDFs and old database data".
    rebuild_vector_db(clear_existing=True) 
    
    print("\n✅ Ingestion Pipeline Completed Successfully!")
