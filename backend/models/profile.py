from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class TopicHistoryItem(BaseModel):
    timestamp: str
    understanding: Optional[float]
    confidence: Optional[float]
    evidence: Optional[str]
    session_id: Optional[str]


class TopicCurrent(BaseModel):
    understanding: Optional[float]
    confidence: Optional[float]
    misconceptions: Optional[List[str]] = []
    last_studied: Optional[str]


class TopicRecord(BaseModel):
    history: Optional[List[TopicHistoryItem]] = []
    current: Optional[TopicCurrent]


class StudentProfile(BaseModel):
    student_id: str
    name: str
    grade: Optional[str]
    created_at: Optional[str]
    metadata: Optional[Dict] = {}
    topics: Optional[Dict[str, TopicRecord]] = Field(default_factory=dict)
