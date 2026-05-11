import re
from typing import Any

from app.agents.base_agent import BaseAgent
from app.utils.text_utils import normalize_whitespace


ACTION_TERMS = (
    "delete",
    "remove",
    "drop",
    "truncate",
    "send",
    "email",
    "deploy",
    "apply",
    "write",
    "update database",
    "production",
    "xóa",
    "xoá",
    "gửi",
    "ghi db",
    "cập nhật production",
    "ap dung",
    "áp dụng",
)
DESTRUCTIVE_TERMS = ("delete", "remove", "drop", "truncate", "xóa", "xoá")
RESEARCH_TERMS = ("search", "crawl", "research", "tìm", "nghiên cứu", "tra cứu", "cập nhật", "refresh")
CODING_TERMS = ("code", "bug", "test", "api", "backend", "frontend", "lập trình", "sửa lỗi")


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"
    description = "Create a small execution plan from intent, route, risk, and available knowledge."

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        request = normalize_whitespace(str(kwargs.get("request", "")))
        route_data = kwargs.get("route_data") if isinstance(kwargs.get("route_data"), dict) else {}
        auto_refresh = bool(kwargs.get("auto_refresh", True))
        mode = str(kwargs.get("mode", "quick"))
        category = str(kwargs.get("category", "chat-auto"))
        workflow = str(kwargs.get("workflow", "chat"))

        intent = "knowledge_build" if workflow == "knowledge_build" else self._intent(request, route_data)
        risk_level, risk_reasons = self._risk(request, intent)
        approval_required = risk_level in {"high", "critical"}
        has_route = bool(route_data.get("supported"))
        needs_research = auto_refresh and (intent in {"research", "qa", "knowledge_build"} or not has_route)
        refresh_allowed = needs_research and not approval_required

        if workflow == "knowledge_build":
            steps = self._knowledge_build_steps(approval_required=approval_required)
        else:
            steps = self._steps(
                intent=intent,
                has_route=has_route,
                refresh_allowed=refresh_allowed,
                approval_required=approval_required,
            )
        plan = {
            "task_type": intent,
            "goal": request,
            "workflow": workflow,
            "mode": mode,
            "category": category,
            "execution_mode": "sequential",
            "risk_level": risk_level,
            "risk_reasons": risk_reasons,
            "approval_required": approval_required,
            "refresh_allowed": refresh_allowed,
            "route_required": has_route,
            "steps": steps,
        }
        return self.success("Generated execution plan.", plan)

    def _intent(self, request: str, route_data: dict[str, Any]) -> str:
        lowered = request.lower()
        if any(term in lowered for term in ACTION_TERMS):
            return "action"
        if any(term in lowered for term in CODING_TERMS):
            return "coding"
        if any(term in lowered for term in RESEARCH_TERMS):
            return "research"
        if self._looks_like_question(lowered):
            return "qa"
        if route_data.get("supported"):
            return "qa"
        return "general"

    def _risk(self, request: str, intent: str) -> tuple[str, list[str]]:
        lowered = request.lower()
        reasons: list[str] = []
        if any(term in lowered for term in DESTRUCTIVE_TERMS):
            reasons.append("Request appears to modify or delete data.")
        if "production" in lowered or "prod" in lowered or "database" in lowered or "db" in lowered:
            reasons.append("Request mentions production or database state.")
        if "email" in lowered or "gửi" in lowered or "send" in lowered:
            reasons.append("Request may contact an external party.")
        if reasons:
            return "high", reasons
        if intent == "action":
            return "medium", ["Request asks the agent to perform an action."]
        return "low", []

    def _steps(
        self,
        *,
        intent: str,
        has_route: bool,
        refresh_allowed: bool,
        approval_required: bool,
    ) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = [
            {
                "id": "step_1",
                "step": 1,
                "name": "Classify and route",
                "agent": "InputRouterAgent",
                "action": "classify_and_route",
                "input": {},
                "depends_on": [],
                "can_run_parallel": False,
                "risk_level": "low",
                "reason": "Classify the request and choose candidate knowledge folders.",
            }
        ]
        if approval_required:
            steps.append(
                {
                    "id": f"step_{len(steps) + 1}",
                    "step": len(steps) + 1,
                    "name": "Request approval",
                    "agent": "PolicyAgent",
                    "action": "request_human_approval",
                    "input": {},
                    "depends_on": [steps[-1]["id"]] if steps else [],
                    "can_run_parallel": False,
                    "risk_level": "high",
                    "reason": "High-risk actions must be approved before tool execution.",
                }
            )
        if has_route:
            steps.append(
                {
                    "id": f"step_{len(steps) + 1}",
                    "step": len(steps) + 1,
                    "name": "Retrieve and answer",
                    "agent": "AnswerAgent",
                    "action": "retrieve_and_answer",
                    "input": {},
                    "depends_on": [steps[-1]["id"]] if steps else [],
                    "can_run_parallel": False,
                    "risk_level": "low",
                    "reason": "Use routed knowledge and vector chunks as answer context.",
                }
            )
        if refresh_allowed:
            steps.append(
                {
                    "id": f"step_{len(steps) + 1}",
                    "step": len(steps) + 1,
                    "name": "Refresh local knowledge",
                    "agent": "AutoRefreshAgent",
                    "action": "refresh_local_knowledge_if_needed",
                    "input": {},
                    "depends_on": [steps[-1]["id"]] if steps else [],
                    "can_run_parallel": False,
                    "risk_level": "low",
                    "reason": "Local search/crawl is allowed when retrieved knowledge is insufficient.",
                }
            )
        if intent in {"qa", "research", "general", "coding"}:
            steps.append(
                {
                    "id": f"step_{len(steps) + 1}",
                    "step": len(steps) + 1,
                    "name": "Verify answer",
                    "agent": "VerifierAgent",
                    "action": "verify_grounding",
                    "input": {},
                    "depends_on": [steps[-1]["id"]] if steps else [],
                    "can_run_parallel": False,
                    "risk_level": "low",
                    "reason": "Check answer support, citations, missing points, and risk before final response.",
                }
            )
        steps.append(
            {
                "id": f"step_{len(steps) + 1}",
                "step": len(steps) + 1,
                "name": "Write session memory",
                "agent": "ChatMemoryAgent",
                "action": "write_session_memory",
                "input": {},
                "depends_on": [steps[-1]["id"]] if steps else [],
                "can_run_parallel": False,
                "risk_level": "low",
                "reason": "Persist the final turn and audit metadata.",
            }
        )
        return steps

    def _knowledge_build_steps(self, *, approval_required: bool) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        if approval_required:
            steps.append(
                {
                    "id": "step_1",
                    "step": 1,
                    "name": "Request approval",
                    "agent": "PolicyAgent",
                    "action": "request_human_approval",
                    "input": {},
                    "depends_on": [],
                    "can_run_parallel": False,
                    "risk_level": "high",
                    "reason": "High-risk build requests must be approved before execution.",
                }
            )
        for agent, action, reason in (
            ("SearchAgent", "search_sources", "Find candidate sources for the topic."),
            ("CrawlerAgent", "crawl_sources", "Fetch readable page content."),
            ("CleanerAgent", "clean_documents", "Remove boilerplate and noisy text."),
            ("ExtractorAgent", "extract_knowledge", "Extract summaries, concepts, key points, and risks."),
            ("CriticAgent", "score_sources", "Rate source quality before composing knowledge."),
            ("ComposerAgent", "compose_markdown", "Write grounded Markdown with metadata."),
            ("IndexerAgent", "index_markdown", "Store chunks in the vector index for later RAG."),
        ):
            steps.append(
                {
                    "id": f"step_{len(steps) + 1}",
                    "step": len(steps) + 1,
                    "name": action.replace("_", " ").title(),
                    "agent": agent,
                    "action": action,
                    "input": {},
                    "depends_on": [steps[-1]["id"]] if steps else [],
                    "can_run_parallel": False,
                    "risk_level": "low",
                    "reason": reason,
                }
            )
        return steps

    def _looks_like_question(self, lowered: str) -> bool:
        if "?" in lowered:
            return True
        return bool(re.search(r"\b(what|why|how|when|where|ai|là gì|vì sao|như thế nào|tại sao)\b", lowered))
