from typing import Any

from fastapi import APIRouter, HTTPException

from app.agents.orchestrator_agent import OrchestratorAgent
from app.schemas.agent_schema import BuildKnowledgeRequest, BuildKnowledgeResponse


router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/build-knowledge", response_model=BuildKnowledgeResponse)
async def build_knowledge(payload: BuildKnowledgeRequest) -> dict[str, Any]:
    orchestrator = OrchestratorAgent()
    result = await orchestrator.execute(
        topic=payload.topic,
        mode=payload.mode,
        category=payload.category,
    )
    if result.get("status") != "success":
        raise HTTPException(status_code=500, detail=result.get("message", "Knowledge build failed."))

    data = result.get("data", {})
    return {
        "status": "success",
        "markdown_file": data.get("markdown_file", ""),
        "agent_logs": [_compact_log(log) for log in data.get("agent_logs", [])],
    }


def _compact_log(log: dict[str, Any]) -> dict[str, Any]:
    data = dict(log.get("data", {}))
    for key in ("documents", "cleaned_documents", "extracted", "content"):
        if key in data:
            value = data[key]
            data[f"{key}_count"] = len(value) if isinstance(value, list) else 1
            data.pop(key, None)
    if "sources" in data and isinstance(data["sources"], list):
        data["sources"] = data["sources"][:10]
    return {
        "agent": log.get("agent", "unknown"),
        "status": log.get("status", "unknown"),
        "message": log.get("message", ""),
        "stage": log.get("stage"),
        "score": log.get("score"),
        "runtime_ms": log.get("runtime_ms"),
        "started_at": log.get("started_at"),
        "ended_at": log.get("ended_at"),
        "input_count": log.get("input_count"),
        "output_count": log.get("output_count"),
        "data": data,
    }
