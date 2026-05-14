from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.agent_routes import _compact_log
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.chat_knowledge_service import ChatKnowledgeService


router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> dict[str, Any]:
    try:
        result = await ChatKnowledgeService().chat(
            payload.message,
            conversation_id=payload.conversation_id,
            auto_refresh=payload.auto_refresh,
            category=payload.category,
            mode=payload.mode,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    result["agent_logs"] = [_compact_log(log) for log in result.get("agent_logs", [])]
    return result
