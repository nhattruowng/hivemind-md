import json
import re
from typing import Any

from app.agents.base_agent import BaseAgent
from app.config import Settings, get_settings
from app.services.ollama_service import OllamaService
from app.utils.text_utils import compact_preview


JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


class ExtractorAgent(BaseAgent):
    name = "ExtractorAgent"
    description = "Extract key knowledge from cleaned documents with Ollama fallback heuristics."

    def __init__(self, ollama: OllamaService | None = None, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.ollama = ollama or OllamaService(self.settings)

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        cleaned_documents = kwargs.get("cleaned_documents", [])
        use_ollama = bool(kwargs.get("use_ollama", True))
        extracted = []
        for document in cleaned_documents:
            text = document.get("clean_text", "")
            llm_result = await self._extract_with_ollama(text) if use_ollama else None
            data = llm_result or self._fallback_extract(text)
            data.update(
                {
                    "url": document.get("url", ""),
                    "title": document.get("title", ""),
                    "content_length": document.get("content_length", len(text)),
                }
            )
            extracted.append(data)
        return self.success(f"Extracted knowledge from {len(extracted)} document(s).", {"extracted": extracted})

    async def _extract_with_ollama(self, clean_document: str) -> dict[str, Any] | None:
        prompt = f"""
Bạn là agent rút trích kiến thức.
Hãy đọc nội dung sau và trích xuất thành JSON hợp lệ với các field:
summary: string
key_points: string[]
concepts: string[]
process_or_architecture: string[]
technologies: string[]
risks: string[]

Nội dung:
{compact_preview(clean_document, 7000)}
"""
        response = await self.ollama.generate(prompt, model=self.settings.ollama_light_model, temperature=0.1)
        if not response:
            return None
        try:
            match = JSON_BLOCK_RE.search(response)
            raw_json = match.group(0) if match else response
            parsed = json.loads(raw_json)
            return {
                "summary": str(parsed.get("summary", "")).strip(),
                "key_points": self._listify(parsed.get("key_points", [])),
                "concepts": self._listify(parsed.get("concepts", [])),
                "process_or_architecture": self._listify(parsed.get("process_or_architecture", [])),
                "technologies": self._listify(parsed.get("technologies", [])),
                "risks": self._listify(parsed.get("risks", [])),
            }
        except Exception:
            return None

    def _fallback_extract(self, text: str) -> dict[str, Any]:
        preview = compact_preview(text, 1400)
        sentences = [sentence.strip() for sentence in SENTENCE_RE.split(preview) if len(sentence.strip()) > 40]
        key_points = sentences[:4] or [preview] if preview else []
        concepts = self._concepts_from_text(text)
        return {
            "summary": compact_preview(" ".join(sentences[:3]) or preview, 700),
            "key_points": key_points,
            "concepts": concepts,
            "process_or_architecture": [],
            "technologies": [value for value in concepts if value.lower() in {"python", "fastapi", "react", "ollama"}],
            "risks": ["Extraction used local heuristic fallback because Ollama generation was unavailable."],
        }

    def _concepts_from_text(self, text: str) -> list[str]:
        words = re.findall(r"\b[A-Z][a-zA-Z0-9]{3,}\b", text)
        seen: set[str] = set()
        concepts = []
        for word in words:
            lowered = word.lower()
            if lowered not in seen:
                seen.add(lowered)
                concepts.append(word)
            if len(concepts) >= 10:
                break
        return concepts

    def _listify(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []
