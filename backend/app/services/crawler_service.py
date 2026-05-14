import asyncio
import logging
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.config import Settings, get_settings
from app.utils.text_utils import clean_text


logger = logging.getLogger(__name__)


class CrawlerService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def crawl_many(self, sources: list[dict[str, str]]) -> list[dict[str, Any]]:
        tasks = [self.crawl_source(source) for source in sources]
        return await asyncio.gather(*tasks)

    async def crawl_source(self, source: dict[str, str]) -> dict[str, Any]:
        url = source.get("url", "")
        title = source.get("title", url)
        if url.startswith("local://"):
            return {
                "url": url,
                "title": title,
                "raw_text": source.get("snippet", ""),
                "status": "success",
            }

        try:
            html = await self._fetch_html(url)
            raw_text = await asyncio.to_thread(self._trafilatura_extract_html, html, url)
            if not raw_text:
                raw_text = self._beautifulsoup_extract_html(html)
            return {
                "url": url,
                "title": title,
                "raw_text": clean_text(raw_text or ""),
                "status": "success" if raw_text else "failed",
            }
        except Exception as exc:
            logger.warning("Failed to crawl %s: %s", url, exc)
            return {"url": url, "title": title, "raw_text": "", "status": "failed"}

    async def _fetch_html(self, url: str) -> str:
        async with httpx.AsyncClient(
            timeout=self.settings.request_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "HiveMindMD/0.1 local knowledge crawler"},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def _trafilatura_extract_html(self, html: str, url: str) -> str:
        try:
            import trafilatura
        except Exception:
            return ""

        try:
            return trafilatura.extract(html, url=url, include_comments=False, include_tables=False) or ""
        except Exception as exc:
            logger.info("Trafilatura extraction failed for %s: %s", url, exc)
            return ""

    def _beautifulsoup_extract_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "aside", "noscript", "form"]):
            tag.decompose()
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        body_text = soup.get_text("\n")
        return clean_text(f"{title}\n\n{body_text}")
