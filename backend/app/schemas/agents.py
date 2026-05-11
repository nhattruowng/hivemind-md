from typing import Any, Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]


class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    category: str = "custom"
    description: str = ""
    role: str = Field(default="custom", min_length=2)
    goal: str = ""
    system_prompt: str = ""
    user_id: str | None = None
    default_model: str = "ollama"
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    risk_level: RiskLevel = "low"
    is_active: bool = True
    allowed_tools: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    evaluation_metrics: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)


class AgentRecord(BaseModel):
    id: str
    user_id: str | None = None
    name: str
    slug: str
    category: str = "custom"
    description: str | None = ""
    role: str
    goal: str | None = ""
    system_prompt: str | None = ""
    default_model: str | None = "ollama"
    temperature: float = 0.2
    risk_level: RiskLevel = "low"
    allowed_tools: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    evaluation_metrics: list[str] = Field(default_factory=list)
    is_system: bool = False
    is_active: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class PlanPreviewRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_id: str | None = None
    category: str = "chat-auto"
    mode: Literal["quick", "standard", "deep"] = "quick"
    auto_refresh: bool = True
    page_context: str = ""


class PlanPreviewResponse(BaseModel):
    task_id: str | None = None
    intent: dict[str, Any]
    route: dict[str, Any]
    plan: dict[str, Any]
    routing: dict[str, Any] = Field(default_factory=dict)
    agents_used: list[str]
    confidence: float | None = None
    needs_approval: bool = False
    timeline: list[dict[str, Any]] = Field(default_factory=list)


class AgentTestRequest(BaseModel):
    input: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)
    user_id: str | None = None


class AgentRuntimeResponse(BaseModel):
    task_id: str
    agent: dict[str, Any]
    result: dict[str, Any]
    timeline: list[dict[str, Any]]
