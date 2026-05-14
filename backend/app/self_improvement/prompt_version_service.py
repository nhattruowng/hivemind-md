import re
from typing import Any

from app.database import get_connection
from app.self_improvement.schemas import PromptVersionCreate
from app.self_improvement.score_service import utc_now


class PromptVersionService:
    def create_prompt_version(
        self,
        agent_name: str,
        prompt: str,
        risk_level: str,
        change_reason: str | None,
        score: float | None = None,
    ) -> dict[str, Any]:
        payload = PromptVersionCreate(
            agent_name=agent_name,
            prompt=prompt.strip(),
            risk_level=risk_level if risk_level in {"low", "medium", "high"} else "medium",
            change_reason=change_reason,
            score=score,
        )
        version = self._next_version(payload.agent_name)
        now = utc_now()
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO prompt_versions (
                    agent_name, version, prompt, score, is_active, risk_level, change_reason, created_at
                ) VALUES (?, ?, ?, ?, 0, ?, ?, ?)
                """,
                (
                    payload.agent_name,
                    version,
                    payload.prompt,
                    payload.score,
                    payload.risk_level,
                    payload.change_reason,
                    now,
                ),
            )
            version_id = int(cursor.lastrowid)
        return self.get_prompt_version(version_id)

    def get_active_prompt(self, agent_name: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, agent_name, version, prompt, score, is_active, risk_level, change_reason, created_at
                FROM prompt_versions
                WHERE agent_name = ? AND is_active = 1
                ORDER BY id DESC
                LIMIT 1
                """,
                (agent_name,),
            ).fetchone()
        return dict(row) if row else None

    def get_prompt_version(self, version_id: int) -> dict[str, Any]:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, agent_name, version, prompt, score, is_active, risk_level, change_reason, created_at
                FROM prompt_versions
                WHERE id = ?
                """,
                (version_id,),
            ).fetchone()
        return dict(row) if row else {}

    def list_prompt_versions(self, agent_name: str | None = None) -> list[dict[str, Any]]:
        values: tuple[Any, ...] = (agent_name,) if agent_name else ()
        where = "WHERE agent_name = ?" if agent_name else ""
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT id, agent_name, version, prompt, score, is_active, risk_level, change_reason, created_at
                FROM prompt_versions
                {where}
                ORDER BY created_at DESC
                """,
                values,
            ).fetchall()
        return [dict(row) for row in rows]

    def activate_prompt_version(self, version_id: int) -> dict[str, Any]:
        version = self.get_prompt_version(version_id)
        if not version:
            return {}
        with get_connection() as connection:
            connection.execute(
                "UPDATE prompt_versions SET is_active = 0 WHERE agent_name = ?",
                (version["agent_name"],),
            )
            connection.execute("UPDATE prompt_versions SET is_active = 1 WHERE id = ?", (version_id,))
        return self.get_prompt_version(version_id)

    def _next_version(self, agent_name: str) -> str:
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT version FROM prompt_versions WHERE agent_name = ?",
                (agent_name,),
            ).fetchall()
        numbers: list[int] = []
        for row in rows:
            match = re.fullmatch(r"v(\d+)", str(row["version"]))
            if match:
                numbers.append(int(match.group(1)))
        return f"v{(max(numbers) if numbers else 0) + 1}"
