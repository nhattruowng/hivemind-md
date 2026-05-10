from datetime import datetime, timezone
from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.knowledge_map_service import KnowledgeMapService
from app.services.markdown_service import MarkdownService
from app.services.metadata_service import MetadataService


class ComposerAgent(BaseAgent):
    name = "ComposerAgent"
    description = "Compose extracted knowledge into a Markdown file and save metadata."

    def __init__(
        self,
        markdown_service: MarkdownService | None = None,
        metadata_service: MetadataService | None = None,
        map_service: KnowledgeMapService | None = None,
    ) -> None:
        self.markdown_service = markdown_service or MarkdownService()
        self.metadata_service = metadata_service or MetadataService()
        self.map_service = map_service or KnowledgeMapService(metadata_service=self.metadata_service)

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        topic = str(kwargs["topic"])
        category = str(kwargs.get("category", "general"))
        extracted = kwargs.get("extracted", [])
        critiques = kwargs.get("critiques", [])
        sources = kwargs.get("sources", [])

        content = self.markdown_service.compose(topic, category, extracted, critiques, sources)
        saved = self.markdown_service.save(topic, category, content)
        trust_score = self.markdown_service.average_trust(critiques)
        now = datetime.now(timezone.utc).isoformat()
        metadata = {
            "title": topic,
            "slug": saved["slug"],
            "category": saved["category"],
            "file_path": saved["relative_path"],
            "sources": sources,
            "trust_score": trust_score,
            "created_at": now,
            "updated_at": now,
        }
        self.metadata_service.upsert_item(
            title=topic,
            slug=saved["slug"],
            category=saved["category"],
            file_path=saved["relative_path"],
            sources=sources,
            trust_score=trust_score,
        )
        map_data = self.map_service.rebuild()
        return self.success(
            f"Created Markdown file {saved['relative_path']}.",
            {
                "markdown_file": saved["relative_path"],
                "absolute_path": saved["absolute_path"],
                "content": content,
                "metadata": metadata,
                "map_file": map_data["map_file"],
            },
        )
