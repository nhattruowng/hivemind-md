import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.database import init_db
from app.self_improvement.evaluator_agent import EvaluatorAgent
from app.self_improvement.improvement_memory import ImprovementMemory
from app.self_improvement.improvement_policy import ImprovementPolicy
from app.self_improvement.prompt_version_service import PromptVersionService
from app.self_improvement.reflection_agent import ReflectionAgent
from app.self_improvement.schemas import EvaluationResult
from app.self_improvement.score_service import ScoreService


class InvalidJsonOllama:
    async def generate(self, *args, **kwargs):
        return "not valid json"


class MarkdownOllama:
    async def generate(self, *args, **kwargs):
        return """## Tighten source handling

### Context
The agent returned a weak output.

### Mistake / Weakness
It missed required detail.

### Improved Strategy
Return structured data and explain missing fields.

### When To Apply
When source data is incomplete.

### Status
Active
"""


class SelfImprovementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        os.environ["DATABASE_URL"] = f"sqlite:///{self.root / 'test.db'}"
        os.environ["KNOWLEDGE_DIR"] = str(self.root / "knowledge")
        os.environ["VECTOR_STORE_DIR"] = str(self.root / "vector")
        os.environ["REFLECTION_SCORE_THRESHOLD"] = "42"
        get_settings.cache_clear()
        init_db()

    def tearDown(self) -> None:
        get_settings.cache_clear()
        self.temp_dir.cleanup()

    def test_record_agent_run_success(self) -> None:
        service = ScoreService()
        run_id = service.record_agent_run(
            task_id="task-1",
            task="Build local knowledge",
            agent_name="SearchAgent",
            input="{}",
            output='{"status":"success"}',
            status="success",
            runtime_ms=12,
        )
        runs = service.list_agent_runs(agent_name="SearchAgent")
        self.assertEqual(run_id, runs[0]["id"])
        self.assertEqual(runs[0]["status"], "success")

    def test_evaluator_fallback_when_json_invalid(self) -> None:
        evaluator = EvaluatorAgent(ollama_service=InvalidJsonOllama(), policy=ImprovementPolicy())
        result = asyncio.run(
            evaluator.evaluate(
                task="Create a note",
                agent_name="ComposerAgent",
                input="{}",
                output='{"status":"success","message":"done"}',
            )
        )
        self.assertGreaterEqual(result.score, 0)
        self.assertLessEqual(result.score, 60)

    def test_reflection_creates_lesson_when_score_low(self) -> None:
        memory = ImprovementMemory()
        reflection = ReflectionAgent(
            ollama_service=MarkdownOllama(),
            memory=memory,
            policy=ImprovementPolicy(reflection_score_threshold=42),
        )
        evaluation = EvaluationResult(
            score=20,
            weaknesses=["Missing detail"],
            improvement_suggestions=["Return structured output"],
            should_reflect=True,
        )
        lesson = asyncio.run(
            reflection.reflect(
                task_id="task-2",
                task="Build note",
                agent_name="ComposerAgent",
                output="weak output",
                evaluation=evaluation,
            )
        )
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson["title"], "Tighten source handling")
        markdown = (self.root / "knowledge" / "self-improvement" / "error-patterns.md").read_text(encoding="utf-8")
        self.assertIn("Tighten source handling", markdown)

    def test_prompt_version_created_and_activation_deactivates_old(self) -> None:
        service = PromptVersionService()
        first = service.create_prompt_version("ComposerAgent", "prompt one", "low", "initial")
        second = service.create_prompt_version("ComposerAgent", "prompt two", "low", "improved")
        service.activate_prompt_version(int(first["id"]))
        active = service.activate_prompt_version(int(second["id"]))
        versions = service.list_prompt_versions(agent_name="ComposerAgent")
        self.assertEqual(active["id"], second["id"])
        self.assertEqual(sum(1 for item in versions if item["is_active"]), 1)
        self.assertEqual(service.get_active_prompt("ComposerAgent")["id"], second["id"])

    def test_workflow_suggestion_saved_pending(self) -> None:
        suggestion = ScoreService().create_workflow_suggestion(
            task_id="task-3",
            suggestion="- Add review checkpoint",
            expected_benefit="Catch weak outputs",
            risk_level="medium",
        )
        self.assertEqual(suggestion["status"], "pending")

    def test_summary_returns_expected_fields(self) -> None:
        score_service = ScoreService()
        score_service.record_agent_run(
            task_id="task-4",
            task="Build note",
            agent_name="SearchAgent",
            status="success",
            score=50,
        )
        ImprovementMemory().save_lesson(
            title="Keep structured output",
            lesson_type="prompt",
            content="Use structured output.",
            agent_name="SearchAgent",
            task_id="task-4",
        )
        PromptVersionService().create_prompt_version("SearchAgent", "prompt", "low", "test", score=50)
        score_service.create_workflow_suggestion("task-4", "- Add checkpoint")
        summary = score_service.get_summary()
        self.assertEqual(
            set(summary.keys()),
            {
                "total_runs",
                "average_score",
                "success_rate",
                "total_lessons",
                "total_prompt_versions",
                "pending_workflow_suggestions",
            },
        )
        self.assertEqual(summary["total_runs"], 1)
        self.assertEqual(summary["pending_workflow_suggestions"], 1)


if __name__ == "__main__":
    unittest.main()
