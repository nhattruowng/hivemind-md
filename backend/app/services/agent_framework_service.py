import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from app.agents.cleaner_agent import CleanerAgent
from app.agents.crawler_agent import CrawlerAgent
from app.agents.critic_agent import CriticAgent
from app.agents.extractor_agent import ExtractorAgent
from app.agents.search_agent import SearchAgent
from app.config import Settings, get_settings
from app.services.domain_profile_service import DomainProfile, DomainProfileService
from app.services.knowledge_map_service import KnowledgeMapService
from app.services.knowledge_refresh_service import KnowledgeRefreshService
from app.services.metadata_service import MetadataService
from app.services.vector_service import VectorService
from app.utils.file_utils import ensure_inside, relative_to_base
from app.utils.source_utils import is_low_value_source, source_host
from app.utils.text_utils import slugify


class AgentFrameworkService:
    def __init__(
        self,
        settings: Settings | None = None,
        profile_service: DomainProfileService | None = None,
        metadata_service: MetadataService | None = None,
        vector_service: VectorService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.profile_service = profile_service or DomainProfileService()
        self.metadata_service = metadata_service or MetadataService()
        self.vector_service = vector_service or VectorService()
        self.refresh_service = KnowledgeRefreshService(
            self.settings,
            metadata_service=self.metadata_service,
            vector_service=self.vector_service,
        )
        self.map_service = KnowledgeMapService(self.settings, self.metadata_service)

    async def run(
        self,
        topic: str,
        category: str = "general",
        mode: str = "standard",
        profile_id: str | None = "auto",
    ) -> dict[str, Any]:
        topic = topic.strip()
        profile = self.profile_service.get_profile(profile_id, topic)
        effective_category = slugify(category if category and category != "general" else profile.category)
        source_limit = profile.source_limits.get(mode, profile.source_limits["standard"])
        worker_count = max(1, min(profile.worker_count, 5))
        logs: list[dict[str, Any]] = []

        plan = self._plan(topic, mode, profile, source_limit, worker_count)
        logs.append(
            self._stage_log(
                "FrameworkPlannerAgent",
                "success",
                f"Planned {len(plan['queries'])} specialist lane(s) for {profile.name}.",
                plan,
                stage="plan",
                score=1.0 if plan["queries"] else 0.0,
                input_count=1,
                output_count=len(plan["queries"]),
            )
        )

        sources, search_logs = await self._search_sources(plan["queries"], source_limit, profile, topic)
        logs.extend(search_logs)
        packets = self._make_packets(sources, profile)
        logs.append(
            self._stage_log(
                "FrameworkRouterAgent",
                "success",
                f"Routed {len(sources)} source(s) into {len(packets)} worker packet(s).",
                {"packets": self._compact_packets(packets)},
                stage="route",
                score=round(min(1.0, len(sources) / max(1, source_limit)), 2),
                input_count=len(sources),
                output_count=len(packets),
            )
        )

        worker_results = await self._run_workers(packets, profile)
        logs.extend(worker_results["logs"])

        synthesis = self._synthesize(topic, profile, worker_results)
        logs.append(
            self._stage_log(
                "FrameworkSynthesisAgent",
                "success",
                f"Synthesized {len(synthesis['cleaned_documents'])} cleaned document(s).",
                synthesis["summary"],
                stage="synthesize",
                score=round(
                    min(1.0, len(synthesis["cleaned_documents"]) / max(1, synthesis["summary"]["source_count"])),
                    2,
                ),
                input_count=synthesis["summary"]["source_count"],
                output_count=len(synthesis["cleaned_documents"]),
            )
        )

        filtered = self._filter(topic, profile, synthesis)
        filter_total = len(filtered["kept_urls"]) + len(filtered["dropped_sources"])
        kept_trust = self._average_trust(filtered["critiques"])
        logs.append(
            self._stage_log(
                "FrameworkFilterAgent",
                "success",
                f"Kept {len(filtered['cleaned_documents'])}/{len(synthesis['cleaned_documents'])} document(s).",
                {
                    "kept_urls": filtered["kept_urls"],
                    "dropped_sources": filtered["dropped_sources"],
                    "min_trust_score": profile.min_trust_score,
                    "average_trust": kept_trust,
                },
                stage="filter",
                score=round((len(filtered["kept_urls"]) / max(1, filter_total)) * kept_trust, 2),
                input_count=len(synthesis["cleaned_documents"]),
                output_count=len(filtered["cleaned_documents"]),
            )
        )

        saved = self.refresh_service.save_refresh_files(
            topic=topic,
            category=effective_category,
            mode=mode,
            sources=filtered["sources"],
            cleaned_documents=filtered["cleaned_documents"],
            extracted=filtered["extracted"],
            critiques=filtered["critiques"],
        )
        manifest = self._save_framework_manifest(topic, effective_category, mode, profile, plan, packets, filtered)
        saved["absolute_files"].append(manifest["absolute_path"])
        saved["relative_files"].append(manifest["relative_path"])
        saved["relative_by_absolute"][manifest["absolute_path"]] = manifest["relative_path"]
        saved["metadata_by_absolute"][manifest["absolute_path"]] = manifest["metadata"]

        indexed = await self.refresh_service.index_saved_files(saved)
        map_data = self.map_service.rebuild()
        map_index = await self.vector_service.index_file(
            map_data["absolute_path"],
            {"title": "Knowledge Map", "category": "system", "file_path": map_data["map_file"], "sources": []},
        )
        logs.append(
            self._stage_log(
                "KnowledgeMapService",
                "success",
                f"Rebuilt knowledge map with {map_data['file_count']} Markdown file(s).",
                {
                    "map_file": map_data["map_file"],
                    "indexed_chunks": map_index["indexed_chunks"],
                    "generated_files": saved["relative_files"],
                    "file_count": map_data["file_count"],
                },
                stage="map",
                score=1.0 if map_data["file_count"] else 0.0,
                input_count=len(saved["relative_files"]),
                output_count=1,
            )
        )
        average_score, agent_scores = self._score_summary(logs)

        return {
            "topic": topic,
            "category": effective_category,
            "mode": mode,
            "profile": profile.to_dict(),
            "files": saved["relative_files"],
            "map_file": map_data["map_file"],
            "indexed": indexed,
            "average_score": average_score,
            "agent_scores": agent_scores,
            "stages": {
                "plan": plan,
                "workers": self._compact_packets(packets),
                "filter": {
                    "kept_urls": filtered["kept_urls"],
                    "dropped_sources": filtered["dropped_sources"],
                },
            },
            "agent_logs": logs,
        }

    def _plan(
        self,
        topic: str,
        mode: str,
        profile: DomainProfile,
        source_limit: int,
        worker_count: int,
    ) -> dict[str, Any]:
        focus_areas = profile.focus_areas[:worker_count]
        queries = [f"{topic} {focus}" for focus in focus_areas]
        return {
            "topic": topic,
            "mode": mode,
            "profile_id": profile.id,
            "profile_name": profile.name,
            "source_limit": source_limit,
            "worker_count": worker_count,
            "max_parallel_workers": profile.max_parallel_workers,
            "use_llm_workers": profile.use_llm_workers,
            "focus_areas": focus_areas,
            "queries": queries,
        }

    async def _search_sources(
        self,
        queries: list[str],
        source_limit: int,
        profile: DomainProfile,
        topic: str,
    ) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
        search_agent = SearchAgent()
        per_query = max(2, min(4, source_limit))
        all_sources: list[dict[str, str]] = []
        logs = []
        for query in queries:
            result = await search_agent.execute(topic=query, limit=per_query)
            sources = result.get("data", {}).get("sources", [])
            all_sources.extend(sources)
            logs.append(
                self._stage_log(
                    "FrameworkSearchAgent",
                    result.get("status", "success"),
                    f"Search lane `{query}` returned {len(sources)} source(s).",
                    {"query": query, "sources": sources[:5]},
                    stage="search",
                    score=round(min(1.0, len(sources) / max(1, per_query)), 2),
                    input_count=1,
                    output_count=len(sources),
                )
            )
        ranked_sources, rejected_sources = self._rank_sources(self._dedupe_sources(all_sources), profile, topic)
        logs.append(
            self._stage_log(
                "FrameworkSourceQualityAgent",
                "success",
                f"Accepted {len(ranked_sources)} source(s), rejected {len(rejected_sources)} low-quality source(s).",
                {
                    "accepted_sources": ranked_sources[:10],
                    "rejected_sources": rejected_sources[:10],
                    "trusted_domains": profile.trusted_domains,
                },
                stage="quality",
                score=round(len(ranked_sources) / max(1, len(ranked_sources) + len(rejected_sources)), 2),
                input_count=len(ranked_sources) + len(rejected_sources),
                output_count=len(ranked_sources),
            )
        )
        return ranked_sources[:source_limit], logs

    def _make_packets(self, sources: list[dict[str, str]], profile: DomainProfile) -> list[dict[str, Any]]:
        if not sources:
            return []
        worker_count = max(1, min(profile.worker_count, 5, len(sources)))
        packets = [
            {"worker_id": index + 1, "focus": profile.focus_areas[index % len(profile.focus_areas)], "sources": []}
            for index in range(worker_count)
        ]
        for index, source in enumerate(sources):
            packets[index % worker_count]["sources"].append(source)
        return packets

    async def _run_workers(self, packets: list[dict[str, Any]], profile: DomainProfile) -> dict[str, Any]:
        semaphore = asyncio.Semaphore(max(1, profile.max_parallel_workers))
        logs: list[dict[str, Any]] = []

        async def run_packet(packet: dict[str, Any]) -> dict[str, Any]:
            async with semaphore:
                started_at = datetime.now(timezone.utc).isoformat()
                started = perf_counter()
                worker_id = int(packet["worker_id"])
                crawler = CrawlerAgent()
                cleaner = CleanerAgent()
                extractor = ExtractorAgent()
                critic = CriticAgent()
                crawl = await crawler.execute(sources=packet["sources"])
                clean = await cleaner.execute(documents=crawl.get("data", {}).get("documents", []))
                cleaned = clean.get("data", {}).get("cleaned_documents", [])
                extract = await extractor.execute(
                    cleaned_documents=cleaned,
                    use_ollama=worker_id <= profile.use_llm_workers,
                )
                critic_result = await critic.execute(cleaned_documents=cleaned)
                runtime_ms = int((perf_counter() - started) * 1000)
                return {
                    "packet": packet,
                    "documents": crawl.get("data", {}).get("documents", []),
                    "cleaned_documents": cleaned,
                    "extracted": extract.get("data", {}).get("extracted", []),
                    "critiques": critic_result.get("data", {}).get("critiques", []),
                    "logs": [crawl, clean, extract, critic_result],
                    "runtime_ms": runtime_ms,
                    "started_at": started_at,
                    "ended_at": datetime.now(timezone.utc).isoformat(),
                }

        results = await asyncio.gather(*(run_packet(packet) for packet in packets))
        for result in results:
            packet = result["packet"]
            cleaned_ratio = len(result["cleaned_documents"]) / max(1, len(packet["sources"]))
            trust_factor = self._average_trust(result["critiques"])
            logs.append(
                self._stage_log(
                    f"FrameworkWorkerAgent-{packet['worker_id']}",
                    "success",
                    f"Processed focus `{packet['focus']}` with {len(result['cleaned_documents'])} cleaned document(s).",
                    {
                        "focus": packet["focus"],
                        "sources": packet["sources"],
                        "source_count": len(packet["sources"]),
                        "cleaned_count": len(result["cleaned_documents"]),
                        "extracted_count": len(result["extracted"]),
                        "cleaned_previews": [
                            {
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "content_length": item.get("content_length", 0),
                            }
                            for item in result["cleaned_documents"][:5]
                        ],
                        "critiques": result["critiques"][:5],
                    },
                    stage="worker",
                    score=round(min(1.0, cleaned_ratio * max(0.1, trust_factor)), 2),
                    runtime_ms=result["runtime_ms"],
                    started_at=result["started_at"],
                    ended_at=result["ended_at"],
                    input_count=len(packet["sources"]),
                    output_count=len(result["cleaned_documents"]),
                )
            )
        return {"results": results, "logs": logs}

    def _synthesize(self, topic: str, profile: DomainProfile, worker_results: dict[str, Any]) -> dict[str, Any]:
        cleaned_documents: list[dict[str, Any]] = []
        extracted: list[dict[str, Any]] = []
        critiques: list[dict[str, Any]] = []
        sources: list[dict[str, str]] = []
        for result in worker_results["results"]:
            cleaned_documents.extend(result["cleaned_documents"])
            extracted.extend(result["extracted"])
            critiques.extend(result["critiques"])
            sources.extend(result["packet"]["sources"])

        return {
            "topic": topic,
            "profile_id": profile.id,
            "sources": self._dedupe_sources(sources),
            "cleaned_documents": self._dedupe_documents(cleaned_documents),
            "extracted": extracted,
            "critiques": critiques,
            "summary": {
                "source_count": len(sources),
                "cleaned_count": len(cleaned_documents),
                "extracted_count": len(extracted),
                "critique_count": len(critiques),
                "source_titles": [str(source.get("title", "")) for source in self._dedupe_sources(sources)[:10]],
                "top_concepts": self._top_concepts(extracted),
            },
        }

    def _filter(self, topic: str, profile: DomainProfile, synthesis: dict[str, Any]) -> dict[str, Any]:
        critique_by_url = {str(item.get("url", "")): item for item in synthesis["critiques"]}
        source_by_url = {str(item.get("url", "")): item for item in synthesis["sources"]}
        extracted_by_url = {str(item.get("url", "")): item for item in synthesis["extracted"]}
        kept_urls: list[str] = []
        dropped_sources: list[dict[str, str]] = []
        cleaned_documents = []

        for document in synthesis["cleaned_documents"]:
            url = str(document.get("url", ""))
            score = float(critique_by_url.get(url, {}).get("trust_score", 0.0) or 0.0)
            content_length = int(document.get("content_length", 0) or 0)
            if content_length < 200:
                dropped_sources.append({"url": url, "reason": "content too short"})
                continue
            if score < profile.min_trust_score:
                dropped_sources.append({"url": url, "reason": "trust score below profile threshold"})
                continue
            kept_urls.append(url)
            cleaned_documents.append(document)

        if not cleaned_documents and synthesis["cleaned_documents"]:
            best = max(synthesis["cleaned_documents"], key=lambda item: int(item.get("content_length", 0) or 0))
            cleaned_documents = [best]
            kept_urls = [str(best.get("url", ""))]
            dropped_sources = [item for item in dropped_sources if item.get("url") not in kept_urls]

        kept_set = set(kept_urls)
        return {
            "topic": topic,
            "sources": [source_by_url[url] for url in kept_urls if url in source_by_url],
            "cleaned_documents": cleaned_documents,
            "extracted": [extracted_by_url[url] for url in kept_urls if url in extracted_by_url],
            "critiques": [critique_by_url[url] for url in kept_urls if url in critique_by_url],
            "kept_urls": kept_urls,
            "dropped_sources": [item for item in dropped_sources if item.get("url") not in kept_set],
        }

    def _save_framework_manifest(
        self,
        topic: str,
        category: str,
        mode: str,
        profile: DomainProfile,
        plan: dict[str, Any],
        packets: list[dict[str, Any]],
        filtered: dict[str, Any],
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        topic_slug = slugify(topic)
        topic_dir = ensure_inside(self.settings.knowledge_path, self.settings.knowledge_path / category / topic_slug)
        topic_dir.mkdir(parents=True, exist_ok=True)
        path = ensure_inside(self.settings.knowledge_path, topic_dir / "agent-framework.md")
        relative = relative_to_base(self.settings.knowledge_path, path)
        metadata = {
            "title": f"{topic} agent framework",
            "slug": f"{topic_slug}-agent-framework",
            "category": category,
            "file_path": relative,
            "sources": filtered["sources"],
            "trust_score": 0.0,
            "updated_at": now,
            "refresh_mode": True,
        }
        content = "\n".join(
            [
                f"# Agent Framework: {topic}",
                "",
                "## Profile",
                "",
                f"- ID: `{profile.id}`",
                f"- Name: {profile.name}",
                f"- Category: `{category}`",
                f"- Mode: `{mode}`",
                f"- Updated: `{now}`",
                "",
                "## 3 Công Đoạn",
                "",
                "1. Planner/Router nhận yêu cầu, chọn profile và chia nguồn thành 4-5 worker lane.",
                "2. Worker agents crawl, clean, extract và critique từng phần nhỏ với giới hạn song song.",
                "3. Synthesis/Filter hợp nhất, loại nguồn yếu, ghi Markdown shard và cập nhật knowledge map.",
                "",
                "## Worker Packets",
                "",
                self._packet_markdown(packets),
                "",
                "## Filter Result",
                "",
                f"- Kept: {len(filtered['kept_urls'])}",
                f"- Dropped: {len(filtered['dropped_sources'])}",
                "",
                "<!-- hivemind-md:metadata",
                json.dumps(metadata, ensure_ascii=True),
                "-->",
                "",
            ]
        )
        path.write_text(content, encoding="utf-8")
        self.metadata_service.upsert_item(
            title=metadata["title"],
            slug=metadata["slug"],
            category=category,
            file_path=relative,
            sources=filtered["sources"],
            trust_score=0.0,
        )
        return {"absolute_path": str(path), "relative_path": relative, "metadata": metadata}

    def _packet_markdown(self, packets: list[dict[str, Any]]) -> str:
        if not packets:
            return "- Không có packet vì search chưa có nguồn."
        lines = []
        for packet in packets:
            lines.append(f"- Worker {packet['worker_id']} `{packet['focus']}`: {len(packet['sources'])} source(s)")
        return "\n".join(lines)

    def _dedupe_sources(self, sources: list[dict[str, str]]) -> list[dict[str, str]]:
        seen: set[str] = set()
        unique = []
        for source in sources:
            url = str(source.get("url", "")).strip()
            if not url or url in seen:
                continue
            seen.add(url)
            unique.append(source)
        return unique

    def _average_trust(self, critiques: list[dict[str, Any]]) -> float:
        scores = [float(item.get("trust_score", 0.0) or 0.0) for item in critiques]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)

    def _top_concepts(self, extracted: list[dict[str, Any]]) -> list[str]:
        concepts: list[str] = []
        seen: set[str] = set()
        for item in extracted:
            for raw_value in item.get("concepts", []) or []:
                value = str(raw_value).strip()
                fingerprint = value.lower()
                if value and fingerprint not in seen:
                    seen.add(fingerprint)
                    concepts.append(value)
                if len(concepts) >= 12:
                    return concepts
        return concepts

    def _dedupe_documents(self, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        unique = []
        for document in documents:
            url = str(document.get("url", "")).strip()
            if not url or url in seen:
                continue
            seen.add(url)
            unique.append(document)
        return unique

    def _rank_sources(
        self,
        sources: list[dict[str, str]],
        profile: DomainProfile,
        topic: str,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        topic_terms = {part.lower() for part in topic.replace("-", " ").split() if len(part) >= 3}
        trusted_domains = tuple(domain.lower().removeprefix("www.") for domain in profile.trusted_domains)
        ranked: list[tuple[float, dict[str, str]]] = []
        rejected: list[dict[str, str]] = []

        for source in sources:
            if is_low_value_source(source):
                rejected.append({**source, "reason": "blocked or low-value SEO source"})
                continue

            host = source_host(str(source.get("url", "")))
            haystack = " ".join(
                [
                    str(source.get("title", "")),
                    str(source.get("snippet", "")),
                    str(source.get("url", "")),
                ]
            ).lower()
            score = 0.0
            if any(host == domain or host.endswith(f".{domain}") for domain in trusted_domains):
                score += 5.0
            score += sum(0.3 for term in topic_terms if term in haystack)
            if profile.id in {"economy", "finance"} and any(
                hint in haystack
                for hint in ("kinh tế", "tài chính", "gdp", "lạm phát", "thị trường", "economy", "finance")
            ):
                score += 1.0
            if host.endswith((".gov", ".edu")):
                score += 2.0
            ranked.append((score, source))

        ranked.sort(key=lambda item: item[0], reverse=True)
        return [source for _, source in ranked], rejected

    def _compact_packets(self, packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "worker_id": packet["worker_id"],
                "focus": packet["focus"],
                "source_count": len(packet["sources"]),
                "sources": packet["sources"][:3],
            }
            for packet in packets
        ]

    def _score_summary(self, logs: list[dict[str, Any]]) -> tuple[float, dict[str, float]]:
        grouped: dict[str, list[float]] = {}
        for log in logs:
            score = log.get("score")
            if score is None:
                continue
            grouped.setdefault(str(log.get("agent", "unknown")), []).append(float(score))
        agent_scores = {
            agent: round(sum(scores) / len(scores), 2)
            for agent, scores in grouped.items()
            if scores
        }
        if not agent_scores:
            return 0.0, {}
        average = round(sum(agent_scores.values()) / len(agent_scores), 2)
        return average, agent_scores

    def _stage_log(
        self,
        agent: str,
        status: str,
        message: str,
        data: dict[str, Any],
        *,
        stage: str,
        score: float | None = None,
        runtime_ms: int | None = None,
        started_at: str | None = None,
        ended_at: str | None = None,
        input_count: int | None = None,
        output_count: int | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "agent": agent,
            "status": status,
            "message": message,
            "stage": stage,
            "score": round(score, 2) if score is not None else None,
            "runtime_ms": runtime_ms,
            "started_at": started_at or now,
            "ended_at": ended_at or now,
            "input_count": input_count,
            "output_count": output_count,
            "data": data,
        }
