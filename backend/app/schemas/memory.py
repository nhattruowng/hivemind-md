from typing import Literal

from pydantic import BaseModel, Field


MemoryType = Literal["preference", "project", "fact", "workflow", "skill", "correction", "temporary"]


class MemoryCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    memory_type: MemoryType = "fact"
    user_id: str | None = None
    source: str = "manual"
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    importance: int = Field(default=1, ge=1, le=5)
    expires_at: str | None = None


class MemoryRecord(BaseModel):
    id: str
    user_id: str
    memory_type: MemoryType
    content: str
    source: str | None = None
    confidence: float = 0.7
    importance: int = 1
    expires_at: str | None = None
    created_at: str
    updated_at: str
    archived_at: str | None = None
