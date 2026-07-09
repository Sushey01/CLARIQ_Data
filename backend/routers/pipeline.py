from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, Optional
from pathlib import Path
import shutil
from ..services.pipeline_service import run_ingestion_pipeline, PROJECT_ROOT

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

# Global state to track pipeline status (simple in-memory tracker)
pipeline_status = {
    "is_running": False,
    "last_error": None,
    "last_url": None
}

class IngestRequest(BaseModel):
    url: str
    clear_existing: bool = False

def background_ingest_task(url: Optional[str], file_path: Optional[Path], clear_existing: bool):
    global pipeline_status
    try:
        pipeline_status["is_running"] = True
        pipeline_status["last_error"] = None
        pipeline_status["last_url"] = url or (file_path.name if file_path else "Local File")
        
        run_ingestion_pipeline(url=url, file_path=file_path, clear_existing=clear_existing)
        
    except Exception as e:
        print(f"Pipeline error: {e}")
        pipeline_status["last_error"] = str(e)
    finally:
        pipeline_status["is_running"] = False

@router.post("/ingest-url")
def ingest_url(req: IngestRequest, background_tasks: BackgroundTasks):
    """
    Trigger the automated ingestion pipeline to download a PDF, extract chunks,
    and update the vector database in the background.
    """
    if pipeline_status["is_running"]:
        raise HTTPException(status_code=400, detail="A pipeline task is already running.")
        
    background_tasks.add_task(background_ingest_task, req.url, None, req.clear_existing)
    return {"status": "processing", "message": f"Ingestion started for {req.url}"}

@router.post("/upload-pdf")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    clear_existing: bool = Form(False)
):
    """
    Upload a PDF directly to the backend and trigger the ingestion pipeline.
    """
    if pipeline_status["is_running"]:
        raise HTTPException(status_code=400, detail="A pipeline task is already running.")
        
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF.")
        
    pdf_dir = PROJECT_ROOT / "data" / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = pdf_dir / file.filename
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    background_tasks.add_task(background_ingest_task, None, file_path, clear_existing)
    return {"status": "processing", "message": f"Ingestion started for {file.filename}"}

@router.get("/status")
def get_status() -> Dict:
    """Check the status of the ingestion pipeline."""
    return pipeline_status
