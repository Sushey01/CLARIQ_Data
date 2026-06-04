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
    misconceptions: Optional[List[str]] = Field(default_factory=list)
    last_studied: Optional[str]


class TopicRecord(BaseModel):
    history: Optional[List[TopicHistoryItem]] = Field(default_factory=list)
    current: Optional[TopicCurrent]


class StudentProfile(BaseModel):
    student_id: Optional[str] = None
    name: str
    grade: Optional[str]
    created_at: Optional[str] = None
    metadata: Optional[Dict] = Field(default_factory=dict)
    topics: Optional[Dict[str, TopicRecord]] = Field(default_factory=dict)


class StudentProfileUpdate(BaseModel):
    student_id: Optional[str] = None
    name: Optional[str] = None
    grade: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Optional[Dict] = Field(default_factory=dict)
    topics: Optional[Dict[str, TopicRecord]] = Field(default_factory=dict)



