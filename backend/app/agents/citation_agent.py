from typing import Any

from app.agents.base_agent import BaseAgent
from app.utils.text_utils import compact_preview


class CitationAgent(BaseAgent):
    name = "CitationAgent"
    description = "Normalize retrieved chunks and source URLs into citation records."

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        citations = kwargs.get("citations") if isinstance(kwargs.get("citations"), list) else []
        retrieval = kwargs.get("retrieval") if isinstance(kwargs.get("retrieval"), list) else []
        sources = kwargs.get("sources") if isinstance(kwargs.get("sources"), list) else []
        normalized = self._normalize(citations, retrieval, sources)
        return self.success(
            f"Prepared {len(normalized)} citation record(s).",
            {"citations": normalized, "source_count": len(sources)},
            confidence=1.0 if normalized else 0.0,
            sources=[str(item.get("source") or item.get("file_path") or "") for item in normalized],
        )

    def _normalize(self, citations: list[Any], retrieval: list[Any], sources: list[Any]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        seen: set[str] = set()
        for index, item in enumerate(citations, start=1):
            if not isinstance(item, dict):
                continue
            file_path = str(item.get("file_path") or item.get("source") or "")
            source_values = item.get("sources", []) if isinstance(item.get("sources"), list) else []
            source = str(source_values[0]) if source_values else file_path
            key = f"{file_path}|{source}"
            if key in seen:
                continue
            seen.add(key)
            records.append(
                {
                    "id": str(item.get("id") or f"S{index}"),
                    "file_path": file_path,
                    "source": source,
                    "score": item.get("score"),
                    "preview": compact_preview(str(item.get("preview") or ""), 240),
                }
            )
        if records:
            return records
        for index, item in enumerate(retrieval, start=1):
            if not isinstance(item, dict):
                continue
            file_path = str(item.get("file_path") or "")
            source_values = item.get("sources", []) if isinstance(item.get("sources"), list) else []
            source = str(source_values[0]) if source_values else file_path
            key = f"{file_path}|{source}"
            if key in seen:
                continue
            seen.add(key)
            records.append(
                {
                    "id": f"S{index}",
                    "file_path": file_path,
                    "source": source,
                    "score": item.get("score"),
                    "preview": compact_preview(str(item.get("preview") or ""), 240),
                }
            )
        if records:
            return records
        for index, source in enumerate(sources[:8], start=1):
            source_text = str(source)
            if source_text in seen:
                continue
            seen.add(source_text)
            records.append({"id": f"S{index}", "file_path": "", "source": source_text, "score": None, "preview": ""})
        return records
