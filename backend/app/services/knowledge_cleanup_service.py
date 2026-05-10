import json
import re
import shutil
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings
from app.services.knowledge_map_service import KnowledgeMapService
from app.services.metadata_service import MetadataService
from app.services.vector_service import VectorService
from app.utils.file_utils import ensure_inside, relative_to_base
from app.utils.source_utils import is_blocked_source_url
from app.utils.text_utils import compact_preview, normalize_whitespace


METADATA_RE = re.compile(r"<!--\s*hivemind-md:metadata\s*(\{.*?\})\s*-->", re.DOTALL)


class KnowledgeCleanupService:
    def __init__(
        self,
        settings: Settings | None = None,
        metadata_service: MetadataService | None = None,
        vector_service: VectorService | None = None,
        map_service: KnowledgeMapService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.metadata_service = metadata_service or MetadataService()
        self.vector_service = vector_service or VectorService(self.settings)
        self.map_service = map_service or KnowledgeMapService(self.settings, self.metadata_service)

    async def cleanup(self, *, dry_run: bool = False, min_trust: float = 0.2) -> dict[str, Any]:
        started = datetime.now(timezone.utc).isoformat()
        files = self._knowledge_files()
        scanned = [self._inspect(path) for path in files]
        duplicate_groups = self._duplicate_groups(scanned)
        duplicate_paths = self._duplicate_paths(duplicate_groups)
        noise_paths = {
            item["path"]
            for item in scanned
            if self._is_noise(item, min_trust=min_trust)
        }
        targets = sorted(duplicate_paths | noise_paths, key=lambda path: str(path))

        quarantined: list[str] = []
        if not dry_run:
            for path in targets:
                quarantined.append(self._quarantine(path, started))
                relative = relative_to_base(self.settings.knowledge_path, path)
                self.metadata_service.delete_item(relative)
                self.vector_service.delete_file(relative)

        report_path = self._write_report(
            started=started,
            dry_run=dry_run,
            scanned=scanned,
            duplicate_groups=duplicate_groups,
            noise_paths=noise_paths,
            quarantined=quarantined,
        )
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

        logs = [
            self._log(
                "KnowledgeScanAgent",
                "scan",
                f"Scanned {len(scanned)} Markdown knowledge file(s).",
                score=1.0,
                input_count=len(scanned),
                output_count=len(scanned),
                data={"files": [item["relative_path"] for item in scanned[:80]]},
            ),
            self._log(
                "DuplicateClusterAgent",
                "dedupe",
                f"Found {len(duplicate_groups)} duplicate cluster(s).",
                score=1.0 if not duplicate_paths else 0.72,
                input_count=len(scanned),
                output_count=len(duplicate_paths),
                data={"duplicate_files": [relative_to_base(self.settings.knowledge_path, path) for path in sorted(duplicate_paths)]},
            ),
            self._log(
                "NoiseFilterAgent",
                "noise",
                f"Flagged {len(noise_paths)} noisy or low-trust file(s).",
                score=1.0 if not noise_paths else 0.75,
                input_count=len(scanned),
                output_count=len(noise_paths),
                data={"noise_files": [relative_to_base(self.settings.knowledge_path, path) for path in sorted(noise_paths)]},
            ),
            self._log(
                "KnowledgeMapService",
                "map",
                f"Rebuilt knowledge map with {map_data['file_count']} Markdown file(s).",
                score=1.0,
                input_count=1,
                output_count=map_index["indexed_chunks"],
                data={"map_file": map_data["map_file"], "indexed_chunks": map_index["indexed_chunks"]},
            ),
        ]

        return {
            "status": "success",
            "dry_run": dry_run,
            "scanned_files": len(scanned),
            "duplicate_groups": len(duplicate_groups),
            "noise_files": len(noise_paths),
            "quarantined_files": quarantined,
            "report_file": relative_to_base(self.settings.knowledge_path, report_path),
            "map_file": map_data["map_file"],
            "agent_logs": logs,
        }

    def _knowledge_files(self) -> list[Path]:
        excluded_parts = {"_chat_history", "_quarantine", "_maintenance"}
        return sorted(
            path
            for path in self.settings.knowledge_path.rglob("*.md")
            if path.name != "_knowledge_map.md"
            and path.is_file()
            and not any(part in excluded_parts for part in path.relative_to(self.settings.knowledge_path).parts)
        )

    def _inspect(self, path: Path) -> dict[str, Any]:
        content = path.read_text(encoding="utf-8", errors="ignore")
        metadata = self._metadata(content)
        sources = metadata.get("sources", []) if isinstance(metadata.get("sources"), list) else []
        source_urls = [url for url in (self._source_url(source) for source in sources) if url]
        title = str(metadata.get("title") or self._title(content) or path.stem)
        trust = self._trust(metadata)
        normalized = normalize_whitespace(content.lower())
        content_hash = sha256(normalized[:12000].encode("utf-8")).hexdigest()
        url_key = source_urls[0].lower() if source_urls else ""
        return {
            "path": path,
            "relative_path": relative_to_base(self.settings.knowledge_path, path),
            "title": title,
            "trust": trust,
            "length": len(content),
            "source_urls": source_urls,
            "fingerprint": url_key or content_hash,
            "preview": compact_preview(content, 240),
        }

    def _metadata(self, content: str) -> dict[str, Any]:
        match = METADATA_RE.search(content)
        if not match:
            return {}
        try:
            parsed = json.loads(match.group(1))
        except Exception:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _title(self, content: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line.replace("# ", "", 1).strip()
        return ""

    def _trust(self, metadata: dict[str, Any]) -> float | None:
        try:
            value = metadata.get("trust_score")
            return None if value is None else float(value)
        except (TypeError, ValueError):
            return None

    def _source_url(self, source: Any) -> str:
        if isinstance(source, dict):
            return str(source.get("url") or "").strip()
        return str(source or "").strip()

    def _duplicate_groups(self, items: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for item in items:
            groups.setdefault(str(item["fingerprint"]), []).append(item)
        return [group for group in groups.values() if len(group) > 1]

    def _duplicate_paths(self, groups: list[list[dict[str, Any]]]) -> set[Path]:
        paths: set[Path] = set()
        for group in groups:
            ranked = sorted(group, key=lambda item: ((item["trust"] or 0.0), item["length"]), reverse=True)
            for item in ranked[1:]:
                paths.add(item["path"])
        return paths

    def _is_noise(self, item: dict[str, Any], *, min_trust: float) -> bool:
        relative = str(item["relative_path"]).lower()
        if relative.endswith("/index.md") or relative.endswith("agent-framework.md"):
            return False
        trust = item["trust"]
        blocked = any(is_blocked_source_url(url) for url in item["source_urls"])
        too_short = int(item["length"]) < 220
        low_trust_source = trust is not None and trust < min_trust and "/sources/" in relative
        return blocked or too_short or low_trust_source

    def _quarantine(self, path: Path, timestamp: str) -> str:
        stamp = timestamp.replace(":", "").replace("+", "-")
        relative = path.relative_to(self.settings.knowledge_path)
        target = ensure_inside(
            self.settings.knowledge_path,
            self.settings.knowledge_path / "_quarantine" / stamp / relative,
        )
        target = target.with_suffix(target.suffix + ".disabled")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))
        return relative_to_base(self.settings.knowledge_path, target)

    def _write_report(
        self,
        *,
        started: str,
        dry_run: bool,
        scanned: list[dict[str, Any]],
        duplicate_groups: list[list[dict[str, Any]]],
        noise_paths: set[Path],
        quarantined: list[str],
    ) -> Path:
        maintenance_dir = ensure_inside(self.settings.knowledge_path, self.settings.knowledge_path / "_maintenance")
        maintenance_dir.mkdir(parents=True, exist_ok=True)
        report_path = ensure_inside(
            self.settings.knowledge_path,
            maintenance_dir / f"cleanup-{started.replace(':', '').replace('+', '-')}.md",
        )
        lines = [
            "# Knowledge Cleanup Report",
            "",
            f"- Started: `{started}`",
            f"- Dry run: `{str(dry_run).lower()}`",
            f"- Scanned files: `{len(scanned)}`",
            f"- Duplicate groups: `{len(duplicate_groups)}`",
            f"- Noise files: `{len(noise_paths)}`",
            f"- Quarantined: `{len(quarantined)}`",
            "",
            "## Duplicate Clusters",
            "",
        ]
        if duplicate_groups:
            for index, group in enumerate(duplicate_groups, start=1):
                lines.append(f"### Cluster {index}")
                for item in group:
                    lines.append(f"- `{item['relative_path']}` | trust `{item['trust']}` | {item['title']}")
                lines.append("")
        else:
            lines.append("- Không phát hiện cụm trùng lặp.")
            lines.append("")

        lines.extend(["## Noise Candidates", ""])
        if noise_paths:
            for path in sorted(noise_paths):
                lines.append(f"- `{relative_to_base(self.settings.knowledge_path, path)}`")
        else:
            lines.append("- Không phát hiện file nhiễu rõ ràng.")
        lines.extend(["", "## Quarantine", ""])
        if quarantined:
            lines.extend(f"- `{path}`" for path in quarantined)
        else:
            lines.append("- Không có file nào bị chuyển vào quarantine.")
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report_path

    def _log(
        self,
        agent: str,
        stage: str,
        message: str,
        *,
        score: float,
        input_count: int,
        output_count: int,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "agent": agent,
            "status": "success",
            "message": message,
            "stage": stage,
            "score": score,
            "runtime_ms": 0,
            "started_at": now,
            "ended_at": now,
            "input_count": input_count,
            "output_count": output_count,
            "data": data,
        }
