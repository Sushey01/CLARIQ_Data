from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from .routers import onboarding, sessions, chat, pipeline
except ImportError:  # pragma: no cover - allows direct script execution in backend/
    from routers import onboarding, sessions, chat, pipeline

app = FastAPI(title="clariq Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(onboarding.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(pipeline.router)
