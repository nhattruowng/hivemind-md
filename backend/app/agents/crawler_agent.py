from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.crawler_service import CrawlerService


class CrawlerAgent(BaseAgent):
    name = "CrawlerAgent"
    description = "Crawl raw text from source URLs."

    def __init__(self, crawler_service: CrawlerService | None = None) -> None:
        self.crawler_service = crawler_service or CrawlerService()

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        sources = kwargs.get("sources", [])
        documents = await self.crawler_service.crawl_many(sources)
        successful = [doc for doc in documents if doc.get("status") == "success" and doc.get("raw_text")]
        return self.success(
            f"Crawled {len(successful)}/{len(documents)} source(s).",
            {"documents": documents},
        )

