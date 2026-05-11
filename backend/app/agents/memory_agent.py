from typing import Any

from app.agents.base_agent import BaseAgent
from app.memory.memory_service import MemoryService
from app.utils.text_utils import compact_preview, normalize_whitespace


MEMORY_COMMANDS = ("remember", "save this", "nhớ", "ghi nhớ", "lưu lại", "luu lai")


class MemoryAgent(BaseAgent):
    name = "MemoryAgent"
    description = "Persist explicit user memory requests without saving incidental chat facts."

    def __init__(self, memory_service: MemoryService | None = None) -> None:
        self.memory_service = memory_service or MemoryService()

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        message = normalize_whitespace(str(kwargs.get("message") or ""))
        user_id = kwargs.get("user_id")
        if not self._should_save(message):
            return self.success(
                "No explicit memory write requested.",
                {"saved": False, "reason": "memory_write_not_requested"},
                confidence=0.78,
            )
        content = self._memory_content(message)
        memory = self.memory_service.create_memory(
            content=content,
            memory_type="preference" if self._looks_like_preference(content) else "fact",
            user_id=user_id,
            source="chat",
            confidence=0.76,
            importance=3,
        )
        return self.success(
            "Saved explicit chat memory.",
            {"saved": True, "memory": memory},
            confidence=0.9,
        )

    def _should_save(self, message: str) -> bool:
        lowered = message.lower()
        return any(command in lowered for command in MEMORY_COMMANDS)

    def _memory_content(self, message: str) -> str:
        content = message
        for command in MEMORY_COMMANDS:
            content = content.replace(command, "", 1)
            content = content.replace(command.capitalize(), "", 1)
        return compact_preview(normalize_whitespace(content).strip(":：- "), 600) or compact_preview(message, 600)

    def _looks_like_preference(self, content: str) -> bool:
        lowered = content.lower()
        return any(term in lowered for term in ("prefer", "thích", "muốn", "style", "format", "giọng", "ngắn gọn"))
