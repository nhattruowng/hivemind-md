from typing import Any
from uuid import uuid4

from app.agents.input_router_agent import InputRouterAgent
from app.orchestration.agent_runtime import AgentRuntime


class PlannerRuntimeService:
    def __init__(self, runtime: AgentRuntime | None = None) -> None:
        self.runtime = runtime or AgentRuntime()

    async def preview(self, *, message: str, user_id: str | None = None, category: str = "chat-auto", mode: str = "quick", auto_refresh: bool = True, page_context: str = "") -> dict[str, Any]:
        task_id = uuid4().hex
        timeline: list[dict[str, Any]] = []
        intent_run = await self.runtime.execute_registered_agent(
            "IntentClassifierAgent",
            input_data={"message": message, "page_context": page_context},
            user_id=user_id,
            task_id=task_id,
        )
        timeline.append(intent_run)
        route_result = await InputRouterAgent().execute(query=message, max_routes=5)
        route_data = route_result.get("data", {})
        timeline.append(
            {
                "agent_id": "",
                "agent": "InputRouterAgent",
                "category": "knowledge",
                "status": route_result.get("status", "success"),
                "message": route_result.get("message", ""),
                "data": route_data,
                "confidence": route_data.get("confidence"),
                "sources": [],
                "tool_calls": [],
                "risk_level": "low",
                "runtime_ms": route_result.get("runtime_ms", 0),
            }
        )
        plan_run = await self.runtime.execute_registered_agent(
            "PlannerAgent",
            input_data={
                "message": message,
                "route": route_data,
                "auto_refresh": auto_refresh,
                "category": category,
                "mode": mode,
            },
            user_id=user_id,
            task_id=task_id,
        )
        timeline.append(plan_run)
        router_run = await self.runtime.execute_registered_agent(
            "AgentRouterAgent",
            input_data={
                "message": message,
                "intent": intent_run.get("data", {}),
                "plan": plan_run.get("data", {}),
            },
            user_id=user_id,
            task_id=task_id,
        )
        timeline.append(router_run)
        routing = router_run.get("data", {})
        selected_agents = routing.get("selected_agents", []) if isinstance(routing, dict) else []
        return {
            "task_id": task_id,
            "intent": intent_run.get("data", {}),
            "route": route_data,
            "plan": plan_run.get("data", {}),
            "routing": routing,
            "agents_used": ["IntentClassifierAgent", "InputRouterAgent", "PlannerAgent", "AgentRouterAgent", *selected_agents],
            "confidence": intent_run.get("confidence"),
            "needs_approval": bool(plan_run.get("data", {}).get("approval_required")),
            "timeline": timeline,
        }
