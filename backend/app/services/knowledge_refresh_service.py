import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.agents.cleaner_agent import CleanerAgent
from app.agents.crawler_agent import CrawlerAgent
from app.agents.critic_agent import CriticAgent
from app.agents.extractor_agent import ExtractorAgent
from app.agents.search_agent import SearchAgent
from app.config import Settings, get_settings
from app.services.knowledge_map_service import KnowledgeMapService
from app.services.metadata_service import MetadataService
from app.services.vector_service import VectorService
from app.utils.file_utils import ensure_inside, relative_to_base
from app.utils.text_utils import compact_preview, slugify


MODE_LIMITS = {"quick": 3, "standard": 5, "deep": 10}


class KnowledgeRefreshService:
    def __init__(
        self,
        settings: Settings | None = None,
        metadata_service: MetadataService | None = None,
        vector_service: VectorService | None = None,
        map_service: KnowledgeMapService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.metadata_service = metadata_service or MetadataService()
        self.vector_service = vector_service or VectorService()
        self.map_service = map_service or KnowledgeMapService(self.settings, self.metadata_service)
        self.search_agent = SearchAgent()
        self.crawler_agent = CrawlerAgent()
        self.cleaner_agent = CleanerAgent()
        self.extractor_agent = ExtractorAgent()
        self.critic_agent = CriticAgent()

    async def refresh(self, topic: str, category: str = "general", mode: str = "standard") -> dict[str, Any]:
        topic = topic.strip()
        category = category.strip() or "general"
        limit = MODE_LIMITS.get(mode, MODE_LIMITS["standard"])
        logs: list[dict[str, Any]] = []

        search = await self.search_agent.execute(topic=topic, limit=limit)
        logs.append(search)
        sources = search.get("data", {}).get("sources", [])[:limit]

        crawl = await self.crawler_agent.execute(sources=sources)
        logs.append(crawl)
        documents = crawl.get("data", {}).get("documents", [])

        clean = await self.cleaner_agent.execute(documents=documents)
        logs.append(clean)
        cleaned_documents = clean.get("data", {}).get("cleaned_documents", [])

        extract = await self.extractor_agent.execute(cleaned_documents=cleaned_documents)
        logs.append(extract)
        extracted = extract.get("data", {}).get("extracted", [])

        critic = await self.critic_agent.execute(cleaned_documents=cleaned_documents)
        logs.append(critic)
        critiques = critic.get("data", {}).get("critiques", [])

        saved = self.save_refresh_files(
            topic=topic,
            category=category,
            mode=mode,
            sources=sources,
            cleaned_documents=cleaned_documents,
            extracted=extracted,
            critiques=critiques,
        )

        indexed = await self.index_saved_files(saved)

        map_data = self.map_service.rebuild()
        map_index = await self.vector_service.index_file(
            map_data["absolute_path"],
            {
                "title": "Knowledge Map",
                "category": "system",
                "file_path": map_data["map_file"],
                "sources": [],
            },
        )
        logs.append(
            {
                "agent": "KnowledgeMapService",
                "status": "success",
                "message": f"Rebuilt knowledge map with {map_data['file_count']} Markdown file(s).",
                "data": {"map_file": map_data["map_file"], "indexed_chunks": map_index["indexed_chunks"]},
            }
        )

        return {
            "topic": topic,
            "category": saved["category"],
            "mode": mode,
            "files": saved["relative_files"],
            "map_file": map_data["map_file"],
            "indexed": indexed,
            "agent_logs": logs,
        }

    async def index_saved_files(self, saved: dict[str, Any]) -> list[dict[str, Any]]:
        indexed = []
        for file_path in saved["absolute_files"]:
            result = await self.vector_service.index_file(file_path, saved["metadata_by_absolute"][file_path])
            indexed.append({"file_path": saved["relative_by_absolute"][file_path], **result})
        return indexed

    def save_refresh_files(
        self,
        topic: str,
        category: str,
        mode: str,
        sources: list[dict[str, str]],
        cleaned_documents: list[dict[str, Any]],
        extracted: list[dict[str, Any]],
        critiques: list[dict[str, Any]],
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        category_slug = slugify(category, fallback="general")
        topic_slug = slugify(topic)
        topic_dir = ensure_inside(self.settings.knowledge_path, self.settings.knowledge_path / category_slug / topic_slug)
        source_dir = ensure_inside(self.settings.knowledge_path, topic_dir / "sources")
        source_dir.mkdir(parents=True, exist_ok=True)
        self._clear_previous_refresh(topic_dir)

        extract_by_url = {str(item.get("url", "")): item for item in extracted}
        critique_by_url = {str(item.get("url", "")): item for item in critiques}
        source_by_url = {str(item.get("url", "")): item for item in sources}

        files: list[Path] = []
        metadata_by_absolute: dict[str, dict[str, Any]] = {}

        index_path = ensure_inside(self.settings.knowledge_path, topic_dir / "index.md")
        index_content = self._compose_topic_index(
            topic=topic,
            category=category_slug,
            mode=mode,
            sources=sources,
            extracted=extracted,
            critiques=critiques,
            now=now,
        )
        index_path.write_text(index_content, encoding="utf-8")
        files.append(index_path)
        index_relative = relative_to_base(self.settings.knowledge_path, index_path)
        index_metadata = {
            "title": topic,
            "slug": f"{topic_slug}-index",
            "category": category_slug,
            "file_path": index_relative,
            "sources": sources,
            "trust_score": self._average_trust(critiques),
            "updated_at": now,
            "refresh_mode": True,
        }
        metadata_by_absolute[str(index_path)] = index_metadata
        self.metadata_service.upsert_item(
            title=topic,
            slug=index_metadata["slug"],
            category=category_slug,
            file_path=index_relative,
            sources=sources,
            trust_score=index_metadata["trust_score"],
        )

        for index, document in enumerate(cleaned_documents, start=1):
            url = str(document.get("url", ""))
            source = source_by_url.get(url, {"title": document.get("title", ""), "url": url, "snippet": ""})
            extracted_data = extract_by_url.get(url, {})
            critique = critique_by_url.get(url, {})
            title = str(document.get("title") or source.get("title") or f"{topic} source {index}")
            file_name = f"{index:02d}-{slugify(title, fallback='source')}.md"
            file_path = ensure_inside(self.settings.knowledge_path, source_dir / file_name)
            file_path.write_text(
                self._compose_source_file(topic, category_slug, mode, source, document, extracted_data, critique, now),
                encoding="utf-8",
            )
            files.append(file_path)
            relative = relative_to_base(self.settings.knowledge_path, file_path)
            source_metadata = {
                "title": title,
                "slug": f"{topic_slug}-source-{index:02d}-{slugify(title, fallback='source')}",
                "category": category_slug,
                "file_path": relative,
                "sources": [source],
                "trust_score": float(critique.get("trust_score", 0.0) or 0.0),
                "updated_at": now,
                "refresh_mode": True,
            }
            metadata_by_absolute[str(file_path)] = source_metadata
            self.metadata_service.upsert_item(
                title=title,
                slug=source_metadata["slug"],
                category=category_slug,
                file_path=relative,
                sources=[source],
                trust_score=source_metadata["trust_score"],
            )

        relative_by_absolute = {str(path): relative_to_base(self.settings.knowledge_path, path) for path in files}
        return {
            "category": category_slug,
            "absolute_files": [str(path) for path in files],
            "relative_files": [relative_by_absolute[str(path)] for path in files],
            "relative_by_absolute": relative_by_absolute,
            "metadata_by_absolute": metadata_by_absolute,
        }

    def _clear_previous_refresh(self, topic_dir: Path) -> None:
        if not topic_dir.exists():
            return
        for path in topic_dir.rglob("*.md"):
            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if '"refresh_mode": true' not in content.lower():
                continue
            relative = relative_to_base(self.settings.knowledge_path, path)
            self.metadata_service.delete_item(relative)
            self.vector_service.delete_file(relative)
            path.unlink()

    def _compose_topic_index(
        self,
        topic: str,
        category: str,
        mode: str,
        sources: list[dict[str, str]],
        extracted: list[dict[str, Any]],
        critiques: list[dict[str, Any]],
        now: str,
    ) -> str:
        summaries = [str(item.get("summary", "")).strip() for item in extracted if item.get("summary")]
        key_points = self._collect_unique(extracted, "key_points")
        concepts = self._collect_unique(extracted, "concepts")
        risks = self._collect_unique(extracted, "risks")
        source_lines = [
            f"- `{index:02d}` [{source.get('title') or source.get('url')}]({source.get('url')})"
            for index, source in enumerate(sources, start=1)
        ]
        metadata = {
            "title": topic,
            "category": category,
            "sources": sources,
            "trust_score": self._average_trust(critiques),
            "updated_at": now,
            "refresh_mode": True,
        }
        return "\n".join(
            [
                f"# {topic}",
                "",
                "## Mục đích",
                "",
                "Đây là file index của một lần làm mới kiến thức. Agent đọc file này trước để chọn shard nguồn phù hợp.",
                "",
                "## Tóm tắt",
                "",
                self._bullet_list(summaries[:6] or ["Chưa có nguồn internet đủ mạnh để tổng hợp sâu."]),
                "",
                "## Ý chính",
                "",
                self._bullet_list(key_points),
                "",
                "## Khái niệm",
                "",
                self._bullet_list(concepts),
                "",
                "## Nguồn và shard",
                "",
                "\n".join(source_lines) if source_lines else "- Chưa có nguồn.",
                "",
                "## Rủi ro",
                "",
                self._bullet_list(risks or ["Cần kiểm chứng thêm nếu nguồn crawl được ít hoặc độ tin cậy thấp."]),
                "",
                "## Metadata",
                "",
                f"- Category: `{category}`",
                f"- Mode: `{mode}`",
                f"- Updated: `{now}`",
                f"- Trust: `{metadata['trust_score']:.2f}`",
                "",
                "<!-- hivemind-md:metadata",
                json.dumps(metadata, ensure_ascii=True),
                "-->",
                "",
            ]
        )

    def _compose_source_file(
        self,
        topic: str,
        category: str,
        mode: str,
        source: dict[str, Any],
        document: dict[str, Any],
        extracted: dict[str, Any],
        critique: dict[str, Any],
        now: str,
    ) -> str:
        url = str(source.get("url") or document.get("url") or "")
        title = str(source.get("title") or document.get("title") or url or topic)
        clean_text = str(document.get("clean_text") or "")
        metadata = {
            "title": title,
            "category": category,
            "sources": [source],
            "trust_score": float(critique.get("trust_score", 0.0) or 0.0),
            "updated_at": now,
            "refresh_mode": True,
        }
        return "\n".join(
            [
                f"# {title}",
                "",
                "## Topic",
                "",
                topic,
                "",
                "## Source",
                "",
                f"- URL: {url or 'N/A'}",
                f"- Trust: {critique.get('trust_level', 'unknown')} ({metadata['trust_score']:.2f})",
                f"- Reason: {critique.get('reason', 'N/A')}",
                "",
                "## Summary",
                "",
                str(extracted.get("summary") or compact_preview(clean_text, 700) or "Chưa có tóm tắt."),
                "",
                "## Key Points",
                "",
                self._bullet_list([str(item) for item in extracted.get("key_points", [])]),
                "",
                "## Concepts",
                "",
                self._bullet_list([str(item) for item in extracted.get("concepts", [])]),
                "",
                "## Source Content",
                "",
                clean_text or "Không có nội dung crawl được.",
                "",
                "## Refresh Metadata",
                "",
                f"- Category: `{category}`",
                f"- Mode: `{mode}`",
                f"- Updated: `{now}`",
                "",
                "<!-- hivemind-md:metadata",
                json.dumps(metadata, ensure_ascii=True),
                "-->",
                "",
            ]
        )

    def _collect_unique(self, extracted: list[dict[str, Any]], key: str) -> list[str]:
        values: list[str] = []
        seen: set[str] = set()
        for item in extracted:
            for raw_value in item.get(key, []) or []:
                value = str(raw_value).strip()
                fingerprint = value.lower()
                if value and fingerprint not in seen:
                    seen.add(fingerprint)
                    values.append(value)
        return values[:16]

    def _bullet_list(self, items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items if item) or "- Chưa có dữ liệu."

    def _average_trust(self, critiques: list[dict[str, Any]]) -> float:
        scores = [float(item.get("trust_score", 0.0)) for item in critiques if item.get("trust_score") is not None]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)
