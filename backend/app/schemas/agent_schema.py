from typing import Any, Literal

from pydantic import BaseModel, Field


BuildMode = Literal["quick", "standard", "deep"]


class BuildKnowledgeRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    mode: BuildMode = "standard"
    category: str = Field(default="general", min_length=1)


class AgentLog(BaseModel):
    agent: str
    status: str
    message: str
    stage: str | None = None
    score: float | None = None
    runtime_ms: int | None = None
    started_at: str | None = None
    ended_at: str | None = None
    input_count: int | None = None
    output_count: int | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class BuildKnowledgeResponse(BaseModel):
    status: str
    markdown_file: str
    agent_logs: list[AgentLog]
