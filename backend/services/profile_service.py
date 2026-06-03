from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException

from models.profile import StudentProfile
from repositories.profile_repository import load_profile, profile_exists, save_profile


def create_profile(profile: StudentProfile) -> StudentProfile:
    student_id = profile.student_id or str(uuid4())

    if profile_exists(student_id):
        raise HTTPException(status_code=400, detail="Profile already exists")

    if not profile.created_at:
        profile.created_at = datetime.utcnow().isoformat()

    profile.student_id = student_id
    save_profile(profile)
    return profile


def get_profile(student_id: str) -> StudentProfile:
    if not profile_exists(student_id):
        raise HTTPException(status_code=404, detail="Profile not found")

    return load_profile(student_id)
