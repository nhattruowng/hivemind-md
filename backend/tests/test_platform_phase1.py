import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.agents.intent_classifier_agent import IntentClassifierAgent
from app.config import get_settings
from app.database import get_connection, init_db
from app.memory.memory_service import MemoryService
from app.orchestration.agent_runtime import AgentRuntime
from app.orchestration.planner_service import PlannerRuntimeService
from app.registry.agent_registry import AgentRegistry
from app.registry.tool_registry import ToolRegistry


class PlatformPhase1Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        os.environ["DATABASE_URL"] = f"sqlite:///{self.root / 'test.db'}"
        os.environ["KNOWLEDGE_DIR"] = str(self.root / "knowledge")
        os.environ["VECTOR_STORE_DIR"] = str(self.root / "vector")
        get_settings.cache_clear()
        init_db()

    def tearDown(self) -> None:
        get_settings.cache_clear()
        self.temp_dir.cleanup()

    def test_phase1_tables_are_created(self) -> None:
        expected = {
            "users",
            "user_profiles",
            "user_memories",
            "agents",
            "tools",
            "agent_tools",
            "workflows",
            "workflow_runs",
            "workflow_steps",
            "approval_requests",
            "evaluations",
            "datasets",
            "user_feedbacks",
        }
        with get_connection() as connection:
            rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        names = {row["name"] for row in rows}
        self.assertTrue(expected.issubset(names))
        with get_connection() as connection:
            agent_columns = {row["name"] for row in connection.execute("PRAGMA table_info(agents)").fetchall()}
        self.assertTrue(
            {
                "category",
                "description",
                "allowed_tools_json",
                "input_schema_json",
                "output_schema_json",
                "evaluation_metrics_json",
            }.issubset(agent_columns)
        )

    def test_agent_registry_seeds_system_agents_and_creates_custom_agent(self) -> None:
        registry = AgentRegistry()
        initial = registry.list_agents()
        self.assertTrue(any(agent["slug"] == "planner" for agent in initial))
        created = registry.create_agent(
            name="Research Coach",
            role="research",
            goal="Help with grounded research.",
            system_prompt="Use sources and ask when context is missing.",
        )
        self.assertEqual(created["name"], "Research Coach")
        self.assertFalse(created["is_system"])
        self.assertIn(created["slug"], {agent["slug"] for agent in registry.list_agents()})

    def test_agent_registry_contains_36_structured_system_agents(self) -> None:
        ToolRegistry().ensure_default_tools()
        agents = [agent for agent in AgentRegistry().list_agents() if agent["is_system"]]
        self.assertEqual(len(agents), 36)
        names = {agent["name"] for agent in agents}
        self.assertTrue(
            {
                "IntentClassifierAgent",
                "PlannerAgent",
                "AgentRouterAgent",
                "RAGAgent",
                "HallucinationGuardAgent",
                "MemoryAgent",
                "CodeAgent",
                "RefactorAgent",
            }.issubset(names)
        )
        categories = {agent["category"] for agent in agents}
        self.assertEqual(categories, {"core", "knowledge", "safety", "personalization", "coding_documents"})
        tool_names = {tool["name"] for tool in ToolRegistry().list_tools()}
        for agent in agents:
            with self.subTest(agent=agent["name"]):
                self.assertTrue(agent["description"])
                self.assertTrue(agent["role"])
                self.assertIn(agent["risk_level"], {"low", "medium", "high"})
                self.assertIsInstance(agent["allowed_tools"], list)
                self.assertTrue(set(agent["allowed_tools"]).issubset(tool_names))
                self.assertIn("properties", agent["input_schema"])
                self.assertIn("properties", agent["output_schema"])
                self.assertGreaterEqual(len(agent["evaluation_metrics"]), 2)

    def test_tool_registry_seeds_default_tools(self) -> None:
        tools = ToolRegistry().list_tools()
        names = {tool["name"] for tool in tools}
        self.assertIn("knowledge_search", names)
        self.assertIn("approval_request", names)
        self.assertTrue(any(tool["permission_level"] == "destructive" for tool in tools))

    def test_memory_service_create_list_and_archive(self) -> None:
        service = MemoryService()
        created = service.create_memory(
            content="User prefers concise Vietnamese answers.",
            memory_type="preference",
            confidence=0.9,
            importance=4,
        )
        memories = service.list_memories(memory_type="preference")
        self.assertEqual(memories[0]["id"], created["id"])
        archived = service.archive_memory(created["id"])
        self.assertIsNotNone(archived)
        self.assertIsNotNone(archived["archived_at"])
        self.assertEqual(service.list_memories(memory_type="preference"), [])

    def test_intent_classifier_detects_build_knowledge(self) -> None:
        result = asyncio.run(IntentClassifierAgent().execute(message="Refresh và index tri thức về AI agent"))
        data = result["data"]
        self.assertEqual(data["intent"], "build_knowledge")
        self.assertTrue(data["requires_tools"])
        self.assertGreaterEqual(data["confidence"], 0.8)

    def test_phase1_api_endpoints(self) -> None:
        from app.main import app

        client = TestClient(app)
        agents_response = client.get("/api/agents")
        self.assertEqual(agents_response.status_code, 200)
        self.assertTrue(any(item["slug"] == "verifier" for item in agents_response.json()))

        create_agent = client.post(
            "/api/agents",
            json={
                "name": "Local Analyst",
                "role": "analysis",
                "goal": "Analyze local knowledge.",
                "system_prompt": "Stay grounded.",
            },
        )
        self.assertEqual(create_agent.status_code, 200)
        self.assertEqual(create_agent.json()["name"], "Local Analyst")

        create_memory = client.post(
            "/api/memory",
            json={
                "content": "Project prefers local-first Ollama defaults.",
                "memory_type": "project",
                "importance": 3,
            },
        )
        self.assertEqual(create_memory.status_code, 200)
        memory_response = client.get("/api/memory?memory_type=project")
        self.assertEqual(memory_response.status_code, 200)
        self.assertEqual(len(memory_response.json()), 1)

        preview = client.post("/api/chat/plan-preview", json={"message": "Tìm và cập nhật tri thức về RAG"})
        self.assertEqual(preview.status_code, 200)
        preview_data = preview.json()
        self.assertIn("plan", preview_data)
        self.assertIn("PlannerAgent", preview_data["agents_used"])
        self.assertIn("timeline", preview_data)
        self.assertIn("routing", preview_data)

    def test_agent_router_and_runtime_preview_select_registered_agents(self) -> None:
        preview = asyncio.run(PlannerRuntimeService().preview(message="Giải thích RAG là gì?"))
        self.assertIn("AgentRouterAgent", [item["agent"] for item in preview["timeline"]])
        selected = preview["routing"]["selected_agents"]
        self.assertIn("RAGAgent", selected)
        self.assertTrue(preview["routing"]["assignments"])

    def test_agent_runtime_executes_functional_agent(self) -> None:
        agent = AgentRegistry().get_agent_by_name_or_slug("IntentClassifierAgent")
        self.assertIsNotNone(agent)
        result = asyncio.run(
            AgentRuntime().execute_registered_agent(
                agent["id"],
                input_data={"message": "Debug lỗi backend"},
                record_run=False,
            )
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["intent"], "debug")

    def test_agent_test_endpoint_returns_timeline(self) -> None:
        from app.main import app

        client = TestClient(app)
        agent = next(item for item in client.get("/api/agents").json() if item["name"] == "PlannerAgent")
        response = client.post(
            f"/api/agents/{agent['id']}/test",
            json={"input": {"message": "Tìm và cập nhật tri thức về RAG"}},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["agent"]["name"], "PlannerAgent")
        self.assertEqual(data["timeline"][0]["agent"], "PlannerAgent")
        self.assertIn("steps", data["result"]["data"])

    def test_chat_endpoint_returns_chat_first_runtime_metadata(self) -> None:
        from app.main import app

        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={
                "message": "RAG là gì?",
                "auto_refresh": False,
                "category": "chat-auto",
                "mode": "quick",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        timeline_agents = {item["agent"] for item in data["timeline"]}
        self.assertIn("IntentClassifierAgent", timeline_agents)
        self.assertIn("ContextBuilderAgent", timeline_agents)
        self.assertIn("AgentRouterAgent", timeline_agents)
        self.assertIn("CitationAgent", timeline_agents)
        self.assertIn("MemoryAgent", timeline_agents)
        self.assertIn("routing", data)
        self.assertIn("context", data)
        self.assertTrue(data["agents_used"])


if __name__ == "__main__":
    unittest.main()
