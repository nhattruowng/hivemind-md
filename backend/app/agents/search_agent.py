from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.web_search_service import WebSearchService


class SearchAgent(BaseAgent):
    name = "SearchAgent"
    description = "Generate search keywords and find relevant source URLs."

    def __init__(self, search_service: WebSearchService | None = None) -> None:
        self.search_service = search_service or WebSearchService()

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        topic = str(kwargs["topic"])
        limit = int(kwargs.get("limit", 5))
        keywords = [topic, f"{topic} overview", f"{topic} architecture"]
        sources = await self.search_service.search(topic, limit)
        return self.success(f"Found {len(sources)} source(s).", {"keywords": keywords, "sources": sources})

