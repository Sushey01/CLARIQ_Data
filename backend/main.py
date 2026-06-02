from fastapi import FastAPI
from routers import onboarding

app = FastAPI(title="clariq Backend")


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(onboarding.router)
