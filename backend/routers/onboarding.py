from fastapi import APIRouter, HTTPException
from backend.models.profile import StudentProfile
from pathlib import Path
import json
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

STORAGE = Path("data/student_profiles")
STORAGE.mkdir(parents=True, exist_ok=True)


@router.post("/create", response_model=StudentProfile)
def create_profile(profile: StudentProfile):
    # write profile to disk for prototype
    sid = profile.student_id or str(uuid4())
    if (STORAGE / f"{sid}.json").exists():
        raise HTTPException(status_code=400, detail="Profile already exists")
    if not profile.created_at:
        profile.created_at = datetime.utcnow().isoformat()
    path = STORAGE / f"{sid}.json"
    path.write_text(profile.json(indent=2))
    return profile


@router.get("/{student_id}", response_model=StudentProfile)
def get_profile(student_id: str):
    path = STORAGE / f"{student_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Profile not found")
    data = json.loads(path.read_text())
    return StudentProfile(**data)
