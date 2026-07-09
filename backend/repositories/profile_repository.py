from pathlib import Path
import json
from typing import List

from ..models.profile import StudentProfile

STORAGE = Path("data/student_profiles")
STORAGE.mkdir(parents=True, exist_ok=True)


def profile_path(student_id: str) -> Path:
    return STORAGE / f"{student_id}.json"


def profile_exists(student_id: str) -> bool:
    return profile_path(student_id).exists()


def save_profile(profile: StudentProfile) -> None:
    if profile.student_id is None:
        raise ValueError("student_id is required to save a profile")
    profile_path(profile.student_id).write_text(profile.model_dump_json(indent=2))


def load_profile(student_id: str) -> StudentProfile:
    data = json.loads(profile_path(student_id).read_text())
    return StudentProfile(**data)


def list_profiles() -> List[StudentProfile]:
    profiles: List[StudentProfile] = []
    for p in STORAGE.glob("*.json"):
        try:
            data = json.loads(p.read_text())
            profiles.append(StudentProfile(**data))
        except Exception:
            # skip malformed files
            continue
    return profiles


def delete_profile(student_id: str) -> None:
    p = profile_path(student_id)
    if p.exists():
        p.unlink()
