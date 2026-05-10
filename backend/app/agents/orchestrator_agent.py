import json
import logging
from time import perf_counter
from typing import Any
from uuid import uuid4

from app.agents.base_agent import BaseAgent
from app.agents.cleaner_agent import CleanerAgent
from app.agents.composer_agent import ComposerAgent
from app.agents.crawler_agent import CrawlerAgent
from app.agents.critic_agent import CriticAgent
from app.agents.extractor_agent import ExtractorAgent
from app.agents.indexer_agent import IndexerAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.search_agent import SearchAgent
from app.config import get_settings
from app.self_improvement.evaluator_agent import EvaluatorAgent
from app.self_improvement.improvement_memory import ImprovementMemory
from app.self_improvement.improvement_policy import ImprovementPolicy
from app.self_improvement.prompt_optimizer_agent import PromptOptimizerAgent
from app.self_improvement.reflection_agent import ReflectionAgent
from app.self_improvement.score_service import ScoreService
from app.self_improvement.workflow_optimizer_agent import WorkflowOptimizerAgent


MODE_LIMITS = {"quick": 3, "standard": 5, "deep": 10}
logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    name = "OrchestratorAgent"
    description = "Coordinate the sequential multi-agent knowledge build workflow."

    def __init__(
        self,
        search_agent: SearchAgent | None = None,
        crawler_agent: CrawlerAgent | None = None,
        cleaner_agent: CleanerAgent | None = None,
        extractor_agent: ExtractorAgent | None = None,
        critic_agent: CriticAgent | None = None,
        composer_agent: ComposerAgent | None = None,
        indexer_agent: IndexerAgent | None = None,
        planner_agent: PlannerAgent | None = None,
    ) -> None:
        self.planner_agent = planner_agent or PlannerAgent()
        self.search_agent = search_agent or SearchAgent()
        self.crawler_agent = crawler_agent or CrawlerAgent()
        self.cleaner_agent = cleaner_agent or CleanerAgent()
        self.extractor_agent = extractor_agent or ExtractorAgent()
        self.critic_agent = critic_agent or CriticAgent()
        self.composer_agent = composer_agent or ComposerAgent()
        self.indexer_agent = indexer_agent or IndexerAgent()
        self.settings = get_settings()
        self.policy = ImprovementPolicy.from_settings(self.settings)
        self.score_service = ScoreService()
        self.memory = ImprovementMemory(self.settings)
        self.evaluator_agent = EvaluatorAgent(policy=self.policy)
        self.reflection_agent = ReflectionAgent(memory=self.memory, policy=self.policy)
        self.prompt_optimizer_agent = PromptOptimizerAgent(policy=self.policy)
        self.workflow_optimizer_agent = WorkflowOptimizerAgent(score_service=self.score_service, policy=self.policy)

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        topic = str(kwargs["topic"])
        category = str(kwargs.get("category", "general"))
        mode = str(kwargs.get("mode", "standard"))
        limit = MODE_LIMITS.get(mode, MODE_LIMITS["standard"])
        task_id = uuid4().hex
        logs: list[dict[str, Any]] = []

        plan = await self._execute_agent(
            self.planner_agent,
            task_id=task_id,
            task=topic,
            agent_input={
                "request": topic,
                "category": category,
                "mode": mode,
                "auto_refresh": True,
                "workflow": "knowledge_build",
            },
        )
        logs.append(plan)
        plan_data = plan.get("data", {})
        if plan_data.get("approval_required"):
            return self.failed(
                "Knowledge build plan requires human approval before execution.",
                {"agent_logs": logs, "plan": plan_data},
            )

        search = await self._execute_agent(
            self.search_agent,
            task_id=task_id,
            task=topic,
            agent_input={"topic": topic, "limit": limit},
        )
        logs.append(search)
        sources = search.get("data", {}).get("sources", [])[:limit]

        crawl = await self._execute_agent(
            self.crawler_agent,
            task_id=task_id,
            task=topic,
            agent_input={"sources": sources},
        )
        logs.append(crawl)
        documents = crawl.get("data", {}).get("documents", [])

        clean = await self._execute_agent(
            self.cleaner_agent,
            task_id=task_id,
            task=topic,
            agent_input={"documents": documents},
        )
        logs.append(clean)
        cleaned_documents = clean.get("data", {}).get("cleaned_documents", [])

        extract = await self._execute_agent(
            self.extractor_agent,
            task_id=task_id,
            task=topic,
            agent_input={"cleaned_documents": cleaned_documents},
        )
        logs.append(extract)
        extracted = extract.get("data", {}).get("extracted", [])

        critic = await self._execute_agent(
            self.critic_agent,
            task_id=task_id,
            task=topic,
            agent_input={"cleaned_documents": cleaned_documents},
        )
        logs.append(critic)
        critiques = critic.get("data", {}).get("critiques", [])

        compose = await self._execute_agent(
            self.composer_agent,
            task_id=task_id,
            task=topic,
            agent_input={
                "topic": topic,
                "category": category,
                "sources": sources,
                "extracted": extracted,
                "critiques": critiques,
            },
        )
        logs.append(compose)
        compose_data = compose.get("data", {})

        index = await self._execute_agent(
            self.indexer_agent,
            task_id=task_id,
            task=topic,
            agent_input={
                "file_path": compose_data.get("absolute_path", compose_data.get("markdown_file", "")),
                "metadata": compose_data.get("metadata", {}),
            },
        )
        logs.append(index)

        markdown_file = compose_data.get("markdown_file", "")
        return self.success(
            f"Knowledge build finished for {topic}.",
            {"markdown_file": markdown_file, "agent_logs": logs, "content": compose_data.get("content", "")},
        )

    async def _execute_agent(
        self,
        agent: BaseAgent,
        task_id: str,
        task: str,
        agent_input: dict[str, Any],
    ) -> dict[str, Any]:
        started_at = perf_counter()
        result = await agent.execute(**agent_input)
        runtime_ms = int((perf_counter() - started_at) * 1000)
        input_text = self._safe_json(agent_input)
        output_text = self._safe_json(result)
        status = str(result.get("status", "failed"))
        run_id = self.score_service.record_agent_run(
            task_id=task_id,
            task=task,
            agent_name=agent.name,
            input=input_text,
            output=output_text,
            status=status,
            error_message=str(result.get("message", "")) if status == "failed" else None,
            runtime_ms=runtime_ms,
        )

        if self.settings.self_improvement_enabled:
            await self._run_self_improvement(
                run_id=run_id,
                task_id=task_id,
                task=task,
                agent=agent,
                input_text=input_text,
                output_text=output_text,
                result=result,
                runtime_ms=runtime_ms,
            )
        return result

    async def _run_self_improvement(
        self,
        run_id: int,
        task_id: str,
        task: str,
        agent: BaseAgent,
        input_text: str,
        output_text: str,
        result: dict[str, Any],
        runtime_ms: int,
    ) -> None:
        try:
            evaluation = await self.evaluator_agent.evaluate(
                task=task,
                agent_name=agent.name,
                input=input_text,
                output=output_text,
            )
            self.score_service.update_run_score(run_id, evaluation.score)
            should_reflect = evaluation.should_reflect or evaluation.score < self.policy.reflection_score_threshold
            if not should_reflect:
                return

            lesson = await self.reflection_agent.reflect(
                task_id=task_id,
                task=task,
                agent_name=agent.name,
                output=output_text,
                evaluation=evaluation,
            )
            existing_lessons = self.memory.search_lessons(agent_name=agent.name, limit=5)
            lesson_text = "\n\n".join(str(item.get("content", "")) for item in existing_lessons)
            if lesson:
                lesson_text = f"{lesson.get('content', '')}\n\n{lesson_text}".strip()

            current_prompt = f"{agent.name}: {agent.description}"
            await self.prompt_optimizer_agent.optimize(
                agent_name=agent.name,
                current_prompt=current_prompt,
                task=task,
                output=output_text,
                evaluation=evaluation,
                lessons=lesson_text,
            )
            await self.workflow_optimizer_agent.optimize(
                task_id=task_id,
                task=task,
                agent_logs=[result],
                runtime_metrics={"runtime_ms": runtime_ms},
                evaluation=evaluation,
            )
        except Exception as exc:
            logger.warning("Self-improvement failed for %s: %s", agent.name, exc)

    def _safe_json(self, value: Any, max_length: int = 12000) -> str:
        text = json.dumps(value, ensure_ascii=True, default=str)
        if len(text) <= max_length:
            return text
        return f"{text[:max_length]}... [truncated]"
