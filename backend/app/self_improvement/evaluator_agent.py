import json
import re
from typing import Any

from app.self_improvement.improvement_policy import ImprovementPolicy
from app.self_improvement.schemas import EvaluationResult
from app.services.ollama_service import OllamaService


EVALUATOR_PROMPT = """Bạn là Evaluator Agent của HiveMind MD.

Hãy đánh giá kết quả của agent dựa trên task.

TASK:
{task}

AGENT NAME:
{agent_name}

INPUT:
{agent_input}

OUTPUT:
{output}

Chấm điểm theo thang 0-60:
1. Đúng yêu cầu: 0-10
2. Đầy đủ: 0-10
3. Có cấu trúc rõ: 0-10
4. Có thể hành động được: 0-10
5. Không bịa/không suy đoán quá mức: 0-10
6. Tối ưu tài nguyên/local-first: 0-10

Trả về JSON hợp lệ:
{{
  "score": 0,
  "strengths": [],
  "weaknesses": [],
  "missing_parts": [],
  "hallucination_risk": "low | medium | high",
  "improvement_suggestions": [],
  "should_reflect": true
}}
"""


class EvaluatorAgent:
    name = "EvaluatorAgent"

    def __init__(
        self,
        ollama_service: OllamaService | None = None,
        policy: ImprovementPolicy | None = None,
    ) -> None:
        self.ollama_service = ollama_service or OllamaService()
        self.policy = policy or ImprovementPolicy.from_settings()

    async def evaluate(
        self,
        task: str,
        agent_name: str,
        input: str | None,
        output: str | None,
        expected_result: str | None = None,
    ) -> EvaluationResult:
        if not output or not output.strip():
            return self._fallback_score(task, agent_name, input, output, expected_result)

        prompt = EVALUATOR_PROMPT.format(
            task=task,
            agent_name=agent_name,
            agent_input=input or "",
            output=output,
        )
        response = await self.ollama_service.generate(prompt, temperature=0)
        parsed = self._parse_evaluation(response)
        if parsed:
            return parsed
        return self._fallback_score(task, agent_name, input, output, expected_result)

    def _parse_evaluation(self, response: str | None) -> EvaluationResult | None:
        data = extract_json_object(response)
        if not data:
            return None
        try:
            score = max(0, min(60, float(data.get("score", 0))))
            risk = str(data.get("hallucination_risk", "medium")).strip().lower()
            if risk not in {"low", "medium", "high"}:
                risk = "medium"
            return EvaluationResult(
                score=score,
                strengths=coerce_string_list(data.get("strengths")),
                weaknesses=coerce_string_list(data.get("weaknesses")),
                missing_parts=coerce_string_list(data.get("missing_parts")),
                hallucination_risk=risk,  # type: ignore[arg-type]
                improvement_suggestions=coerce_string_list(data.get("improvement_suggestions")),
                should_reflect=coerce_bool(
                    data.get("should_reflect"),
                    default=score < self.policy.reflection_score_threshold,
                ),
            )
        except Exception:
            return None

    def _fallback_score(
        self,
        task: str,
        agent_name: str,
        input: str | None,
        output: str | None,
        expected_result: str | None = None,
    ) -> EvaluationResult:
        output = output or ""
        output_lower = output.lower()
        if not output.strip():
            return EvaluationResult(
                score=4,
                strengths=[],
                weaknesses=["Agent output is empty."],
                missing_parts=["A usable response or data payload."],
                hallucination_risk="high",
                improvement_suggestions=["Return a structured result with status, message, and data."],
                should_reflect=True,
            )

        score = 20.0
        strengths: list[str] = []
        weaknesses: list[str] = []
        missing_parts: list[str] = []
        suggestions: list[str] = []

        if "status" in output_lower and "success" in output_lower:
            score += 10
            strengths.append("Output reports a successful status.")
        elif "failed" in output_lower or "error" in output_lower:
            score -= 8
            weaknesses.append("Output contains an error or failed status.")

        if len(output) > 300:
            score += 8
            strengths.append("Output has enough detail for review.")
        else:
            missing_parts.append("More detailed result content.")

        if any(token in output for token in ("{", "[", ":", "- ")):
            score += 8
            strengths.append("Output appears structured.")
        else:
            weaknesses.append("Output is not clearly structured.")

        if task.lower()[:24] and task.lower()[:24] in output_lower:
            score += 4
        if expected_result and expected_result.lower() in output_lower:
            score += 6

        if "http" in output_lower or "source" in output_lower or "markdown" in output_lower:
            score += 5
        if not input:
            suggestions.append("Include the effective agent input in future logs.")

        score = max(0, min(60, round(score, 2)))
        if not suggestions:
            suggestions.append(f"Review {agent_name} output against the task before reusing it.")
        return EvaluationResult(
            score=score,
            strengths=strengths,
            weaknesses=weaknesses,
            missing_parts=missing_parts,
            hallucination_risk="medium" if score < 42 else "low",
            improvement_suggestions=suggestions,
            should_reflect=score < self.policy.reflection_score_threshold,
        )


def extract_json_object(response: str | None) -> dict[str, Any] | None:
    if not response:
        return None
    text = response.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        text = text[start : end + 1]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def coerce_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0"}:
            return False
    if value is None:
        return default
    return bool(value)
