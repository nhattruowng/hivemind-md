from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.agent_routes import _compact_log
from app.schemas.agent_framework_schema import (
    AgentFrameworkRequest,
    AgentFrameworkResponse,
    DomainProfileResponse,
)
from app.services.agent_framework_service import AgentFrameworkService
from app.services.domain_profile_service import DomainProfileService


router = APIRouter(prefix="/api/agent-framework", tags=["agent-framework"])


@router.get("/profiles", response_model=list[DomainProfileResponse])
async def list_domain_profiles() -> list[dict[str, Any]]:
    return DomainProfileService().list_profiles()


@router.post("/run", response_model=AgentFrameworkResponse)
async def run_agent_framework(payload: AgentFrameworkRequest) -> dict[str, Any]:
    result = await AgentFrameworkService().run(
        topic=payload.topic,
        category=payload.category,
        mode=payload.mode,
        profile_id=payload.profile_id,
    )
    if not result.get("files"):
        raise HTTPException(status_code=500, detail="Agent framework did not produce any Markdown files.")

    return {
        "status": "success",
        "topic": result["topic"],
        "category": result["category"],
        "profile": result["profile"],
        "files": result["files"],
        "map_file": result["map_file"],
        "average_score": result["average_score"],
        "agent_scores": result["agent_scores"],
        "stages": result["stages"],
        "agent_logs": [_compact_log(log) for log in result["agent_logs"]],
    }
