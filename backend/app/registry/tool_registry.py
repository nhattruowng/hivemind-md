import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.database import get_connection


DEFAULT_TOOLS = [
    ("knowledge_search", "Search indexed Markdown knowledge.", "public"),
    ("markdown_read", "Read Markdown inside the app-owned knowledge base.", "public"),
    ("markdown_write", "Write Markdown inside the app-owned knowledge base.", "private"),
    ("vector_search", "Search vector chunks.", "public"),
    ("web_search", "Search the web for candidate sources.", "public"),
    ("web_crawl", "Fetch and extract source page content.", "public"),
    ("code_read", "Read project files.", "private"),
    ("code_write", "Modify project files.", "destructive"),
    ("run_tests", "Run project test commands.", "private"),
    ("sqlite_query", "Query app-owned SQLite tables.", "private"),
    ("memory_read", "Read user memories.", "private"),
    ("memory_write", "Create or update user memories.", "private"),
    ("approval_request", "Create a human approval request.", "sensitive"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ToolRegistry:
    def ensure_default_tools(self) -> None:
        now = utc_now()
        retry_policy = {"max_retries": 2, "backoff": "exponential"}
        with get_connection() as connection:
            for name, description, permission_level in DEFAULT_TOOLS:
                existing = connection.execute("SELECT id FROM tools WHERE name = ?", (name,)).fetchone()
                if existing:
                    continue
                connection.execute(
                    """
                    INSERT INTO tools (
                        id, name, description, input_schema_json, output_schema_json,
                        permission_level, timeout_seconds, retry_policy_json, is_active,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uuid4().hex,
                        name,
                        description,
                        "{}",
                        "{}",
                        permission_level,
                        30,
                        json.dumps(retry_policy, ensure_ascii=True),
                        1,
                        now,
                        now,
                    ),
                )

    def list_tools(self, include_inactive: bool = False) -> list[dict[str, Any]]:
        self.ensure_default_tools()
        where = "" if include_inactive else "WHERE is_active = 1"
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT id, name, description, input_schema_json, output_schema_json,
                       permission_level, timeout_seconds, retry_policy_json, is_active,
                       created_at, updated_at
                FROM tools
                {where}
                ORDER BY name ASC
                """
            ).fetchall()
        return [self._decode(row) for row in rows]

    def create_tool(
        self,
        *,
        name: str,
        description: str = "",
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        permission_level: str = "public",
        timeout_seconds: int = 30,
        retry_policy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = utc_now()
        tool_id = uuid4().hex
        permission = permission_level if permission_level in {"public", "private", "sensitive", "destructive"} else "public"
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO tools (
                    id, name, description, input_schema_json, output_schema_json,
                    permission_level, timeout_seconds, retry_policy_json, is_active,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tool_id,
                    name.strip(),
                    description.strip(),
                    json.dumps(input_schema or {}, ensure_ascii=True),
                    json.dumps(output_schema or {}, ensure_ascii=True),
                    permission,
                    int(timeout_seconds or 30),
                    json.dumps(retry_policy or {"max_retries": 2, "backoff": "exponential"}, ensure_ascii=True),
                    1,
                    now,
                    now,
                ),
            )
        return self.get_tool(tool_id) or {}

    def get_tool(self, tool_id: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, name, description, input_schema_json, output_schema_json,
                       permission_level, timeout_seconds, retry_policy_json, is_active,
                       created_at, updated_at
                FROM tools
                WHERE id = ?
                """,
                (tool_id,),
            ).fetchone()
        return self._decode(row) if row else None

    def _decode(self, row: Any) -> dict[str, Any]:
        data = dict(row)
        data["is_active"] = bool(data.get("is_active"))
        for raw_key, clean_key in (
            ("input_schema_json", "input_schema"),
            ("output_schema_json", "output_schema"),
            ("retry_policy_json", "retry_policy"),
        ):
            try:
                data[clean_key] = json.loads(data.pop(raw_key) or "{}")
            except Exception:
                data[clean_key] = {}
        return data
