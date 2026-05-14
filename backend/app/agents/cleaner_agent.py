from typing import Any

from app.agents.base_agent import BaseAgent
from app.utils.text_utils import clean_text


class CleanerAgent(BaseAgent):
    name = "CleanerAgent"
    description = "Clean crawled text and normalize formatting."

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        documents = kwargs.get("documents", [])
        cleaned = []
        for document in documents:
            if document.get("status") != "success":
                continue
            text = clean_text(document.get("raw_text", ""))
            if not text:
                continue
            cleaned.append(
                {
                    "url": document.get("url", ""),
                    "title": document.get("title", ""),
                    "clean_text": text,
                    "content_length": len(text),
                }
            )
        return self.success(f"Cleaned {len(cleaned)} document(s).", {"cleaned_documents": cleaned})

