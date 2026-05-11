from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.database import get_connection
from app.utils.text_utils import normalize_whitespace


MEMORY_TYPES = {"preference", "project", "fact", "workflow", "skill", "correction", "temporary"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryService:
    def list_memories(
        self,
        *,
        user_id: str | None = None,
        memory_type: str | None = None,
        include_archived: bool = False,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        local_user = user_id or "local"
        clauses = ["user_id = ?"]
        values: list[Any] = [local_user]
        if memory_type:
            clauses.append("memory_type = ?")
            values.append(memory_type)
        if not include_archived:
            clauses.append("archived_at IS NULL")
        values.append(max(1, min(int(limit or 100), 500)))
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT id, user_id, memory_type, content, source, confidence, importance,
                       expires_at, created_at, updated_at, archived_at
                FROM user_memories
                WHERE {' AND '.join(clauses)}
                ORDER BY importance DESC, updated_at DESC
                LIMIT ?
                """,
                tuple(values),
            ).fetchall()
        return [dict(row) for row in rows]

    def create_memory(
        self,
        *,
        content: str,
        memory_type: str = "fact",
        user_id: str | None = None,
        source: str = "manual",
        confidence: float = 0.7,
        importance: int = 1,
        expires_at: str | None = None,
    ) -> dict[str, Any]:
        cleaned = normalize_whitespace(content)
        if not cleaned:
            raise ValueError("Memory content is required.")
        now = utc_now()
        memory_id = uuid4().hex
        normalized_type = memory_type if memory_type in MEMORY_TYPES else "fact"
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO user_memories (
                    id, user_id, memory_type, content, source, confidence, importance,
                    expires_at, created_at, updated_at, archived_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                """,
                (
                    memory_id,
                    user_id or "local",
                    normalized_type,
                    cleaned,
                    source,
                    max(0.0, min(float(confidence), 1.0)),
                    max(1, min(int(importance or 1), 5)),
                    expires_at,
                    now,
                    now,
                ),
            )
        return self.get_memory(memory_id) or {}

    def archive_memory(self, memory_id: str, *, user_id: str | None = None) -> dict[str, Any] | None:
        now = utc_now()
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE user_memories
                SET archived_at = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (now, now, memory_id, user_id or "local"),
            )
        return self.get_memory(memory_id)

    def get_memory(self, memory_id: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, user_id, memory_type, content, source, confidence, importance,
                       expires_at, created_at, updated_at, archived_at
                FROM user_memories
                WHERE id = ?
                """,
                (memory_id,),
            ).fetchone()
        return dict(row) if row else None
