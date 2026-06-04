from models.profile import StudentProfile, StudentProfileUpdate
from services.profile_service import create_profile, get_profile, update_profile
import repositories.profile_repository as profile_repo


def test_create_get_update_profile(tmp_path, monkeypatch):
    storage = tmp_path / "student_profiles"
    monkeypatch.setattr(profile_repo, "STORAGE", storage)
    storage.mkdir(parents=True)

    p = StudentProfile(name="Alice", grade="9")
    created = create_profile(p)
    assert created.student_id is not None

    loaded = get_profile(created.student_id)
    assert loaded.name == "Alice"

    upd = StudentProfileUpdate(grade="10")
    updated = update_profile(created.student_id, upd)
    assert updated.grade == "10"
