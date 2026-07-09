# Weekly Progress Report

**Date:** July 9, 2026  
**Project:** Clariq — AI-Powered Socratic Science Tutor (FYP CMP6200)  
**Name:** Shekhar Lamichhane Magar | Student ID: 23189647

---

## Executive Summary

This week focused on improving the Socratic tutoring flow so it feels helpful instead of repetitive. The earlier behavior could keep asking the same practical-example style question even after the student showed partial understanding or asked for a direct explanation. I updated the logic so it now starts with a simple Socratic prompt, gives one or two hints if the student is confused, and then switches to a direct explanation instead of looping endlessly.

I also checked the backend entrypoint path for future frontend integration. The backend app now imports correctly from the project root as `backend.main`, and the chat service regression test confirms the tutor can switch from Socratic mode to explanation mode when the student says they are confused.

---

## What Changed vs Before

| Area | Before | After |
|------|--------|-------|
| Socratic prompt flow | Repeated practical-example questions could loop for multiple turns | Starts with a simple Socratic prompt, then backs off after one or two confused responses |
| Student confusion handling | Confusion often led to another near-identical question | Confusion now triggers a stronger hint, then a direct explanation |
| Full-answer requests | Some explicit explanation requests still stayed in the question loop | Requests like “make me understand fully” now route to direct explanation |
| Backend app import | `uvicorn main:app` from the repo root failed because the backend package imports were not wired correctly | `backend.main` imports successfully from the repository root |
| Regression coverage | No backend-level test for mode switching | Added a backend service test covering Socratic → explain transition |

---

## What We Completed

### 1) Socratic Backoff Logic
- Added mode selection in `backend/services/chat_service.py`.
- The tutor now chooses between:
  - `socratic` for the first simple prompt,
  - `clarify` when the student seems unsure,
  - `explain` after repeated confusion or an explicit request for a full explanation.
- Added a guard to avoid the same example loop repeating indefinitely.

### 2) Backend Wiring for Frontend Use
- Updated the backend package to use package-relative imports.
- Verified the backend app can be imported from the repository root with `from backend.main import app`.
- This makes the backend easier to launch later through the frontend or with the correct Uvicorn module path.

### 3) Regression Testing
- Added `backend/tests/test_chat_service_modes.py`.
- The test confirms that a confused follow-up response shifts the tutor from Socratic questioning to direct explanation.
- Test result: passed.

---

## Verification

### Backend Import Check
- Verified the backend entrypoint imports successfully from the project root.
- Confirmed the FastAPI app object loads and exposes routes.

### Test Result
- `pytest backend/tests/test_chat_service_modes.py -q`
- Result: `1 passed`

---

## Notes For Next Step

- The frontend should call `POST /sessions/{session_id}/chat`.
- The backend now supports the interaction pattern needed for a smoother student experience.
- If needed next, the mode selection can be tuned further to make the explain backoff stricter or more gradual.

---

## Files Updated

- `backend/services/chat_service.py`
- `backend/main.py`
- `backend/routers/onboarding.py`
- `backend/routers/sessions.py`
- `backend/routers/chat.py`
- `backend/routers/pipeline.py`
- `backend/services/session_service.py`
- `backend/services/profile_service.py`
- `backend/repositories/session_repository.py`
- `backend/repositories/profile_repository.py`
- `backend/tests/test_chat_service_modes.py`


start with a simple Socratic prompt,
if the student is confused once or twice, switch to the direct explanation,
avoid repeating the same example loop,
and only keep asking if the student still seems uncertain.