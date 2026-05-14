import json
from datetime import datetime, timezone
from typing import Any

from app.database import get_connection


class MetadataService:
    def upsert_item(
        self,
        title: str,
        slug: str,
        category: str,
        file_path: str,
        sources: list[dict[str, Any]],
        trust_score: float,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        sources_json = json.dumps(sources, ensure_ascii=True)
        with get_connection() as connection:
            existing = connection.execute(
                "SELECT created_at FROM knowledge_items WHERE slug = ?",
                (slug,),
            ).fetchone()
            created_at = existing["created_at"] if existing else now
            connection.execute(
                """
                INSERT INTO knowledge_items (
                    title, slug, category, file_path, sources, trust_score, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    title = excluded.title,
                    category = excluded.category,
                    file_path = excluded.file_path,
                    sources = excluded.sources,
                    trust_score = excluded.trust_score,
                    updated_at = excluded.updated_at
                """,
                (title, slug, category, file_path, sources_json, trust_score, created_at, now),
            )

    def list_items(self) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT title, category, file_path, updated_at, trust_score
                FROM knowledge_items
                ORDER BY updated_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def delete_item(self, file_path: str) -> bool:
        with get_connection() as connection:
            cursor = connection.execute("DELETE FROM knowledge_items WHERE file_path = ?", (file_path,))
            return cursor.rowcount > 0

