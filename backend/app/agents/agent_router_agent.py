from typing import Any

from app.agents.base_agent import BaseAgent
from app.registry.agent_registry import AgentRegistry


AGENT_ALIASES = {
    "InputRouterAgent": "ContextBuilderAgent",
    "AnswerAgent": "RAGAgent",
    "AutoRefreshAgent": "KnowledgeRefreshAgent",
    "ChatMemoryAgent": "MemoryAgent",
}
IMPLEMENTED_RUNTIME_AGENTS = {
    "IntentClassifierAgent",
    "PlannerAgent",
    "AgentRouterAgent",
    "VerifierAgent",
    "RAGAgent",
}
INTENT_FALLBACKS = {
    "chat": ["ContextBuilderAgent", "RAGAgent", "VerifierAgent", "MemoryAgent"],
    "research": ["SearchAgent", "CrawlerAgent", "ExtractorAgent", "CriticAgent", "ComposerAgent", "VerifierAgent"],
    "build_knowledge": ["SearchAgent", "CrawlerAgent", "CleanerAgent", "ExtractorAgent", "CriticAgent", "ComposerAgent", "IndexerAgent"],
    "code": ["CodeAgent", "ReviewAgent", "TestGeneratorAgent"],
    "debug": ["DebugAgent", "ReviewAgent", "TestGeneratorAgent"],
    "document": ["DocumentAgent", "CitationAgent", "VerifierAgent"],
    "workflow": ["WorkflowAgent", "DecisionAgent", "VerifierAgent"],
    "automation": ["WorkflowAgent", "PolicyAgent", "ApprovalAgent"],
    "settings": ["PolicyAgent", "SecurityAgent"],
    "unknown": ["PlannerAgent", "DecisionAgent", "VerifierAgent"],
}


class AgentRouterAgent(BaseAgent):
    name = "AgentRouterAgent"
    description = "Route planned steps to registered agents and mark runtime executability."

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry()

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        plan = kwargs.get("plan") if isinstance(kwargs.get("plan"), dict) else {}
        intent_data = kwargs.get("intent") if isinstance(kwargs.get("intent"), dict) else {}
        user_id = kwargs.get("user_id")
        intent = str(intent_data.get("intent") or plan.get("task_type") or "unknown")
        steps = plan.get("steps", []) if isinstance(plan.get("steps", []), list) else []
        assignments = self._assign_steps(steps, user_id=user_id)
        if not assignments:
            assignments = self._fallback_assignments(intent, user_id=user_id)
        else:
            assignments = self._ensure_intent_backbone(assignments, intent, user_id=user_id)
        selected_agents = self._unique([item["selected_agent"] for item in assignments if item.get("selected_agent")])
        return self.success(
            "Routed plan steps to registered agents.",
            {
                "intent": intent,
                "execution_mode": plan.get("execution_mode", "sequential"),
                "assignments": assignments,
                "selected_agents": selected_agents,
                "executable_agents": [item["selected_agent"] for item in assignments if item.get("executable")],
            },
            confidence=0.86 if assignments else 0.2,
        )

    def _assign_steps(self, steps: list[Any], *, user_id: str | None) -> list[dict[str, Any]]:
        assignments: list[dict[str, Any]] = []
        for index, raw_step in enumerate(steps, start=1):
            if not isinstance(raw_step, dict):
                continue
            requested = str(raw_step.get("agent") or "")
            selected_name = AGENT_ALIASES.get(requested, requested)
            agent = self.registry.get_agent_by_name_or_slug(selected_name, user_id=user_id)
            if not agent:
                continue
            assignments.append(self._assignment(raw_step, agent, requested_agent=requested, index=index))
        return assignments

    def _ensure_intent_backbone(
        self,
        assignments: list[dict[str, Any]],
        intent: str,
        *,
        user_id: str | None,
    ) -> list[dict[str, Any]]:
        existing = {item["selected_agent"] for item in assignments}
        for name in INTENT_FALLBACKS.get(intent, []):
            if name in existing:
                continue
            if intent in {"chat", "unknown"} and name not in {"RAGAgent", "VerifierAgent", "MemoryAgent"}:
                continue
            agent = self.registry.get_agent_by_name_or_slug(name, user_id=user_id)
            if not agent:
                continue
            step = {
                "id": f"backbone_{len(assignments) + 1}",
                "step": len(assignments) + 1,
                "name": agent["role"].replace("_", " ").title(),
                "agent": name,
                "action": agent["role"],
                "risk_level": agent["risk_level"],
            }
            assignments.append(self._assignment(step, agent, requested_agent=name, index=len(assignments) + 1))
            existing.add(name)
        return assignments

    def _fallback_assignments(self, intent: str, *, user_id: str | None) -> list[dict[str, Any]]:
        assignments: list[dict[str, Any]] = []
        for index, name in enumerate(INTENT_FALLBACKS.get(intent, INTENT_FALLBACKS["unknown"]), start=1):
            agent = self.registry.get_agent_by_name_or_slug(name, user_id=user_id)
            if not agent:
                continue
            step = {
                "id": f"fallback_{index}",
                "step": index,
                "name": agent["role"].replace("_", " ").title(),
                "agent": name,
                "action": agent["role"],
                "risk_level": agent["risk_level"],
            }
            assignments.append(self._assignment(step, agent, requested_agent=name, index=index))
        return assignments

    def _assignment(self, step: dict[str, Any], agent: dict[str, Any], *, requested_agent: str, index: int) -> dict[str, Any]:
        return {
            "step_id": str(step.get("id") or f"step_{index}"),
            "step_name": str(step.get("name") or step.get("action") or agent["name"]),
            "requested_agent": requested_agent,
            "selected_agent": agent["name"],
            "agent_id": agent["id"],
            "category": agent["category"],
            "role": agent["role"],
            "risk_level": max(str(step.get("risk_level") or "low"), agent["risk_level"], key=self._risk_rank),
            "allowed_tools": agent["allowed_tools"],
            "executable": agent["name"] in IMPLEMENTED_RUNTIME_AGENTS,
            "reason": f"Matched step '{requested_agent}' to registry agent '{agent['name']}'.",
        }

    def _risk_rank(self, value: str) -> int:
        return {"low": 0, "medium": 1, "high": 2}.get(value, 0)

    def _unique(self, values: list[str]) -> list[str]:
        output: list[str] = []
        seen: set[str] = set()
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            output.append(value)
        return output
