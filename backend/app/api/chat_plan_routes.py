from typing import Any

from fastapi import APIRouter, HTTPException

from app.orchestration.planner_service import PlannerRuntimeService
from app.schemas.agents import PlanPreviewRequest, PlanPreviewResponse


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/plan-preview", response_model=PlanPreviewResponse)
async def plan_preview(payload: PlanPreviewRequest) -> dict[str, Any]:
    try:
        return await PlannerRuntimeService().preview(
            message=payload.message,
            user_id=payload.user_id,
            category=payload.category,
            mode=payload.mode,
            auto_refresh=payload.auto_refresh,
            page_context=payload.page_context,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
