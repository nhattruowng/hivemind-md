from typing import Any

from pydantic import BaseModel, Field

from app.schemas.agent_schema import AgentLog, BuildMode


class DomainProfileResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str
    focus_areas: list[str]
    routing_keywords: list[str]
    worker_count: int
    max_parallel_workers: int
    use_llm_workers: int
    min_trust_score: float
    source_limits: dict[str, int]
    trusted_domains: list[str]
    main_model: str | None = None
    light_model: str | None = None


class AgentFrameworkRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    category: str = Field(default="general", min_length=1)
    mode: BuildMode = "standard"
    profile_id: str = "auto"


class AgentFrameworkResponse(BaseModel):
    status: str
    topic: str
    category: str
    profile: DomainProfileResponse
    files: list[str]
    map_file: str
    average_score: float
    agent_scores: dict[str, float]
    stages: dict[str, Any]
    agent_logs: list[AgentLog]
