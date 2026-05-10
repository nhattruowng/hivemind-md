from typing import Literal

from pydantic import BaseModel, Field


RunStatus = Literal["success", "failed"]
LessonType = Literal["prompt", "workflow", "tool", "error", "success", "failed"]
LessonStatus = Literal["active", "archived"]
RiskLevel = Literal["low", "medium", "high"]
SuggestionStatus = Literal["pending", "applied", "rejected"]


class AgentRunCreate(BaseModel):
    task_id: str
    task: str
    agent_name: str
    input: str | None = None
    output: str | None = None
    score: float | None = None
    status: RunStatus
    error_message: str | None = None
    runtime_ms: int | None = None


class AgentRunResponse(AgentRunCreate):
    id: int
    created_at: str


class EvaluationResult(BaseModel):
    score: float = Field(default=0, ge=0, le=60)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_parts: list[str] = Field(default_factory=list)
    hallucination_risk: RiskLevel = "medium"
    improvement_suggestions: list[str] = Field(default_factory=list)
    should_reflect: bool = True


class ReflectionLessonCreate(BaseModel):
    title: str
    lesson_type: LessonType = "prompt"
    agent_name: str | None = None
    task_id: str | None = None
    content: str
    status: LessonStatus = "active"


class ReflectionLessonResponse(ReflectionLessonCreate):
    id: int
    created_at: str
    updated_at: str


class PromptVersionCreate(BaseModel):
    agent_name: str
    prompt: str
    risk_level: RiskLevel = "low"
    change_reason: str | None = None
    score: float | None = None


class PromptVersionResponse(PromptVersionCreate):
    id: int
    version: str
    is_active: int = 0
    created_at: str


class WorkflowSuggestionCreate(BaseModel):
    task_id: str
    suggestion: str
    expected_benefit: str | None = None
    risk_level: RiskLevel = "medium"
    status: SuggestionStatus = "pending"


class WorkflowSuggestionResponse(WorkflowSuggestionCreate):
    id: int
    created_at: str
    updated_at: str


class SelfImprovementSummary(BaseModel):
    total_runs: int = 0
    average_score: float = 0
    success_rate: float = 0
    total_lessons: int = 0
    total_prompt_versions: int = 0
    pending_workflow_suggestions: int = 0


class ApplyPromptVersionRequest(BaseModel):
    confirm: bool = True


class RejectWorkflowSuggestionRequest(BaseModel):
    reason: str | None = None
