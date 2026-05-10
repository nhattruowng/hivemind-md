import asyncio
import logging
from typing import Any

from app.utils.source_utils import is_low_value_source
from app.utils.text_utils import slugify


logger = logging.getLogger(__name__)


class WebSearchService:
    async def search(self, topic: str, limit: int) -> list[dict[str, str]]:
        try:
            results = await asyncio.to_thread(self._duckduckgo_search, topic, limit)
            if results:
                return results[:limit]
        except Exception as exc:
            logger.warning("DuckDuckGo search failed: %s", exc)
        return self._fallback_sources(topic, limit)

    def _duckduckgo_search(self, topic: str, limit: int) -> list[dict[str, str]]:
        try:
            from ddgs import DDGS
        except Exception as exc:
            logger.info("ddgs is unavailable, trying legacy duckduckgo_search: %s", exc)
            try:
                from duckduckgo_search import DDGS
            except Exception as legacy_exc:
                logger.info("duckduckgo_search is unavailable: %s", legacy_exc)
                return []

        normalized: list[dict[str, str]] = []
        with DDGS() as ddgs:
            for item in ddgs.text(topic, max_results=limit):
                if not isinstance(item, dict):
                    continue
                url = str(item.get("href") or item.get("url") or "").strip()
                if not url:
                    continue
                normalized.append(
                    {
                        "title": str(item.get("title") or url),
                        "url": url,
                        "snippet": str(item.get("body") or item.get("snippet") or ""),
                    }
                )
        return [source for source in normalized if not is_low_value_source(source)]

    def _fallback_sources(self, topic: str, limit: int) -> list[dict[str, str]]:
        slug = slugify(topic)
        seeds: list[dict[str, Any]] = [
            {
                "title": f"Search fallback for {topic}",
                "url": f"local://search/{slug}",
                "snippet": (
                    "Live web search was not available in this environment. "
                    "The workflow can still create a limited Markdown note and mark source confidence as low."
                ),
            }
        ]
        return seeds[: max(1, min(limit, len(seeds)))]
