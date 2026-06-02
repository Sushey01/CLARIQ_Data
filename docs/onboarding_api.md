# Onboarding API

Endpoints (prototype):

- `POST /onboarding/create` — create a new student profile. Body: `StudentProfile` Pydantic model.
- `GET /onboarding/{student_id}` — fetch student profile.

Notes:
- Storage is file-based under `data/student_profiles/` for the scaffold. Replace with DB in production.
- `StudentProfile` model lives in `backend/models/profile.py`.
