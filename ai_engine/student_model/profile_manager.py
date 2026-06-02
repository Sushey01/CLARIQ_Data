"""Scaffold for student profile manager."""
import json
from pathlib import Path


class ProfileManager:
    def __init__(self, storage_dir="data/student_profiles"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_profile(self, student_id, name="Student", grade="clariq"):
        profile = {
            "student_id": student_id,
            "name": name,
            "grade": grade,
            "created_at": "",
            "topics": {}
        }
        path = self.storage_dir / f"{student_id}.json"
        path.write_text(json.dumps(profile, indent=2))
        return profile
