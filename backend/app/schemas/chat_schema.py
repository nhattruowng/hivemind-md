from typing import Any

from pydantic import BaseModel, Field

from app.schemas.agent_schema import AgentLog, BuildMode


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: str | None = None
    auto_refresh: bool = True
    category: str = Field(default="chat-auto", min_length=1)
    mode: BuildMode = "quick"


class ChatResponse(BaseModel):
    answer: str
    related_files: list[str]
    sources: list[str]
    conversation_id: str
    chat_file: str
    auto_refreshed: bool = False
    updated_files: list[str] = Field(default_factory=list)
    confidence: float | None = None
    grounding_score: float | None = None
    citations: list[dict[str, Any]] = Field(default_factory=list)
    verification: dict[str, Any] = Field(default_factory=dict)
    plan: dict[str, Any] = Field(default_factory=dict)
    token_estimate: int | None = None
    route: dict[str, Any] = Field(default_factory=dict)
    active_agents: int = 0
    agent_roles: list[dict[str, str]] = Field(default_factory=list)
    agent_logs: list[AgentLog] = Field(default_factory=list)
