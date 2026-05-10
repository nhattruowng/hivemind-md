from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from app.agents.answer_agent import AnswerAgent
from app.agents.input_router_agent import InputRouterAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.verifier_agent import VerifierAgent
from app.config import Settings, get_settings
from app.services.chat_history_service import ChatHistoryService
from app.services.knowledge_refresh_service import KnowledgeRefreshService
from app.utils.text_utils import compact_preview, estimate_tokens, normalize_whitespace


class ChatKnowledgeService:
    def __init__(
        self,
        settings: Settings | None = None,
        answer_agent: AnswerAgent | None = None,
        router_agent: InputRouterAgent | None = None,
        planner_agent: PlannerAgent | None = None,
        verifier_agent: VerifierAgent | None = None,
        refresh_service: KnowledgeRefreshService | None = None,
        history_service: ChatHistoryService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.answer_agent = answer_agent or AnswerAgent(settings=self.settings)
        self.router_agent = router_agent or InputRouterAgent(settings=self.settings)
        self.planner_agent = planner_agent or PlannerAgent()
        self.verifier_agent = verifier_agent or VerifierAgent()
        self.refresh_service = refresh_service or KnowledgeRefreshService(settings=self.settings)
        self.history_service = history_service or ChatHistoryService(self.settings)

    async def chat(
        self,
        message: str,
        *,
        conversation_id: str | None = None,
        auto_refresh: bool = True,
        category: str = "chat-auto",
        mode: str = "quick",
    ) -> dict[str, Any]:
        logs: list[dict[str, Any]] = []
        question = normalize_whitespace(message)
        original_tokens = estimate_tokens(message)
        normalized_tokens = estimate_tokens(question)
        logs.append(
            self._log(
                "ChatInputAgent",
                "input",
                "Normalized user input and estimated token budget.",
                score=1.0,
                input_count=original_tokens,
                output_count=normalized_tokens,
                data={
                    "original_chars": len(message),
                    "normalized_chars": len(question),
                    "token_saving": max(0, original_tokens - normalized_tokens),
                    "query": question,
                },
            )
        )

        route_started = perf_counter()
        route_result = await self.router_agent.execute(query=question, max_routes=5)
        route_data = route_result.get("data", {})
        route_paths = self._selected_route_paths(route_data)
        effective_category = self._effective_category(category, route_data)
        logs.append(
            self._log(
                "InputRouterAgent",
                "route",
                route_result.get("message", "Routed input to supported knowledge folders."),
                started=route_started,
                score=float(route_data.get("confidence", 0.0) or 0.0),
                input_count=1,
                output_count=len(route_paths),
                data=route_data,
            )
        )

        plan_started = perf_counter()
        plan_result = await self.planner_agent.execute(
            request=question,
            route_data=route_data,
            auto_refresh=auto_refresh,
            category=effective_category,
            mode=mode,
        )
        plan_data = plan_result.get("data", {})
        logs.append(
            self._log(
                "PlannerAgent",
                "plan",
                plan_result.get("message", "Generated execution plan."),
                started=plan_started,
                score=self._plan_score(plan_data),
                input_count=1,
                output_count=len(plan_data.get("steps", []) or []),
                data=plan_data,
            )
        )

        first_answer = await self._run_answer_agent(question, route_data=route_data)
        logs.append(first_answer["log"])
        answer_data = first_answer["data"]
        auto_refreshed = False
        updated_files: list[str] = []
        refresh_result: dict[str, Any] | None = None

        if auto_refresh and answer_data.get("needs_refresh") and plan_data.get("refresh_allowed", True):
            refresh_started = perf_counter()
            refresh_result = await self.refresh_service.refresh(topic=question, category=effective_category, mode=mode)
            updated_files = list(refresh_result.get("files", []))
            auto_refreshed = True
            logs.append(
                self._log(
                    "AutoRefreshAgent",
                    "refresh",
                    f"Knowledge gap detected, refreshed {len(updated_files)} Markdown shard(s).",
                    started=refresh_started,
                    score=0.85 if updated_files else 0.45,
                    input_count=1,
                    output_count=len(updated_files),
                    data={
                        "topic": question,
                        "category": refresh_result.get("category", effective_category),
                        "route": route_data,
                        "mode": mode,
                        "files": updated_files,
                        "map_file": refresh_result.get("map_file", ""),
                    },
                )
            )
            logs.extend(self._stage_refresh_logs(refresh_result.get("agent_logs", [])))

            second_answer = await self._run_answer_agent(question, stage="answer_after_refresh", route_data=route_data)
            logs.append(second_answer["log"])
            answer_data = second_answer["data"]

        verification = await self._run_verifier_agent(question, answer_data)
        logs.append(verification["log"])
        verification_data = verification["data"]
        answer_data["verification"] = verification_data
        answer_data["confidence"] = self._verified_confidence(
            answer_data.get("confidence", 0.0),
            verification_data.get("confidence", 0.0),
        )

        history_started = perf_counter()
        history = self.history_service.append_turn(
            question=question,
            answer=str(answer_data.get("answer", "")),
            conversation_id=conversation_id,
            related_files=list(answer_data.get("related_files", [])),
            sources=list(answer_data.get("sources", [])),
            auto_refreshed=auto_refreshed,
            updated_files=updated_files,
        )
        logs.append(
            self._log(
                "ChatMemoryAgent",
                "memory",
                "Saved chat turn as Markdown history.",
                started=history_started,
                score=1.0,
                input_count=1,
                output_count=1,
                data=history,
            )
        )

        roles = self._agent_roles(logs)
        return {
            "answer": answer_data.get("answer", ""),
            "related_files": answer_data.get("related_files", []),
            "sources": answer_data.get("sources", []),
            "conversation_id": history["conversation_id"],
            "chat_file": history["chat_file"],
            "auto_refreshed": auto_refreshed,
            "updated_files": updated_files,
            "confidence": answer_data.get("confidence", 0.0),
            "grounding_score": answer_data.get("grounding_score", verification_data.get("grounding_score", 0.0)),
            "citations": answer_data.get("citations", []),
            "verification": verification_data,
            "plan": plan_data,
            "token_estimate": answer_data.get("token_estimate", normalized_tokens),
            "route": route_data,
            "agent_roles": roles,
            "active_agents": len(roles),
            "agent_logs": logs,
        }

    async def _run_answer_agent(
        self,
        question: str,
        stage: str = "answer",
        route_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        started = perf_counter()
        routes = (route_data or {}).get("top_routes", [])
        route_paths = self._selected_route_paths(route_data or {})
        result = await self.answer_agent.execute(
            question=question,
            route_paths=route_paths,
            route_context=(route_data or {}).get("route_context", ""),
        )
        data = result.get("data", {})
        confidence = data.get("confidence")
        score = float(confidence) if isinstance(confidence, (int, float)) else None
        return {
            "data": data,
            "log": self._log(
                "AnswerAgent",
                stage,
                result.get("message", "Answered from retrieved knowledge."),
                started=started,
                score=score,
                input_count=estimate_tokens(question),
                output_count=len(str(data.get("answer", "")).split()),
                data={
                    "confidence": data.get("confidence", 0.0),
                    "needs_refresh": data.get("needs_refresh", False),
                    "match_count": data.get("match_count", 0),
                    "used_chunk_count": data.get("used_chunk_count", 0),
                    "route_paths": data.get("route_paths", route_paths),
                    "primary_folder": (route_data or {}).get("primary_folder", ""),
                    "primary_category": (route_data or {}).get("primary_category", ""),
                    "related_files": data.get("related_files", []),
                    "sources": data.get("sources", [])[:10],
                    "retrieval": data.get("retrieval", []),
                    "citations": data.get("citations", []),
                    "grounding_score": data.get("grounding_score", 0.0),
                    "answer_preview": compact_preview(str(data.get("answer", "")), 360),
                },
            ),
        }

    async def _run_verifier_agent(self, question: str, answer_data: dict[str, Any]) -> dict[str, Any]:
        started = perf_counter()
        result = await self.verifier_agent.execute(
            question=question,
            answer=answer_data.get("answer", ""),
            retrieval=answer_data.get("retrieval", []),
            citations=answer_data.get("citations", []),
            sources=answer_data.get("sources", []),
            confidence=answer_data.get("confidence", 0.0),
            needs_refresh=answer_data.get("needs_refresh", False),
        )
        data = result.get("data", {})
        score = data.get("grounding_score")
        return {
            "data": data,
            "log": self._log(
                "VerifierAgent",
                "verify",
                result.get("message", "Verified answer grounding."),
                started=started,
                score=float(score) if isinstance(score, (int, float)) else None,
                input_count=estimate_tokens(question),
                output_count=len(data.get("unsupported_claims", []) or []),
                data=data,
            ),
        }

    def _effective_category(self, requested_category: str, route_data: dict[str, Any]) -> str:
        requested = (requested_category or "").strip() or "chat-auto"
        if requested not in {"chat-auto", "general"}:
            return requested
        if route_data.get("supported") and route_data.get("primary_category"):
            return str(route_data["primary_category"])
        return requested

    def _selected_route_paths(self, route_data: dict[str, Any]) -> list[str]:
        if not route_data.get("supported"):
            return []
        primary_folder = str(route_data.get("primary_folder") or "").strip()
        primary_category = str(route_data.get("primary_category") or "").strip()
        if not primary_folder:
            return []
        selected = [primary_folder]
        for route in route_data.get("top_routes", []):
            folder_path = str(route.get("folder_path") or "").strip()
            category = str(route.get("category") or "").strip()
            confidence = float(route.get("confidence") or 0.0)
            if not folder_path or folder_path == primary_folder:
                continue
            if category == primary_category and confidence >= 0.45:
                selected.append(folder_path)
            if len(selected) >= 3:
                break
        return selected

    def _stage_refresh_logs(self, logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        staged = []
        for log in logs:
            agent = str(log.get("agent", "KnowledgeAgent"))
            stage = "refresh"
            if "Search" in agent:
                stage = "search"
            elif "Crawler" in agent:
                stage = "crawl"
            elif "Cleaner" in agent:
                stage = "clean"
            elif "Extractor" in agent:
                stage = "extract"
            elif "Critic" in agent:
                stage = "quality"
            elif "Map" in agent:
                stage = "map"
            next_log = dict(log)
            next_log["stage"] = next_log.get("stage") or stage
            next_log["score"] = next_log.get("score")
            next_log["input_count"] = next_log.get("input_count")
            next_log["output_count"] = next_log.get("output_count")
            staged.append(next_log)
        return staged

    def _agent_roles(self, logs: list[dict[str, Any]]) -> list[dict[str, str]]:
        role_map = {
            "input": ("Input Router", "Chuẩn hóa câu hỏi và giảm token nhiễu."),
            "route": ("Knowledge Router", "Nhận diện input và phân cấp tới folder tri thức phù hợp."),
            "plan": ("Planner", "Chia request thành bước, intent, risk và quyền chạy auto-refresh."),
            "answer": ("Retrieval Answer", "Tìm chunk phù hợp và tổng hợp câu trả lời."),
            "answer_after_refresh": ("Post-refresh Answer", "Trả lời lại sau khi kho tri thức được cập nhật."),
            "refresh": ("Auto Research", "Search/crawl/tóm tắt khi kho còn thiếu dữ liệu."),
            "search": ("Search Worker", "Tìm nguồn web liên quan."),
            "crawl": ("Crawler Worker", "Đọc nội dung nguồn."),
            "clean": ("Noise Cleaner", "Làm sạch text và bỏ phần rác."),
            "extract": ("Extractor", "Rút ý chính, khái niệm, rủi ro."),
            "quality": ("Quality Critic", "Chấm độ tin cậy nguồn."),
            "map": ("Map Writer", "Ghi shard và cập nhật knowledge map."),
            "verify": ("Verifier", "Kiểm tra grounding, citation, claim thiếu nguồn và rủi ro."),
            "memory": ("Chat Memory", "Lưu lịch sử chat thành Markdown."),
        }
        roles: list[dict[str, str]] = []
        seen: set[str] = set()
        for log in logs:
            stage = str(log.get("stage") or "")
            if stage in seen:
                continue
            seen.add(stage)
            title, description = role_map.get(stage, (str(log.get("agent", "Agent")), str(log.get("message", ""))))
            roles.append({"stage": stage, "name": title, "description": description})
        return roles

    def _log(
        self,
        agent: str,
        stage: str,
        message: str,
        *,
        started: float | None = None,
        score: float | None = None,
        input_count: int | None = None,
        output_count: int | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        runtime_ms = int((perf_counter() - started) * 1000) if started is not None else 0
        return {
            "agent": agent,
            "status": "success",
            "message": message,
            "stage": stage,
            "score": score,
            "runtime_ms": runtime_ms,
            "started_at": now,
            "ended_at": now,
            "input_count": input_count,
            "output_count": output_count,
            "data": data or {},
        }

    def _plan_score(self, plan_data: dict[str, Any]) -> float:
        if plan_data.get("approval_required"):
            return 0.45
        if plan_data.get("refresh_allowed"):
            return 0.86
        return 0.78

    def _verified_confidence(self, answer_confidence: Any, verifier_confidence: Any) -> float:
        try:
            answer_value = float(answer_confidence)
        except (TypeError, ValueError):
            answer_value = 0.0
        try:
            verifier_value = float(verifier_confidence)
        except (TypeError, ValueError):
            verifier_value = answer_value
        if answer_value <= 0:
            return round(verifier_value, 4)
        if verifier_value <= 0:
            return round(answer_value, 4)
        return round(min(answer_value, verifier_value), 4)
