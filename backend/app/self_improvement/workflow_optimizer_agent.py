import json
from typing import Any

from app.self_improvement.evaluator_agent import extract_json_object
from app.self_improvement.improvement_policy import ImprovementPolicy
from app.self_improvement.schemas import EvaluationResult
from app.self_improvement.score_service import ScoreService
from app.services.ollama_service import OllamaService


WORKFLOW_OPTIMIZER_PROMPT = """Bạn là Workflow Optimizer Agent của HiveMind MD.

Hãy phân tích workflow hiện tại và đề xuất cải tiến.

TASK:
{task}

AGENT LOGS:
{agent_logs}

RUNTIME METRICS:
{runtime_metrics}

EVALUATION:
{evaluation_json}

Hãy đề xuất:
1. Có bước nào nên thêm không?
2. Có bước nào dư không?
3. Có nên đổi thứ tự agent không?
4. Có cần retry logic không?
5. Có cần human review không?
6. Có bước nào gây tốn tài nguyên không?

Trả về JSON hợp lệ:
{{
  "workflow_changes": [],
  "expected_benefit": "string",
  "risk_level": "low | medium | high",
  "auto_apply_allowed": false
}}
"""


class WorkflowOptimizerAgent:
    name = "WorkflowOptimizerAgent"

    def __init__(
        self,
        ollama_service: OllamaService | None = None,
        score_service: ScoreService | None = None,
        policy: ImprovementPolicy | None = None,
    ) -> None:
        self.ollama_service = ollama_service or OllamaService()
        self.score_service = score_service or ScoreService()
        self.policy = policy or ImprovementPolicy.from_settings()

    async def optimize(
        self,
        task_id: str,
        task: str,
        agent_logs: list[dict[str, Any]],
        runtime_metrics: dict[str, Any],
        evaluation: EvaluationResult,
    ) -> dict[str, object] | None:
        evaluation_json = json.dumps(evaluation.model_dump(), ensure_ascii=True)
        prompt = WORKFLOW_OPTIMIZER_PROMPT.format(
            task=task,
            agent_logs=json.dumps(agent_logs, ensure_ascii=True, default=str),
            runtime_metrics=json.dumps(runtime_metrics, ensure_ascii=True, default=str),
            evaluation_json=evaluation_json,
        )
        response = await self.ollama_service.generate(prompt, temperature=0.1)
        parsed = extract_json_object(response) or self._fallback_suggestion(agent_logs, runtime_metrics, evaluation)
        changes = parsed.get("workflow_changes") or []
        if isinstance(changes, str):
            changes = [changes]
        changes = [str(item).strip() for item in changes if str(item).strip()]
        if not changes:
            return None

        risk_level = self._safe_risk(str(parsed.get("risk_level", "medium")))
        suggestion = "\n".join(f"- {item}" for item in changes)
        expected_benefit = str(parsed.get("expected_benefit") or "Improve workflow reliability for similar tasks.")
        return self.score_service.create_workflow_suggestion(
            task_id=task_id,
            suggestion=suggestion,
            expected_benefit=expected_benefit,
            risk_level=risk_level,
            status="pending",
        )

    def _fallback_suggestion(
        self,
        agent_logs: list[dict[str, Any]],
        runtime_metrics: dict[str, Any],
        evaluation: EvaluationResult,
    ) -> dict[str, object]:
        failed_agents = [str(item.get("agent")) for item in agent_logs if item.get("status") == "failed"]
        runtime_ms = int(runtime_metrics.get("runtime_ms") or 0)
        changes: list[str] = []
        if failed_agents:
            changes.append(f"Add retry or human review after failures in {', '.join(failed_agents)}.")
        if evaluation.missing_parts:
            changes.append("Add a validation checkpoint for missing required output parts before the next agent runs.")
        if runtime_ms > 30000:
            changes.append("Review whether this agent step can use fewer sources or a lighter model for quick mode.")
        if not changes:
            changes.append("Add a lightweight review checkpoint for low-scoring outputs before downstream reuse.")
        return {
            "workflow_changes": changes,
            "expected_benefit": "Reduce repeated low-score runs without changing production workflow automatically.",
            "risk_level": "medium",
            "auto_apply_allowed": False,
        }

    def _safe_risk(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized in {"low", "medium", "high"}:
            return normalized
        return "medium"
