from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class SessionEvent(BaseModel):
    timestamp: str
    role: str
    content: str
    metadata: Optional[Dict] = Field(default_factory=dict)


class Session(BaseModel):
    session_id: str
    student_id: str
    topic: Optional[str]
    started_at: str
    events: List[SessionEvent] = Field(default_factory=list)
    status: Optional[str] = "active"
