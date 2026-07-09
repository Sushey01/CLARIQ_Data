from fastapi import APIRouter
from typing import List

from ..models.profile import StudentProfile, StudentProfileUpdate
from ..services.profile_service import (
    create_profile as create_profile_service,
    get_profile as get_profile_service,
    update_profile as update_profile_service,
    list_all_profiles as list_profiles_service,
)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/create", response_model=StudentProfile)
def create_profile(profile: StudentProfile):
    return create_profile_service(profile)


@router.get("/{student_id}", response_model=StudentProfile)
def get_profile(student_id: str):
    return get_profile_service(student_id)


@router.patch("/{student_id}", response_model=StudentProfile)
def update_profile(student_id: str, profile_update: StudentProfileUpdate):
    return update_profile_service(student_id, profile_update)


@router.get("/", response_model=List[StudentProfile])
def list_profiles():
    return list_profiles_service()