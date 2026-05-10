from fastapi import APIRouter, HTTPException

from app.schemas.knowledge_schema import (
    KnowledgeDeleteRequest,
    KnowledgeDeleteResponse,
    KnowledgeCleanupRequest,
    KnowledgeCleanupResponse,
    KnowledgeItem,
    KnowledgeMapResponse,
    KnowledgeReadResponse,
    KnowledgeRefreshRequest,
    KnowledgeRefreshResponse,
)
from app.api.agent_routes import _compact_log
from app.services.knowledge_cleanup_service import KnowledgeCleanupService
from app.services.knowledge_map_service import KnowledgeMapService
from app.services.knowledge_refresh_service import KnowledgeRefreshService
from app.services.markdown_service import MarkdownService
from app.services.metadata_service import MetadataService
from app.services.approval_policy import ApprovalPolicy
from app.services.vector_service import VectorService


router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeItem])
async def list_knowledge() -> list[dict[str, object]]:
    return MetadataService().list_items()


@router.get("/read", response_model=KnowledgeReadResponse)
async def read_knowledge(file_path: str) -> dict[str, str]:
    service = MarkdownService()
    path = service.resolve(file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Knowledge file not found.")
    return {"content": path.read_text(encoding="utf-8")}


@router.get("/map", response_model=KnowledgeMapResponse)
async def read_knowledge_map() -> dict[str, str]:
    service = KnowledgeMapService()
    data = service.rebuild()
    return {"map_file": data["map_file"], "content": data["content"]}


@router.post("/refresh", response_model=KnowledgeRefreshResponse)
async def refresh_knowledge(payload: KnowledgeRefreshRequest) -> dict[str, object]:
    result = await KnowledgeRefreshService().refresh(
        topic=payload.topic,
        category=payload.category,
        mode=payload.mode,
    )
    return {
        "status": "success",
        "topic": result["topic"],
        "category": result["category"],
        "files": result["files"],
        "map_file": result["map_file"],
        "agent_logs": [_compact_log(log) for log in result["agent_logs"]],
    }


@router.post("/cleanup", response_model=KnowledgeCleanupResponse)
async def cleanup_knowledge(payload: KnowledgeCleanupRequest) -> dict[str, object]:
    approval = ApprovalPolicy().evaluate("cleanup_knowledge", approved=payload.approved)
    if not payload.dry_run and not approval.allowed:
        raise HTTPException(status_code=428, detail=approval.to_dict())
    result = await KnowledgeCleanupService().cleanup(dry_run=payload.dry_run, min_trust=payload.min_trust)
    return {
        **result,
        "agent_logs": [_compact_log(log) for log in result.get("agent_logs", [])],
    }


@router.delete("/delete", response_model=KnowledgeDeleteResponse)
async def delete_knowledge(payload: KnowledgeDeleteRequest) -> dict[str, str]:
    approval = ApprovalPolicy().evaluate("delete_knowledge", approved=payload.approved)
    if not approval.allowed:
        raise HTTPException(status_code=428, detail=approval.to_dict())
    markdown = MarkdownService()
    path = markdown.resolve(payload.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Knowledge file not found.")
    path.unlink()
    MetadataService().delete_item(payload.file_path)
    VectorService().delete_file(payload.file_path)
    KnowledgeMapService().rebuild()
    return {"status": "success", "deleted": payload.file_path}
