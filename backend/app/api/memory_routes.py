from fastapi import APIRouter, HTTPException

from app.memory.memory_service import MemoryService
from app.schemas.memory import MemoryCreateRequest, MemoryRecord


router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.get("", response_model=list[MemoryRecord])
async def list_memory(
    user_id: str | None = None,
    memory_type: str | None = None,
    include_archived: bool = False,
) -> list[dict[str, object]]:
    return MemoryService().list_memories(
        user_id=user_id,
        memory_type=memory_type,
        include_archived=include_archived,
    )


@router.post("", response_model=MemoryRecord)
async def create_memory(payload: MemoryCreateRequest) -> dict[str, object]:
    try:
        return MemoryService().create_memory(
            content=payload.content,
            memory_type=payload.memory_type,
            user_id=payload.user_id,
            source=payload.source,
            confidence=payload.confidence,
            importance=payload.importance,
            expires_at=payload.expires_at,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
