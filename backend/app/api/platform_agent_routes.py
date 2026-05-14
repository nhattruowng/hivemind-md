from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.orchestration.agent_runtime import AgentRuntime
from app.registry.agent_registry import AgentRegistry
from app.schemas.agents import AgentCreateRequest, AgentRecord, AgentRuntimeResponse, AgentTestRequest


router = APIRouter(prefix="/api/agents", tags=["agent-registry"])


@router.get("", response_model=list[AgentRecord])
async def list_agents(user_id: str | None = None, include_inactive: bool = False) -> list[dict[str, object]]:
    return AgentRegistry().list_agents(user_id=user_id, include_inactive=include_inactive)


@router.post("", response_model=AgentRecord)
async def create_agent(payload: AgentCreateRequest) -> dict[str, object]:
    try:
        return AgentRegistry().create_agent(
            name=payload.name,
            category=payload.category,
            description=payload.description,
            role=payload.role,
            goal=payload.goal,
            system_prompt=payload.system_prompt,
            user_id=payload.user_id,
            default_model=payload.default_model,
            temperature=payload.temperature,
            risk_level=payload.risk_level,
            is_active=payload.is_active,
            allowed_tools=payload.allowed_tools,
            input_schema=payload.input_schema or None,
            output_schema=payload.output_schema or None,
            evaluation_metrics=payload.evaluation_metrics or None,
            config=payload.config,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{agent_id}/test", response_model=AgentRuntimeResponse)
async def test_agent(agent_id: str, payload: AgentTestRequest) -> dict[str, object]:
    registry = AgentRegistry()
    agent = registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found.")
    task_id = uuid4().hex
    result = await AgentRuntime(registry=registry).execute_registered_agent(
        agent_id,
        input_data=payload.input,
        context=payload.context,
        config=payload.config,
        user_id=payload.user_id,
        task_id=task_id,
    )
    return {
        "task_id": task_id,
        "agent": agent,
        "result": result,
        "timeline": [result],
    }
