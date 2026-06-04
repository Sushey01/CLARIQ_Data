from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException

from models.profile import StudentProfile, StudentProfileUpdate
from repositories.profile_repository import (
    load_profile,
    profile_exists,
    save_profile,
    list_profiles,
)


def create_profile(profile: StudentProfile) -> StudentProfile:
    student_id = profile.student_id or str(uuid4())

    if profile_exists(student_id):
        raise HTTPException(status_code=400, detail="Profile already exists")

    if not profile.created_at:
        profile.created_at = datetime.now(timezone.utc).isoformat()

    profile.student_id = student_id
    save_profile(profile)
    return profile


def get_profile(student_id: str) -> StudentProfile:
    if not profile_exists(student_id):
        raise HTTPException(status_code=404, detail="Profile not found")

    return load_profile(student_id)


def update_profile(student_id: str, update: StudentProfileUpdate) -> StudentProfile:
    if not profile_exists(student_id):
        raise HTTPException(status_code=404, detail="Profile not found")

    existing = load_profile(student_id)

    # Support pydantic v2's model_dump / v1's dict
    if hasattr(update, "model_dump"):
        update_data = update.model_dump(exclude_unset=True)
    else:
        update_data = update.dict(exclude_unset=True)

    for k, v in update_data.items():
        if v is None:
            continue
        if k == "topics" and isinstance(v, dict):
            existing_topics = existing.topics or {}
            existing_topics.update(v)
            existing.topics = existing_topics
        else:
            setattr(existing, k, v)

    save_profile(existing)
    return existing


def list_all_profiles() -> list[StudentProfile]:
    return list_profiles()
