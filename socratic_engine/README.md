Socratic Engine
===============

This is a minimal Socratic engine that calls the backend APIs to create profiles, start sessions, and post events.

Run (from the repo root):

```bash
# use the backend virtualenv python if available
python -m engine
# or set a custom backend URL:
BACKEND_URL=http://127.0.0.1:8000 python -m engine
```

The engine is intentionally lightweight and designed to run as a separate process; later you can containerize it.
