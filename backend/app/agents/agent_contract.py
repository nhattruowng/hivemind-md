from typing import Any, Literal

from pydantic import BaseModel, Field


AgentStatus = Literal["success", "failed", "needs_approval", "skipped"]
RiskLevel = Literal["low", "medium", "high"]


class AgentContext(BaseModel):
    user_profile: dict[str, Any] = Field(default_factory=dict)
    memories: list[dict[str, Any]] = Field(default_factory=list)
    knowledge_routes: list[dict[str, Any]] = Field(default_factory=list)
    permissions: dict[str, Any] = Field(default_factory=dict)


class AgentEnvelope(BaseModel):
    task_id: str
    user_id: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    context: AgentContext = Field(default_factory=AgentContext)
    config: dict[str, Any] = Field(default_factory=dict)


class ToolCallRecord(BaseModel):
    tool_name: str
    status: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    runtime_ms: int = 0


class AgentResult(BaseModel):
    agent: str
    status: AgentStatus
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    confidence: float | None = None
    sources: list[Any] = Field(default_factory=list)
    tool_calls: list[ToolCallRecord | dict[str, Any]] = Field(default_factory=list)
    risk_level: RiskLevel = "low"
    runtime_ms: int = 0


def normalize_agent_result(raw: dict[str, Any]) -> dict[str, Any]:
    return AgentResult(
        agent=str(raw.get("agent", "Agent")),
        status=raw.get("status", "failed"),
        message=str(raw.get("message", "")),
        data=raw.get("data", {}) if isinstance(raw.get("data", {}), dict) else {},
        confidence=raw.get("confidence"),
        sources=raw.get("sources", []) if isinstance(raw.get("sources", []), list) else [],
        tool_calls=raw.get("tool_calls", []) if isinstance(raw.get("tool_calls", []), list) else [],
        risk_level=raw.get("risk_level", "low"),
        runtime_ms=int(raw.get("runtime_ms", 0) or 0),
    ).model_dump()
