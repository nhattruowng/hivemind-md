import json
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from app.agents.agent_router_agent import AgentRouterAgent
from app.agents.answer_agent import AnswerAgent
from app.agents.intent_classifier_agent import IntentClassifierAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.verifier_agent import VerifierAgent
from app.registry.agent_registry import AgentRegistry
from app.self_improvement.score_service import ScoreService
from app.utils.text_utils import compact_preview


class AgentRuntime:
    def __init__(self, registry: AgentRegistry | None = None, score_service: ScoreService | None = None) -> None:
        self.registry = registry or AgentRegistry()
        self.score_service = score_service or ScoreService()

    async def execute_registered_agent(
        self,
        agent_ref: str,
        *,
        input_data: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
        user_id: str | None = None,
        task_id: str = "runtime-preview",
        record_run: bool = True,
    ) -> dict[str, Any]:
        input_data = input_data or {}
        context = context or {}
        config = config or {}
        agent_record = self.registry.get_agent_by_name_or_slug(agent_ref, user_id=user_id)
        if not agent_record:
            return self._runtime_result(
                agent={"name": agent_ref, "id": "", "category": "unknown", "risk_level": "low"},
                status="failed",
                message="Agent is not registered or inactive.",
                data={},
                started=perf_counter(),
                task_id=task_id,
                input_data=input_data,
                record_run=record_run,
            )

        started = perf_counter()
        raw_result = await self._execute_known_agent(agent_record, input_data=input_data, context=context, config=config, user_id=user_id)
        runtime_result = self._runtime_result(
            agent=agent_record,
            status=str(raw_result.get("status", "failed")),
            message=str(raw_result.get("message", "")),
            data=raw_result.get("data", {}) if isinstance(raw_result.get("data", {}), dict) else {},
            started=started,
            confidence=raw_result.get("confidence"),
            sources=raw_result.get("sources", []),
            tool_calls=raw_result.get("tool_calls", []),
            task_id=task_id,
            input_data=input_data,
            record_run=record_run,
        )
        return runtime_result

    async def _execute_known_agent(
        self,
        agent_record: dict[str, Any],
        *,
        input_data: dict[str, Any],
        context: dict[str, Any],
        config: dict[str, Any],
        user_id: str | None,
    ) -> dict[str, Any]:
        name = str(agent_record.get("name", ""))
        message = str(input_data.get("message") or input_data.get("request") or input_data.get("question") or "")
        if name == "IntentClassifierAgent":
            return await IntentClassifierAgent().execute(message=message, page_context=input_data.get("page_context", ""))
        if name == "PlannerAgent":
            return await PlannerAgent().execute(
                request=message,
                route_data=input_data.get("route", {}),
                auto_refresh=bool(input_data.get("auto_refresh", True)),
                category=str(input_data.get("category", "chat-auto")),
                mode=str(input_data.get("mode", "quick")),
                workflow=str(input_data.get("workflow", "chat")),
            )
        if name == "AgentRouterAgent":
            return await AgentRouterAgent(registry=self.registry).execute(
                request=message,
                intent=input_data.get("intent", {}),
                plan=input_data.get("plan", {}),
                user_id=user_id,
            )
        if name == "VerifierAgent":
            return await VerifierAgent().execute(
                question=str(input_data.get("question") or message),
                answer=str(input_data.get("answer") or ""),
                retrieval=input_data.get("retrieval", []),
                citations=input_data.get("citations", []),
                sources=input_data.get("sources", []),
                confidence=input_data.get("confidence", 0.0),
                needs_refresh=input_data.get("needs_refresh", False),
            )
        if name == "RAGAgent":
            return await AnswerAgent().execute(
                question=str(input_data.get("question") or message),
                route_paths=input_data.get("route_paths", []),
                route_context=input_data.get("route_context", ""),
            )
        return {
            "agent": name,
            "status": "skipped",
            "message": "Agent is registered but does not have a runtime adapter yet.",
            "data": {
                "registered": True,
                "category": agent_record.get("category", ""),
                "role": agent_record.get("role", ""),
                "allowed_tools": agent_record.get("allowed_tools", []),
                "input_preview": compact_preview(json.dumps(input_data, ensure_ascii=True, default=str), 400),
            },
            "confidence": 0.0,
            "sources": [],
            "tool_calls": [],
            "risk_level": agent_record.get("risk_level", "low"),
        }

    def _runtime_result(
        self,
        *,
        agent: dict[str, Any],
        status: str,
        message: str,
        data: dict[str, Any],
        started: float,
        confidence: Any = None,
        sources: list[Any] | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
        task_id: str,
        input_data: dict[str, Any],
        record_run: bool,
    ) -> dict[str, Any]:
        runtime_ms = int((perf_counter() - started) * 1000)
        output = {
            "agent_id": agent.get("id", ""),
            "agent": agent.get("name", "Agent"),
            "category": agent.get("category", "unknown"),
            "status": status,
            "message": message,
            "data": data,
            "confidence": confidence,
            "sources": sources or [],
            "tool_calls": tool_calls or [],
            "risk_level": agent.get("risk_level", "low"),
            "runtime_ms": runtime_ms,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        if record_run:
            self._record_runtime_run(task_id=task_id, agent_name=str(output["agent"]), input_data=input_data, output=output, runtime_ms=runtime_ms)
        return output

    def _record_runtime_run(
        self,
        *,
        task_id: str,
        agent_name: str,
        input_data: dict[str, Any],
        output: dict[str, Any],
        runtime_ms: int,
    ) -> None:
        try:
            self.score_service.record_agent_run(
                task_id=task_id,
                task="Registered agent runtime execution",
                agent_name=agent_name,
                input=json.dumps(input_data, ensure_ascii=True, default=str)[:12000],
                output=json.dumps(output, ensure_ascii=True, default=str)[:12000],
                status="success" if output.get("status") in {"success", "skipped"} else "failed",
                runtime_ms=runtime_ms,
            )
        except Exception:
            return
