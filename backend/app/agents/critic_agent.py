from typing import Any

from app.agents.base_agent import BaseAgent
from app.utils.source_utils import score_source


class CriticAgent(BaseAgent):
    name = "CriticAgent"
    description = "Evaluate source reliability and flag weak evidence."

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        cleaned_documents = kwargs.get("cleaned_documents", [])
        critiques = []
        for document in cleaned_documents:
            score, level, reason = score_source(
                document.get("url", ""),
                int(document.get("content_length", 0)),
            )
            critiques.append(
                {
                    "url": document.get("url", ""),
                    "trust_score": score,
                    "trust_level": level,
                    "reason": reason,
                }
            )
        return self.success(f"Scored {len(critiques)} source(s).", {"critiques": critiques})

