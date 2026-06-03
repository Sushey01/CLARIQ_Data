from fastapi import APIRouter

from models.profile import StudentProfile
from services.profile_service import create_profile as create_profile_service
from services.profile_service import get_profile as get_profile_service

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

@router.post("/create", response_model=StudentProfile)
def create_profile(profile: StudentProfile):
    return create_profile_service(profile)

@router.get("/{student_id}", response_model=StudentProfile)
def get_profile(student_id: str):
    return get_profile_service(student_id)