from fastapi import APIRouter, HTTPException

from app.self_improvement.improvement_memory import ImprovementMemory
from app.self_improvement.prompt_version_service import PromptVersionService
from app.self_improvement.schemas import (
    AgentRunResponse,
    ReflectionLessonResponse,
    SelfImprovementSummary,
    WorkflowSuggestionResponse,
    PromptVersionResponse,
)
from app.self_improvement.score_service import ScoreService


router = APIRouter(prefix="/api/self-improvement", tags=["self-improvement"])


@router.get("/summary", response_model=SelfImprovementSummary)
async def get_summary() -> dict[str, object]:
    return ScoreService().get_summary()


@router.get("/runs", response_model=list[AgentRunResponse])
async def list_agent_runs(
    agent_name: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, object]]:
    return ScoreService().list_agent_runs(agent_name=agent_name, status=status, limit=limit)


@router.get("/lessons", response_model=list[ReflectionLessonResponse])
async def list_lessons(
    agent_name: str | None = None,
    lesson_type: str | None = None,
    status: str | None = None,
) -> list[dict[str, object]]:
    return ImprovementMemory().list_lessons(agent_name=agent_name, lesson_type=lesson_type, status=status)


@router.post("/lessons/{lesson_id}/archive", response_model=ReflectionLessonResponse)
async def archive_lesson(lesson_id: int) -> dict[str, object]:
    lesson = ImprovementMemory().archive_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    return lesson


@router.get("/prompt-versions", response_model=list[PromptVersionResponse])
async def list_prompt_versions(agent_name: str | None = None) -> list[dict[str, object]]:
    return PromptVersionService().list_prompt_versions(agent_name=agent_name)


@router.post("/prompt-versions/{version_id}/activate", response_model=PromptVersionResponse)
async def activate_prompt_version(version_id: int) -> dict[str, object]:
    version = PromptVersionService().activate_prompt_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Prompt version not found.")
    return version


@router.get("/workflow-suggestions", response_model=list[WorkflowSuggestionResponse])
async def list_workflow_suggestions(
    status: str | None = None,
    risk_level: str | None = None,
) -> list[dict[str, object]]:
    return ScoreService().list_workflow_suggestions(status=status, risk_level=risk_level)


@router.post("/workflow-suggestions/{suggestion_id}/reject", response_model=WorkflowSuggestionResponse)
async def reject_workflow_suggestion(suggestion_id: int) -> dict[str, object]:
    suggestion = ScoreService().update_workflow_suggestion_status(suggestion_id, "rejected")
    if not suggestion:
        raise HTTPException(status_code=404, detail="Workflow suggestion not found.")
    return suggestion


@router.post("/workflow-suggestions/{suggestion_id}/apply", response_model=WorkflowSuggestionResponse)
async def mark_workflow_suggestion_applied(suggestion_id: int) -> dict[str, object]:
    suggestion = ScoreService().update_workflow_suggestion_status(suggestion_id, "applied")
    if not suggestion:
        raise HTTPException(status_code=404, detail="Workflow suggestion not found.")
    return suggestion
