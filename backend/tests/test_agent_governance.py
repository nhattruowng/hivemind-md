import asyncio
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.answer_agent import AnswerAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.verifier_agent import VerifierAgent
from app.services.approval_policy import ApprovalPolicy


class AgentGovernanceTests(unittest.TestCase):
    def test_planner_marks_destructive_action_for_approval(self) -> None:
        result = asyncio.run(
            PlannerAgent().execute(
                request="Xóa file knowledge này và update production database",
                route_data={"supported": True},
                auto_refresh=True,
            )
        )
        data = result["data"]
        self.assertEqual(data["task_type"], "action")
        self.assertEqual(data["risk_level"], "high")
        self.assertTrue(data["approval_required"])
        self.assertTrue(any(step["agent"] == "PolicyAgent" for step in data["steps"]))

    def test_planner_creates_knowledge_build_steps(self) -> None:
        result = asyncio.run(
            PlannerAgent().execute(
                request="AI agent orchestration",
                workflow="knowledge_build",
                category="ai",
                mode="standard",
            )
        )
        steps = result["data"]["steps"]
        self.assertEqual(result["data"]["task_type"], "knowledge_build")
        self.assertIn("SearchAgent", [step["agent"] for step in steps])
        self.assertIn("IndexerAgent", [step["agent"] for step in steps])

    def test_verifier_accepts_grounded_answer_with_citation(self) -> None:
        result = asyncio.run(
            VerifierAgent().execute(
                question="What is HiveMind MD?",
                answer="HiveMind MD stores Markdown knowledge for grounded local RAG. [S1]",
                retrieval=[
                    {
                        "file_path": "docs/architecture.md",
                        "preview": "HiveMind MD stores Markdown knowledge for grounded local RAG.",
                        "sources": ["docs/architecture.md"],
                    }
                ],
                citations=[{"id": "S1", "file_path": "docs/architecture.md"}],
                confidence=0.8,
            )
        )
        data = result["data"]
        self.assertTrue(data["verified"])
        self.assertGreaterEqual(data["grounding_score"], 0.3)

    def test_verifier_flags_unsupported_claims(self) -> None:
        result = asyncio.run(
            VerifierAgent().execute(
                question="What is the deployment cost?",
                answer="The system costs exactly 999 USD per month and runs on a managed cluster.",
                retrieval=[{"file_path": "docs/architecture.md", "preview": "The system runs local-first with Markdown files."}],
                citations=[],
                confidence=0.6,
            )
        )
        data = result["data"]
        self.assertFalse(data["verified"])
        self.assertGreaterEqual(len(data["unsupported_claims"]), 1)
        self.assertIn("citations", data["missing_points"])

    def test_approval_policy_blocks_high_risk_without_approval(self) -> None:
        decision = ApprovalPolicy().evaluate("delete_knowledge", approved=False)
        self.assertTrue(decision.approval_required)
        self.assertFalse(decision.allowed)
        approved = ApprovalPolicy().evaluate("delete_knowledge", approved=True)
        self.assertTrue(approved.allowed)

    def test_answer_agent_appends_citation_section(self) -> None:
        agent = object.__new__(AnswerAgent)
        answer = agent._attach_citations(
            "Short grounded answer.",
            [{"id": "S1", "file_path": "docs/architecture.md", "sources": ["https://example.test/source"]}],
        )
        self.assertIn("Nguồn sử dụng:", answer)
        self.assertIn("[S1]", answer)

    def test_eval_dataset_has_required_cases(self) -> None:
        dataset_path = Path(__file__).resolve().parents[1] / "evals" / "agent_quality_dataset.json"
        dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
        case_types = {case["type"] for case in dataset["cases"]}
        self.assertTrue({"hallucination", "rag_qa", "planning", "verification", "approval"}.issubset(case_types))


if __name__ == "__main__":
    unittest.main()
