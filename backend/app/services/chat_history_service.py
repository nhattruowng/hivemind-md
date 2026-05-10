import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.config import Settings, get_settings
from app.utils.file_utils import ensure_inside, relative_to_base
from app.utils.text_utils import compact_preview, slugify


SESSION_RE = re.compile(r"[^a-zA-Z0-9_-]+")


class ChatHistoryService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def append_turn(
        self,
        question: str,
        answer: str,
        *,
        conversation_id: str | None = None,
        related_files: list[str] | None = None,
        sources: list[str] | None = None,
        auto_refreshed: bool = False,
        updated_files: list[str] | None = None,
    ) -> dict[str, str]:
        session_id = self._normalize_session_id(conversation_id)
        history_path = self._session_path(session_id)
        history_path.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()

        if not history_path.exists():
            title = slugify(question, fallback="chat")[:48]
            history_path.write_text(
                "\n".join(
                    [
                        f"# Chat Session {session_id}",
                        "",
                        "## Mục đích",
                        "",
                        "Lưu lịch sử hỏi đáp với kho tri thức dưới dạng Markdown. File này không được index trực tiếp để tránh làm nhiễu RAG.",
                        "",
                        "## Metadata",
                        "",
                        f"- Created: `{now}`",
                        f"- Title: `{title}`",
                        "",
                        "<!-- hivemind-md:metadata",
                        json.dumps(
                            {
                                "title": f"Chat {title}",
                                "category": "_chat_history",
                                "updated_at": now,
                                "chat_history": True,
                            },
                            ensure_ascii=True,
                        ),
                        "-->",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

        block = "\n".join(
            [
                "",
                "---",
                "",
                f"## Turn {now}",
                "",
                "### User",
                "",
                question.strip(),
                "",
                "### Assistant",
                "",
                answer.strip(),
                "",
                "### Retrieval",
                "",
                f"- Auto refreshed: `{str(auto_refreshed).lower()}`",
                f"- Related files: `{', '.join(related_files or []) or 'none'}`",
                f"- Updated files: `{', '.join(updated_files or []) or 'none'}`",
                "",
                "### Sources",
                "",
                self._source_lines(sources or []),
                "",
            ]
        )
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(block)

        return {
            "conversation_id": session_id,
            "chat_file": relative_to_base(self.settings.knowledge_path, history_path),
            "preview": compact_preview(block, 500),
        }

    def _session_path(self, session_id: str) -> Path:
        return ensure_inside(self.settings.knowledge_path, self.settings.knowledge_path / "_chat_history" / f"{session_id}.md")

    def _normalize_session_id(self, value: str | None) -> str:
        if value:
            cleaned = SESSION_RE.sub("-", value).strip("-")[:96]
            if cleaned:
                return cleaned
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"{timestamp}-{uuid4().hex[:8]}"

    def _source_lines(self, sources: list[str]) -> str:
        if not sources:
            return "- Không có nguồn."
        return "\n".join(f"- {source}" for source in sources[:20])
