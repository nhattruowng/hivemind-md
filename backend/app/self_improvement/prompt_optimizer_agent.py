import json

from app.self_improvement.evaluator_agent import extract_json_object, coerce_string_list
from app.self_improvement.improvement_policy import ImprovementPolicy
from app.self_improvement.prompt_version_service import PromptVersionService
from app.self_improvement.schemas import EvaluationResult
from app.services.ollama_service import OllamaService


PROMPT_OPTIMIZER_PROMPT = """Bạn là Prompt Optimizer Agent của HiveMind MD.

Hãy tối ưu prompt cho agent dựa trên lỗi đã được phát hiện.

CURRENT PROMPT:
{current_prompt}

TASK:
{task}

OUTPUT:
{output}

EVALUATION:
{evaluation_json}

LESSONS:
{lessons}

Yêu cầu:
1. Giữ mục tiêu ban đầu của agent.
2. Không làm prompt dài quá mức.
3. Thêm ràng buộc cụ thể để tránh lỗi cũ.
4. Không thêm hành vi nguy hiểm.
5. Không yêu cầu fine-tune.
6. Không yêu cầu sửa code production.

Trả về JSON hợp lệ:
{{
  "optimized_prompt": "string",
  "changes": [],
  "risk_level": "low | medium | high",
  "change_reason": "string",
  "should_auto_apply": false
}}
"""


class PromptOptimizerAgent:
    name = "PromptOptimizerAgent"

    def __init__(
        self,
        ollama_service: OllamaService | None = None,
        prompt_service: PromptVersionService | None = None,
        policy: ImprovementPolicy | None = None,
    ) -> None:
        self.ollama_service = ollama_service or OllamaService()
        self.prompt_service = prompt_service or PromptVersionService()
        self.policy = policy or ImprovementPolicy.from_settings()

    async def optimize(
        self,
        agent_name: str,
        current_prompt: str,
        task: str,
        output: str,
        evaluation: EvaluationResult,
        lessons: str,
    ) -> dict[str, object] | None:
        evaluation_json = json.dumps(evaluation.model_dump(), ensure_ascii=True)
        prompt = PROMPT_OPTIMIZER_PROMPT.format(
            current_prompt=current_prompt,
            task=task,
            output=output,
            evaluation_json=evaluation_json,
            lessons=lessons,
        )
        response = await self.ollama_service.generate(prompt, temperature=0.1)
        parsed = extract_json_object(response) or self._fallback_optimization(current_prompt, evaluation)

        optimized_prompt = str(parsed.get("optimized_prompt") or current_prompt).strip()
        if not optimized_prompt:
            return None
        risk_level = self._safe_risk(str(parsed.get("risk_level", "medium")))
        change_reason = str(parsed.get("change_reason") or "Prompt version generated from self-improvement feedback.")
        should_auto_apply = bool(parsed.get("should_auto_apply", False))

        if not self.policy.auto_save_prompt_versions:
            return None
        version = self.prompt_service.create_prompt_version(
            agent_name=agent_name,
            prompt=optimized_prompt,
            risk_level=risk_level,
            change_reason=change_reason,
            score=evaluation.score,
        )
        if version and self.policy.can_auto_apply_prompt(risk_level, should_auto_apply):
            version = self.prompt_service.activate_prompt_version(int(version["id"]))
        return version

    def _fallback_optimization(self, current_prompt: str, evaluation: EvaluationResult) -> dict[str, object]:
        suggestions = coerce_string_list(evaluation.improvement_suggestions)
        missing = coerce_string_list(evaluation.missing_parts)
        additions = suggestions or missing or ["Return complete, structured, evidence-aware output."]
        optimized = "\n".join(
            [
                current_prompt.strip(),
                "",
                "Self-improvement constraints:",
                *[f"- {item}" for item in additions[:4]],
                "- Do not request fine-tuning, production code changes, or unsafe automation.",
            ]
        ).strip()
        return {
            "optimized_prompt": optimized,
            "changes": additions,
            "risk_level": "low",
            "change_reason": "Rule-based fallback prompt improvement after a low evaluation score.",
            "should_auto_apply": False,
        }

    def _safe_risk(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized in {"low", "medium", "high"}:
            return normalized
        return "medium"
