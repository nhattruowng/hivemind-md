import json
import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.database import get_connection
from app.utils.text_utils import slugify


COMMON_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "task_id": {"type": "string"},
        "user_id": {"type": ["string", "null"]},
        "input": {"type": "object"},
        "context": {"type": "object"},
        "config": {"type": "object"},
    },
    "required": ["input"],
}
COMMON_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "agent": {"type": "string"},
        "status": {"enum": ["success", "failed", "needs_approval", "skipped"]},
        "message": {"type": "string"},
        "data": {"type": "object"},
        "confidence": {"type": ["number", "null"]},
        "sources": {"type": "array"},
        "tool_calls": {"type": "array"},
        "risk_level": {"enum": ["low", "medium", "high"]},
        "runtime_ms": {"type": "integer"},
    },
    "required": ["agent", "status", "message", "data"],
}
DEFAULT_METRICS = ["accuracy", "completeness", "faithfulness", "risk_score", "latency_ms"]


def _agent_slug(name: str) -> str:
    base = name.removesuffix("Agent")
    words = re.sub(r"(?<!^)(?=[A-Z])", "-", base)
    return slugify(words, fallback="agent")


def _agent(
    name: str,
    category: str,
    role: str,
    description: str,
    *,
    tools: list[str] | None = None,
    risk_level: str = "low",
    metrics: list[str] | None = None,
    default_model: str = "qwen2.5:7b",
) -> dict[str, Any]:
    slug = _agent_slug(name)
    return {
        "name": name,
        "slug": slug,
        "category": category,
        "description": description,
        "role": role,
        "goal": description,
        "system_prompt": f"{name}: {description}",
        "default_model": default_model,
        "risk_level": risk_level,
        "allowed_tools": tools or [],
        "input_schema": COMMON_INPUT_SCHEMA,
        "output_schema": COMMON_OUTPUT_SCHEMA,
        "evaluation_metrics": metrics or DEFAULT_METRICS,
        "config": {"class": name, "status": "registered"},
    }


DEFAULT_SYSTEM_AGENTS = [
    _agent("IntentClassifierAgent", "core", "intent_classifier", "Classifies user requests for routing and planning.", default_model="heuristic"),
    _agent("PlannerAgent", "core", "planner", "Creates structured execution plans and marks risky steps.", default_model="heuristic"),
    _agent("AgentRouterAgent", "core", "agent_router", "Maps planned steps to the best available agent.", tools=["memory_read"]),
    _agent("TaskExecutorAgent", "core", "task_executor", "Executes one planned task with structured logging.", tools=["approval_request"], risk_level="medium"),
    _agent("WorkflowAgent", "core", "workflow", "Coordinates JSON-defined workflow execution.", tools=["approval_request"], risk_level="medium"),
    _agent("DecisionAgent", "core", "decision", "Chooses next actions from verifier, policy, and runtime signals.", tools=["memory_read"]),
    _agent("SearchAgent", "knowledge", "search", "Finds candidate web sources for a research topic.", tools=["web_search"], metrics=["retrieval_precision", "source_quality", "latency_ms"]),
    _agent("CrawlerAgent", "knowledge", "crawler", "Fetches and extracts readable source page content.", tools=["web_crawl"], metrics=["extraction_quality", "source_quality", "latency_ms"]),
    _agent("CleanerAgent", "knowledge", "cleaner", "Removes boilerplate and noisy text from crawled documents.", metrics=["format_quality", "noise_reduction", "latency_ms"]),
    _agent("ExtractorAgent", "knowledge", "extractor", "Extracts summaries, concepts, key points, and risks.", metrics=["completeness", "accuracy", "latency_ms"]),
    _agent("CriticAgent", "knowledge", "critic", "Scores source trust and flags weak evidence.", metrics=["source_quality", "risk_score", "faithfulness"]),
    _agent("ComposerAgent", "knowledge", "composer", "Composes grounded Markdown knowledge shards.", tools=["markdown_write"], metrics=["format_quality", "citation_quality", "faithfulness"]),
    _agent("IndexerAgent", "knowledge", "indexer", "Indexes Markdown into the vector store.", tools=["vector_search", "markdown_read"], metrics=["index_success", "latency_ms"]),
    _agent("RAGAgent", "knowledge", "rag", "Retrieves relevant knowledge chunks for grounded answers.", tools=["knowledge_search", "vector_search"], metrics=["retrieval_precision", "faithfulness", "latency_ms"]),
    _agent("RerankerAgent", "knowledge", "reranker", "Reranks retrieved chunks before context assembly.", tools=["vector_search"], metrics=["retrieval_precision", "citation_quality"]),
    _agent("ContextCompressorAgent", "knowledge", "context_compressor", "Compresses context while preserving citations.", metrics=["compression_ratio", "faithfulness", "citation_quality"]),
    _agent("CitationAgent", "knowledge", "citation", "Builds chunk-to-source citation maps.", tools=["markdown_read"], metrics=["citation_quality", "faithfulness"]),
    _agent("KnowledgeRefreshAgent", "knowledge", "knowledge_refresh", "Refreshes local Markdown knowledge when evidence is insufficient.", tools=["web_search", "web_crawl", "markdown_write", "vector_search"], risk_level="medium"),
    _agent("VerifierAgent", "safety", "verifier", "Verifies answer grounding, citations, missing points, and action risk.", default_model="heuristic"),
    _agent("HallucinationGuardAgent", "safety", "hallucination_guard", "Detects unsupported claims and no-answer conditions.", metrics=["faithfulness", "unsupported_claim_rate", "risk_score"]),
    _agent("PolicyAgent", "safety", "policy", "Evaluates policy risk before tool execution.", tools=["approval_request"], risk_level="medium", metrics=["risk_score", "approval_accuracy"]),
    _agent("ApprovalAgent", "safety", "approval", "Creates and resolves human approval requests.", tools=["approval_request"], risk_level="medium", metrics=["approval_accuracy", "latency_ms"]),
    _agent("SecurityAgent", "safety", "security", "Checks prompt injection, path safety, secret leakage, and unsafe actions.", tools=["code_read"], risk_level="medium", metrics=["risk_score", "security_findings"]),
    _agent("RollbackAgent", "safety", "rollback", "Prepares rollback plans for prompts, workflows, and risky state changes.", tools=["markdown_read", "markdown_write"], risk_level="high", metrics=["rollback_success", "risk_score"]),
    _agent("ProfileAgent", "personalization", "profile", "Builds user profile context from stable preferences.", tools=["memory_read"]),
    _agent("MemoryAgent", "personalization", "memory", "Decides whether to save, update, or archive memories.", tools=["memory_read", "memory_write"], risk_level="medium"),
    _agent("PreferenceAgent", "personalization", "preference", "Extracts stable user preferences from interactions.", tools=["memory_read", "memory_write"], risk_level="medium"),
    _agent("ContextBuilderAgent", "personalization", "context_builder", "Builds compact request context from profile, memory, and routes.", tools=["memory_read", "knowledge_search"]),
    _agent("FeedbackAgent", "personalization", "feedback", "Captures user ratings and correction signals.", tools=["memory_write"], risk_level="medium"),
    _agent("LearningAgent", "personalization", "learning", "Turns repeated feedback into improvement proposals without auto-apply.", tools=["memory_read", "memory_write"], risk_level="medium"),
    _agent("CodeAgent", "coding_documents", "code", "Explains code and proposes small implementation changes.", tools=["code_read"], risk_level="medium", metrics=["accuracy", "test_relevance", "risk_score"]),
    _agent("DebugAgent", "coding_documents", "debug", "Inspects errors and proposes root-cause fixes.", tools=["code_read", "run_tests"], risk_level="medium", metrics=["bug_fix_accuracy", "test_relevance", "latency_ms"]),
    _agent("ReviewAgent", "coding_documents", "review", "Reviews code quality, security, architecture, and missing tests.", tools=["code_read"], metrics=["issue_precision", "risk_score", "test_relevance"]),
    _agent("TestGeneratorAgent", "coding_documents", "test_generator", "Generates focused unit/API/regression tests.", tools=["code_read", "code_write", "run_tests"], risk_level="high", metrics=["test_relevance", "coverage_delta", "risk_score"]),
    _agent("DocumentAgent", "coding_documents", "document", "Creates and edits grounded technical documentation.", tools=["markdown_read", "markdown_write"], risk_level="medium", metrics=["format_quality", "completeness", "accuracy"]),
    _agent("RefactorAgent", "coding_documents", "refactor", "Proposes maintainable refactors and risk-limited code changes.", tools=["code_read", "code_write", "run_tests"], risk_level="high", metrics=["maintainability", "test_relevance", "risk_score"]),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AgentRegistry:
    def ensure_system_agents(self) -> None:
        now = utc_now()
        active_system_slugs = [item["slug"] for item in DEFAULT_SYSTEM_AGENTS]
        with get_connection() as connection:
            for item in DEFAULT_SYSTEM_AGENTS:
                existing = connection.execute(
                    "SELECT id FROM agents WHERE user_id = ? AND slug = ?",
                    ("system", item["slug"]),
                ).fetchone()
                values = (
                    item["name"],
                    item["category"],
                    item["description"],
                    item["role"],
                    item["goal"],
                    item["system_prompt"],
                    item["default_model"],
                    item["risk_level"],
                    json.dumps(item["allowed_tools"], ensure_ascii=True),
                    json.dumps(item["input_schema"], ensure_ascii=True),
                    json.dumps(item["output_schema"], ensure_ascii=True),
                    json.dumps(item["evaluation_metrics"], ensure_ascii=True),
                    json.dumps(item["config"], ensure_ascii=True),
                    now,
                )
                if existing:
                    connection.execute(
                        """
                        UPDATE agents
                        SET name = ?, category = ?, description = ?, role = ?, goal = ?,
                            system_prompt = ?, default_model = ?, risk_level = ?,
                            allowed_tools_json = ?, input_schema_json = ?,
                            output_schema_json = ?, evaluation_metrics_json = ?,
                            config_json = ?, is_system = 1, is_active = 1, updated_at = ?
                        WHERE id = ?
                        """,
                        (*values, existing["id"]),
                    )
                    continue
                connection.execute(
                    """
                    INSERT INTO agents (
                        id, user_id, name, slug, category, description, role, goal,
                        system_prompt, default_model, temperature, risk_level, is_system,
                        is_active, allowed_tools_json, input_schema_json, output_schema_json,
                        evaluation_metrics_json, config_json, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uuid4().hex,
                        "system",
                        item["name"],
                        item["slug"],
                        item["category"],
                        item["description"],
                        item["role"],
                        item["goal"],
                        item["system_prompt"],
                        item["default_model"],
                        0.2,
                        item["risk_level"],
                        1,
                        1,
                        json.dumps(item["allowed_tools"], ensure_ascii=True),
                        json.dumps(item["input_schema"], ensure_ascii=True),
                        json.dumps(item["output_schema"], ensure_ascii=True),
                        json.dumps(item["evaluation_metrics"], ensure_ascii=True),
                        json.dumps(item["config"], ensure_ascii=True),
                        now,
                        now,
                    ),
                )
            placeholders = ",".join("?" for _ in active_system_slugs)
            connection.execute(
                f"""
                UPDATE agents
                SET is_active = 0, updated_at = ?
                WHERE user_id = 'system' AND slug NOT IN ({placeholders})
                """,
                (now, *active_system_slugs),
            )

    def list_agents(self, user_id: str | None = None, include_inactive: bool = False) -> list[dict[str, Any]]:
        self.ensure_system_agents()
        local_user = user_id or "local"
        clauses = ["(user_id = ? OR user_id = 'system')"]
        values: list[Any] = [local_user]
        if not include_inactive:
            clauses.append("is_active = 1")
        where = " AND ".join(clauses)
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT id, user_id, name, slug, category, description, role, goal,
                       system_prompt, default_model, temperature, risk_level, is_system,
                       is_active, allowed_tools_json, input_schema_json, output_schema_json,
                       evaluation_metrics_json, config_json, created_at, updated_at
                FROM agents
                WHERE {where}
                ORDER BY is_system DESC, category ASC, name ASC
                """,
                tuple(values),
            ).fetchall()
        return [self._decode(row) for row in rows]

    def create_agent(
        self,
        *,
        name: str,
        role: str,
        goal: str = "",
        system_prompt: str = "",
        user_id: str | None = None,
        default_model: str = "ollama",
        temperature: float = 0.2,
        risk_level: str = "low",
        is_active: bool = True,
        config: dict[str, Any] | None = None,
        category: str = "custom",
        description: str = "",
        allowed_tools: list[str] | None = None,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        evaluation_metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        now = utc_now()
        local_user = user_id or "local"
        slug = self._unique_slug(local_user, slugify(name, fallback="agent"))
        agent_id = uuid4().hex
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO agents (
                    id, user_id, name, slug, category, description, role, goal,
                    system_prompt, default_model, temperature, risk_level, is_system,
                    is_active, allowed_tools_json, input_schema_json, output_schema_json,
                    evaluation_metrics_json, config_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    agent_id,
                    local_user,
                    name.strip(),
                    slug,
                    category.strip() or "custom",
                    description.strip(),
                    role.strip() or "custom",
                    goal.strip(),
                    system_prompt.strip(),
                    default_model.strip() or "ollama",
                    float(temperature),
                    risk_level if risk_level in {"low", "medium", "high"} else "low",
                    0,
                    1 if is_active else 0,
                    json.dumps(allowed_tools or [], ensure_ascii=True),
                    json.dumps(input_schema or COMMON_INPUT_SCHEMA, ensure_ascii=True),
                    json.dumps(output_schema or COMMON_OUTPUT_SCHEMA, ensure_ascii=True),
                    json.dumps(evaluation_metrics or DEFAULT_METRICS, ensure_ascii=True),
                    json.dumps(config or {}, ensure_ascii=True),
                    now,
                    now,
                ),
            )
        return self.get_agent(agent_id) or {}

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, user_id, name, slug, category, description, role, goal,
                       system_prompt, default_model, temperature, risk_level, is_system,
                       is_active, allowed_tools_json, input_schema_json, output_schema_json,
                       evaluation_metrics_json, config_json, created_at, updated_at
                FROM agents
                WHERE id = ?
                """,
                (agent_id,),
            ).fetchone()
        return self._decode(row) if row else None

    def get_agent_by_name_or_slug(self, value: str, user_id: str | None = None) -> dict[str, Any] | None:
        self.ensure_system_agents()
        local_user = user_id or "local"
        lookup = value.strip()
        if not lookup:
            return None
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, user_id, name, slug, category, description, role, goal,
                       system_prompt, default_model, temperature, risk_level, is_system,
                       is_active, allowed_tools_json, input_schema_json, output_schema_json,
                       evaluation_metrics_json, config_json, created_at, updated_at
                FROM agents
                WHERE is_active = 1
                  AND (user_id = ? OR user_id = 'system')
                  AND (id = ? OR name = ? OR slug = ?)
                ORDER BY is_system DESC
                LIMIT 1
                """,
                (local_user, lookup, lookup, lookup),
            ).fetchone()
        return self._decode(row) if row else None

    def _unique_slug(self, user_id: str, base_slug: str) -> str:
        slug = base_slug
        with get_connection() as connection:
            index = 2
            while connection.execute("SELECT 1 FROM agents WHERE user_id = ? AND slug = ?", (user_id, slug)).fetchone():
                slug = f"{base_slug}-{index}"
                index += 1
        return slug

    def _decode(self, row: Any) -> dict[str, Any]:
        data = dict(row)
        data["is_system"] = bool(data.get("is_system"))
        data["is_active"] = bool(data.get("is_active"))
        for raw_key, clean_key, fallback in (
            ("allowed_tools_json", "allowed_tools", []),
            ("input_schema_json", "input_schema", COMMON_INPUT_SCHEMA),
            ("output_schema_json", "output_schema", COMMON_OUTPUT_SCHEMA),
            ("evaluation_metrics_json", "evaluation_metrics", DEFAULT_METRICS),
            ("config_json", "config", {}),
        ):
            try:
                data[clean_key] = json.loads(data.pop(raw_key) or json.dumps(fallback))
            except Exception:
                data[clean_key] = fallback
        data.setdefault("category", "custom")
        data.setdefault("description", "")
        return data
