import json
import logging
import math
import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings
from app.services.ollama_service import OllamaService
from app.utils.text_utils import chunk_text


logger = logging.getLogger(__name__)
TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


@dataclass
class VectorSearchResult:
    chunk: str
    score: float
    file_path: str
    sources: list[str]
    metadata: dict[str, Any]


class VectorService:
    def __init__(self, settings: Settings | None = None, ollama: OllamaService | None = None) -> None:
        self.settings = settings or get_settings()
        self.ollama = ollama or OllamaService(self.settings)
        self.fallback_path = self.settings.vector_store_path / "fallback_index.json"
        self.collection = self._init_chroma_collection()

    async def index_file(self, file_path: str, metadata: dict[str, Any]) -> dict[str, Any]:
        absolute_path = Path(file_path)
        if not absolute_path.is_absolute():
            absolute_path = self.settings.knowledge_path / absolute_path
        content = absolute_path.read_text(encoding="utf-8")
        chunks = chunk_text(content, self.settings.default_chunk_size)
        if not chunks:
            return {"indexed_chunks": 0, "backend": self.backend_name}

        embeddings = [await self._embed(chunk) for chunk in chunks]
        relative_file = str(absolute_path.resolve().relative_to(self.settings.knowledge_path.resolve())).replace("\\", "/")
        records = []
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = sha256(f"{relative_file}:{index}".encode("utf-8")).hexdigest()
            record_metadata = {
                **metadata,
                "file_path": relative_file,
                "chunk_index": index,
                "sources": json.dumps(metadata.get("sources", []), ensure_ascii=True),
            }
            records.append(
                {
                    "id": chunk_id,
                    "chunk": chunk,
                    "embedding": embedding,
                    "metadata": record_metadata,
                }
            )

        if self.collection is not None:
            self.collection.upsert(
                ids=[record["id"] for record in records],
                documents=[record["chunk"] for record in records],
                embeddings=[record["embedding"] for record in records],
                metadatas=[record["metadata"] for record in records],
            )
        else:
            self._upsert_fallback(relative_file, records)

        return {"indexed_chunks": len(records), "backend": self.backend_name}

    async def query(self, question: str, top_k: int = 4) -> list[VectorSearchResult]:
        query_embedding = await self._embed(question)
        if self.collection is not None:
            return self._query_chroma(query_embedding, top_k)
        return self._query_fallback(query_embedding, top_k)

    def delete_file(self, file_path: str) -> None:
        if self.collection is not None:
            try:
                self.collection.delete(where={"file_path": file_path})
            except Exception as exc:
                logger.warning("Failed to delete Chroma records for %s: %s", file_path, exc)
        if self.fallback_path.exists():
            data = self._load_fallback()
            data["records"] = [
                record for record in data.get("records", []) if record.get("metadata", {}).get("file_path") != file_path
            ]
            self._save_fallback(data)

    @property
    def backend_name(self) -> str:
        return "chromadb" if self.collection is not None else "json-fallback"

    def _init_chroma_collection(self) -> Any | None:
        try:
            import chromadb
        except Exception as exc:
            logger.info("ChromaDB unavailable, using JSON vector fallback: %s", exc)
            return None

        try:
            client = chromadb.PersistentClient(path=str(self.settings.vector_store_path))
            return client.get_or_create_collection(name="hivemind_knowledge")
        except Exception as exc:
            logger.warning("Failed to initialize ChromaDB, using JSON fallback: %s", exc)
            return None

    async def _embed(self, text: str) -> list[float]:
        embedding = await self.ollama.embed(text)
        return embedding or self._hash_embedding(text)

    def _hash_embedding(self, text: str, dimensions: int = 384) -> list[float]:
        vector = [0.0] * dimensions
        tokens = TOKEN_RE.findall(text.lower())
        for token in tokens:
            digest = sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % dimensions
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def _query_chroma(self, embedding: list[float], top_k: int) -> list[VectorSearchResult]:
        result = self.collection.query(query_embeddings=[embedding], n_results=top_k)
        documents = result.get("documents", [[]])[0]
        distances = result.get("distances", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        matches: list[VectorSearchResult] = []
        for document, distance, metadata in zip(documents, distances, metadatas):
            sources = self._decode_sources(metadata.get("sources", "[]"))
            score = round(1.0 / (1.0 + float(distance or 0.0)), 4)
            matches.append(
                VectorSearchResult(
                    chunk=document,
                    score=score,
                    file_path=metadata.get("file_path", ""),
                    sources=sources,
                    metadata=dict(metadata),
                )
            )
        return matches

    def _query_fallback(self, embedding: list[float], top_k: int) -> list[VectorSearchResult]:
        data = self._load_fallback()
        matches = []
        for record in data.get("records", []):
            score = self._cosine(embedding, record.get("embedding", []))
            metadata = record.get("metadata", {})
            matches.append(
                VectorSearchResult(
                    chunk=record.get("chunk", ""),
                    score=round(score, 4),
                    file_path=metadata.get("file_path", ""),
                    sources=self._decode_sources(metadata.get("sources", "[]")),
                    metadata=metadata,
                )
            )
        matches.sort(key=lambda item: item.score, reverse=True)
        return matches[:top_k]

    def _upsert_fallback(self, file_path: str, records: list[dict[str, Any]]) -> None:
        data = self._load_fallback()
        existing = [
            record for record in data.get("records", []) if record.get("metadata", {}).get("file_path") != file_path
        ]
        data["records"] = existing + records
        self._save_fallback(data)

    def _load_fallback(self) -> dict[str, Any]:
        if not self.fallback_path.exists():
            return {"records": []}
        return json.loads(self.fallback_path.read_text(encoding="utf-8"))

    def _save_fallback(self, data: dict[str, Any]) -> None:
        self.fallback_path.parent.mkdir(parents=True, exist_ok=True)
        self.fallback_path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")

    def _cosine(self, left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
        right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
        return dot / (left_norm * right_norm)

    def _decode_sources(self, value: str) -> list[str]:
        try:
            raw_sources = json.loads(value)
        except Exception:
            return []
        if isinstance(raw_sources, list):
            return [str(item.get("url", item)) if isinstance(item, dict) else str(item) for item in raw_sources]
        return []

