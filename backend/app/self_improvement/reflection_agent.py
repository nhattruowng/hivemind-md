import json
import re

from app.self_improvement.improvement_memory import ImprovementMemory
from app.self_improvement.improvement_policy import ImprovementPolicy
from app.self_improvement.schemas import EvaluationResult
from app.services.ollama_service import OllamaService


REFLECTION_PROMPT = """Bạn là Reflection Agent của HiveMind MD.

Dựa trên task, output và đánh giá, hãy rút ra bài học có thể tái sử dụng để agent làm tốt hơn lần sau.

TASK:
{task}

OUTPUT:
{output}

EVALUATION:
{evaluation_json}

Yêu cầu:
- Không viết chung chung.
- Bài học phải có thể áp dụng lại.
- Không đề xuất fine-tune model.
- Không đề xuất sửa code tự động nguy hiểm.

Trả về Markdown:
## Lesson Title

### Context

### Mistake / Weakness

### Improved Strategy

### When To Apply

### Status
Active
"""


class ReflectionAgent:
    name = "ReflectionAgent"

    def __init__(
        self,
        ollama_service: OllamaService | None = None,
        memory: ImprovementMemory | None = None,
        policy: ImprovementPolicy | None = None,
    ) -> None:
        self.ollama_service = ollama_service or OllamaService()
        self.memory = memory or ImprovementMemory()
        self.policy = policy or ImprovementPolicy.from_settings()

    async def reflect(
        self,
        task_id: str,
        task: str,
        agent_name: str,
        output: str,
        evaluation: EvaluationResult,
    ) -> dict[str, object] | None:
        if evaluation.score >= self.policy.reflection_score_threshold and not evaluation.should_reflect:
            return None

        evaluation_json = json.dumps(evaluation.model_dump(), ensure_ascii=True)
        prompt = REFLECTION_PROMPT.format(task=task, output=output, evaluation_json=evaluation_json)
        markdown = await self.ollama_service.generate(prompt, temperature=0.1)
        if not markdown:
            markdown = self._fallback_markdown(task, agent_name, evaluation)

        title = self._extract_title(markdown)
        lesson_type = self._lesson_type(evaluation)
        if not self.policy.auto_save_lessons:
            return {
                "id": 0,
                "title": title,
                "lesson_type": lesson_type,
                "agent_name": agent_name,
                "task_id": task_id,
                "content": markdown,
                "status": "active",
                "created_at": "",
                "updated_at": "",
            }
        return self.memory.save_lesson(
            title=title,
            lesson_type=lesson_type,
            content=markdown,
            agent_name=agent_name,
            task_id=task_id,
        )

    def _fallback_markdown(self, task: str, agent_name: str, evaluation: EvaluationResult) -> str:
        weaknesses = "; ".join(evaluation.weaknesses or evaluation.missing_parts or ["The output missed reusable quality criteria."])
        suggestions = "; ".join(evaluation.improvement_suggestions or ["Check completeness and structure before finishing."])
        return "\n".join(
            [
                f"## Improve {agent_name} responses for similar tasks",
                "",
                "### Context",
                task,
                "",
                "### Mistake / Weakness",
                weaknesses,
                "",
                "### Improved Strategy",
                suggestions,
                "",
                "### When To Apply",
                f"Apply when {agent_name} handles tasks with similar inputs or failure patterns.",
                "",
                "### Status",
                "Active",
            ]
        )

    def _extract_title(self, markdown: str) -> str:
        match = re.search(r"^##\s+(.+)$", markdown, re.MULTILINE)
        if match:
            return match.group(1).strip()[:160]
        return "Reusable improvement lesson"

    def _lesson_type(self, evaluation: EvaluationResult) -> str:
        if evaluation.score < 24 or evaluation.hallucination_risk == "high":
            return "error"
        if any("tool" in item.lower() for item in evaluation.improvement_suggestions):
            return "tool"
        return "prompt"
