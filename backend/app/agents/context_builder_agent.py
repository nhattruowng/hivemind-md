from typing import Any

from app.agents.base_agent import BaseAgent
from app.memory.memory_service import MemoryService
from app.utils.text_utils import compact_preview, normalize_whitespace


class ContextBuilderAgent(BaseAgent):
    name = "ContextBuilderAgent"
    description = "Build compact chat context from memory, knowledge routes, and request metadata."

    def __init__(self, memory_service: MemoryService | None = None) -> None:
        self.memory_service = memory_service or MemoryService()

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        message = normalize_whitespace(str(kwargs.get("message") or kwargs.get("request") or ""))
        user_id = kwargs.get("user_id")
        route_data = kwargs.get("route") if isinstance(kwargs.get("route"), dict) else {}
        memories = self.memory_service.list_memories(user_id=user_id, limit=8)
        relevant_memories = self._relevant_memories(message, memories)
        context = {
            "user_id": user_id or "local",
            "request_preview": compact_preview(message, 300),
            "memories": relevant_memories,
            "knowledge_routes": route_data.get("top_routes", [])[:5] if isinstance(route_data.get("top_routes"), list) else [],
            "primary_folder": route_data.get("primary_folder", ""),
            "primary_category": route_data.get("primary_category", ""),
            "permissions": {
                "local_knowledge_read": True,
                "local_knowledge_write": True,
                "destructive_actions": False,
            },
        }
        return self.success(
            "Built chat context from memory and knowledge routes.",
            context,
            confidence=0.84 if relevant_memories or route_data.get("supported") else 0.62,
        )

    def _relevant_memories(self, message: str, memories: list[dict[str, Any]]) -> list[dict[str, Any]]:
        terms = {term.lower() for term in message.split() if len(term) > 2}
        scored: list[tuple[int, int, dict[str, Any]]] = []
        for item in memories:
            content = str(item.get("content", ""))
            lowered = content.lower()
            overlap = sum(1 for term in terms if term in lowered)
            importance = int(item.get("importance") or 1)
            if overlap > 0 or item.get("memory_type") in {"preference", "project"}:
                scored.append((overlap, importance, item))
        scored.sort(key=lambda value: (value[0], value[1]), reverse=True)
        return [
            {
                "id": item.get("id"),
                "memory_type": item.get("memory_type"),
                "content": item.get("content"),
                "source": item.get("source"),
                "confidence": item.get("confidence"),
                "importance": item.get("importance"),
            }
            for _, _, item in scored[:6]
        ]
