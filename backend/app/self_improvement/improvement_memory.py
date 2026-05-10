from pathlib import Path
from typing import Any

from app.config import Settings, get_settings
from app.database import get_connection
from app.self_improvement.schemas import ReflectionLessonCreate
from app.self_improvement.score_service import utc_now


LESSON_FILE_BY_TYPE = {
    "prompt": "prompt-lessons.md",
    "workflow": "workflow-lessons.md",
    "tool": "tool-usage-lessons.md",
    "error": "error-patterns.md",
    "success": "successful-strategies.md",
    "failed": "failed-strategies.md",
}


class ImprovementMemory:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.memory_dir = self.settings.knowledge_path / "self-improvement"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_memory_files()

    def save_lesson(
        self,
        title: str,
        lesson_type: str,
        content: str,
        agent_name: str | None = None,
        task_id: str | None = None,
        status: str = "active",
    ) -> dict[str, Any]:
        payload = ReflectionLessonCreate(
            title=title.strip() or "Reusable improvement lesson",
            lesson_type=lesson_type if lesson_type in LESSON_FILE_BY_TYPE else "prompt",
            agent_name=agent_name,
            task_id=task_id,
            content=content.strip(),
            status="archived" if status == "archived" else "active",
        )
        now = utc_now()
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO improvement_lessons (
                    title, lesson_type, agent_name, task_id, content, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.title,
                    payload.lesson_type,
                    payload.agent_name,
                    payload.task_id,
                    payload.content,
                    payload.status,
                    now,
                    now,
                ),
            )
            lesson_id = int(cursor.lastrowid)
        lesson = self.get_lesson(lesson_id)
        self._append_lesson_markdown(lesson)
        return lesson

    def get_lesson(self, lesson_id: int) -> dict[str, Any]:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, title, lesson_type, agent_name, task_id, content, status, created_at, updated_at
                FROM improvement_lessons
                WHERE id = ?
                """,
                (lesson_id,),
            ).fetchone()
        return dict(row) if row else {}

    def list_lessons(
        self,
        agent_name: str | None = None,
        lesson_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        values: list[Any] = []
        if agent_name:
            clauses.append("agent_name = ?")
            values.append(agent_name)
        if lesson_type:
            clauses.append("lesson_type = ?")
            values.append(lesson_type)
        if status:
            clauses.append("status = ?")
            values.append(status)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT id, title, lesson_type, agent_name, task_id, content, status, created_at, updated_at
                FROM improvement_lessons
                {where}
                ORDER BY created_at DESC
                """,
                tuple(values),
            ).fetchall()
        return [dict(row) for row in rows]

    def search_lessons(
        self,
        agent_name: str | None = None,
        lesson_type: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        lessons = self.list_lessons(agent_name=agent_name, lesson_type=lesson_type, status="active")
        return lessons[: max(1, limit)]

    def archive_lesson(self, lesson_id: int) -> dict[str, Any]:
        now = utc_now()
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE improvement_lessons
                SET status = 'archived', updated_at = ?
                WHERE id = ?
                """,
                (now, lesson_id),
            )
        return self.get_lesson(lesson_id)

    def _ensure_memory_files(self) -> None:
        for lesson_type, filename in LESSON_FILE_BY_TYPE.items():
            path = self.memory_dir / filename
            if not path.exists():
                title = lesson_type.replace("-", " ").replace("_", " ").title()
                path.write_text(f"# {title}\n\n", encoding="utf-8")
        scoreboard = self.memory_dir / "agent-scoreboard.md"
        if not scoreboard.exists():
            scoreboard.write_text("# Agent Scoreboard\n\n", encoding="utf-8")

    def _append_lesson_markdown(self, lesson: dict[str, Any]) -> None:
        if not lesson:
            return
        filename = LESSON_FILE_BY_TYPE.get(str(lesson.get("lesson_type")), "prompt-lessons.md")
        path = self._resolve_memory_file(filename)
        block = [
            "",
            f"## Lesson {lesson.get('id')} - {lesson.get('title')}",
            "",
            "### Agent",
            str(lesson.get("agent_name") or "N/A"),
            "",
            "### Context",
            f"Task ID: {lesson.get('task_id') or 'N/A'}",
            "",
            "### Problem / Weakness",
            str(lesson.get("content") or "").strip() or "N/A",
            "",
            "### Improved Strategy",
            "Apply the reusable lesson above before running a similar task again.",
            "",
            "### When To Apply",
            "When a similar task, agent, or failure pattern appears.",
            "",
            "### Status",
            str(lesson.get("status") or "active").title(),
            "",
            "### Created At",
            str(lesson.get("created_at") or ""),
            "",
        ]
        with path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(block))

    def _resolve_memory_file(self, filename: str) -> Path:
        path = self.memory_dir / filename
        path.resolve().relative_to(self.memory_dir.resolve())
        return path
