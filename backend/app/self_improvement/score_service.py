from datetime import datetime, timezone
from typing import Any

from app.database import get_connection
from app.self_improvement.schemas import AgentRunCreate, WorkflowSuggestionCreate


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ScoreService:
    def record_agent_run(
        self,
        task_id: str,
        task: str,
        agent_name: str,
        input: str | None = None,
        output: str | None = None,
        score: float | None = None,
        status: str = "success",
        error_message: str | None = None,
        runtime_ms: int | None = None,
    ) -> int:
        payload = AgentRunCreate(
            task_id=task_id,
            task=task,
            agent_name=agent_name,
            input=input,
            output=output,
            score=score,
            status="success" if status == "success" else "failed",
            error_message=error_message,
            runtime_ms=runtime_ms,
        )
        now = utc_now()
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO agent_runs (
                    task_id, task, agent_name, input, output, score, status,
                    error_message, runtime_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.task_id,
                    payload.task,
                    payload.agent_name,
                    payload.input,
                    payload.output,
                    payload.score,
                    payload.status,
                    payload.error_message,
                    payload.runtime_ms,
                    now,
                ),
            )
            run_id = int(cursor.lastrowid)
        self.update_scoreboard(agent_name)
        return run_id

    def update_run_score(self, run_id: int, score: float) -> None:
        with get_connection() as connection:
            row = connection.execute("SELECT agent_name FROM agent_runs WHERE id = ?", (run_id,)).fetchone()
            if not row:
                return
            connection.execute("UPDATE agent_runs SET score = ? WHERE id = ?", (float(score), run_id))
            agent_name = str(row["agent_name"])
        self.update_scoreboard(agent_name)

    def update_scoreboard(self, agent_name: str) -> None:
        now = utc_now()
        with get_connection() as connection:
            stats = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_runs,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success_runs,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_runs,
                    AVG(score) AS average_score,
                    AVG(runtime_ms) AS average_runtime_ms
                FROM agent_runs
                WHERE agent_name = ?
                """,
                (agent_name,),
            ).fetchone()
            if not stats:
                return
            connection.execute(
                """
                INSERT INTO agent_scoreboard (
                    agent_name, total_runs, success_runs, failed_runs,
                    average_score, average_runtime_ms, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(agent_name) DO UPDATE SET
                    total_runs = excluded.total_runs,
                    success_runs = excluded.success_runs,
                    failed_runs = excluded.failed_runs,
                    average_score = excluded.average_score,
                    average_runtime_ms = excluded.average_runtime_ms,
                    updated_at = excluded.updated_at
                """,
                (
                    agent_name,
                    int(stats["total_runs"] or 0),
                    int(stats["success_runs"] or 0),
                    int(stats["failed_runs"] or 0),
                    round(float(stats["average_score"] or 0), 2),
                    int(float(stats["average_runtime_ms"] or 0)),
                    now,
                ),
            )

    def list_agent_runs(
        self,
        agent_name: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        values: list[Any] = []
        if agent_name:
            clauses.append("agent_name = ?")
            values.append(agent_name)
        if status:
            clauses.append("status = ?")
            values.append(status)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        values.append(max(1, min(int(limit or 50), 500)))
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT id, task_id, task, agent_name, input, output, score, status,
                       error_message, runtime_ms, created_at
                FROM agent_runs
                {where}
                ORDER BY created_at DESC
                LIMIT ?
                """,
                tuple(values),
            ).fetchall()
        return [dict(row) for row in rows]

    def create_workflow_suggestion(
        self,
        task_id: str,
        suggestion: str,
        expected_benefit: str | None = None,
        risk_level: str = "medium",
        status: str = "pending",
    ) -> dict[str, Any]:
        payload = WorkflowSuggestionCreate(
            task_id=task_id,
            suggestion=suggestion,
            expected_benefit=expected_benefit,
            risk_level=risk_level if risk_level in {"low", "medium", "high"} else "medium",
            status=status if status in {"pending", "applied", "rejected"} else "pending",
        )
        now = utc_now()
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO workflow_suggestions (
                    task_id, suggestion, expected_benefit, risk_level, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.task_id,
                    payload.suggestion,
                    payload.expected_benefit,
                    payload.risk_level,
                    payload.status,
                    now,
                    now,
                ),
            )
            suggestion_id = int(cursor.lastrowid)
        return self.get_workflow_suggestion(suggestion_id)

    def get_workflow_suggestion(self, suggestion_id: int) -> dict[str, Any]:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, task_id, suggestion, expected_benefit, risk_level, status, created_at, updated_at
                FROM workflow_suggestions
                WHERE id = ?
                """,
                (suggestion_id,),
            ).fetchone()
        return dict(row) if row else {}

    def list_workflow_suggestions(
        self,
        status: str | None = None,
        risk_level: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        values: list[Any] = []
        if status:
            clauses.append("status = ?")
            values.append(status)
        if risk_level:
            clauses.append("risk_level = ?")
            values.append(risk_level)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT id, task_id, suggestion, expected_benefit, risk_level, status, created_at, updated_at
                FROM workflow_suggestions
                {where}
                ORDER BY updated_at DESC
                """,
                tuple(values),
            ).fetchall()
        return [dict(row) for row in rows]

    def update_workflow_suggestion_status(self, suggestion_id: int, status: str) -> dict[str, Any]:
        now = utc_now()
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE workflow_suggestions
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, now, suggestion_id),
            )
        return self.get_workflow_suggestion(suggestion_id)

    def get_summary(self) -> dict[str, Any]:
        with get_connection() as connection:
            run_stats = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_runs,
                    AVG(score) AS average_score,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success_runs
                FROM agent_runs
                """
            ).fetchone()
            total_lessons = connection.execute("SELECT COUNT(*) AS total FROM improvement_lessons").fetchone()
            prompt_versions = connection.execute("SELECT COUNT(*) AS total FROM prompt_versions").fetchone()
            pending = connection.execute(
                "SELECT COUNT(*) AS total FROM workflow_suggestions WHERE status = 'pending'"
            ).fetchone()
        total_runs = int(run_stats["total_runs"] or 0)
        success_runs = int(run_stats["success_runs"] or 0)
        return {
            "total_runs": total_runs,
            "average_score": round(float(run_stats["average_score"] or 0), 2),
            "success_rate": round((success_runs / total_runs) * 100, 2) if total_runs else 0,
            "total_lessons": int(total_lessons["total"] or 0),
            "total_prompt_versions": int(prompt_versions["total"] or 0),
            "pending_workflow_suggestions": int(pending["total"] or 0),
        }
