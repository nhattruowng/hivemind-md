from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.vector_service import VectorService


class IndexerAgent(BaseAgent):
    name = "IndexerAgent"
    description = "Chunk Markdown content, embed it, and store it in the vector database."

    def __init__(self, vector_service: VectorService | None = None) -> None:
        self.vector_service = vector_service or VectorService()

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        file_path = str(kwargs["file_path"])
        metadata = kwargs.get("metadata", {})
        result = await self.vector_service.index_file(file_path, metadata)
        return self.success(
            f"Indexed {result['indexed_chunks']} chunk(s) with {result['backend']}.",
            result,
        )

