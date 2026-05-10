import re
import unicodedata
from pathlib import Path
from typing import Any

from app.agents.base_agent import BaseAgent
from app.config import Settings, get_settings
from app.services.metadata_service import MetadataService
from app.utils.text_utils import normalize_whitespace


TOKEN_RE = re.compile(r"[a-zA-Z0-9À-ỹ_]+")
SYSTEM_DIRS = {"_chat_history", "_maintenance", "_quarantine", "__pycache__"}
DOMAIN_ALIASES = {
    "finance": ["tai chinh", "dau tu", "ngan hang", "chung khoan", "bitcoin", "crypto", "von", "tien"],
    "taichinh": ["tai chinh", "dau tu", "ngan hang", "chung khoan", "bitcoin", "crypto", "von", "tien"],
    "economy": ["kinh te", "vi mo", "gdp", "lam phat", "xuat khau", "ty gia", "tin dung"],
    "kinhte": ["kinh te", "vi mo", "gdp", "lam phat", "xuat khau", "ty gia", "tin dung"],
    "programming": ["lap trinh", "code", "backend", "frontend", "python", "javascript", "typescript", "api"],
    "ai": ["tri tue nhan tao", "ai", "llm", "agent", "rag", "ollama", "machine learning"],
    "general": ["tong quat", "kien thuc", "general"],
}


class InputRouterAgent(BaseAgent):
    name = "InputRouterAgent"
    description = "Classify user input and route it to supported knowledge folders."

    def __init__(
        self,
        settings: Settings | None = None,
        metadata_service: MetadataService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.metadata_service = metadata_service or MetadataService()

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        query = normalize_whitespace(str(kwargs.get("query", "")))
        max_routes = int(kwargs.get("max_routes", 5))
        candidates = self._build_candidates()
        ranked = self._rank(query, candidates)
        top_routes = ranked[:max_routes]
        primary = top_routes[0] if top_routes else {}
        confidence = float(primary.get("confidence", 0.0) or 0.0)
        supported = bool(primary) and confidence >= 0.18
        route_context = self._route_context(top_routes)
        return self.success(
            "Routed input to supported knowledge folders." if supported else "No strong knowledge folder route found.",
            {
                "query": query,
                "supported": supported,
                "confidence": round(confidence, 3),
                "primary_category": primary.get("category", "general") if supported else "general",
                "primary_folder": primary.get("folder_path", "") if supported else "",
                "top_routes": top_routes,
                "route_context": route_context,
                "candidate_count": len(candidates),
            },
        )

    def _build_candidates(self) -> list[dict[str, Any]]:
        folder_map: dict[str, dict[str, Any]] = {}
        for path in self.settings.knowledge_path.rglob("*.md"):
            if not path.is_file() or path.name == "_knowledge_map.md":
                continue
            relative = path.relative_to(self.settings.knowledge_path)
            if any(part in SYSTEM_DIRS for part in relative.parts):
                continue
            folder = relative.parent
            if not str(folder) or str(folder) == ".":
                continue
            folder_key = self._route_folder_key(folder)
            category = folder.parts[0] if folder.parts else "general"
            current = folder_map.setdefault(
                folder_key,
                {
                    "category": category,
                    "folder_path": folder_key,
                    "titles": set(),
                    "file_count": 0,
                    "trust_total": 0.0,
                    "trust_count": 0,
                },
            )
            current["file_count"] += 1

        for item in self.metadata_service.list_items():
            file_path = str(item.get("file_path") or "")
            if not file_path or file_path == "_knowledge_map.md":
                continue
            if file_path.startswith(("_chat_history/", "_maintenance/", "_quarantine/")):
                continue
            folder_key = self._route_folder_key(Path(file_path).parent)
            if not folder_key or folder_key == ".":
                continue
            category = str(item.get("category") or folder_key.split("/", 1)[0] or "general")
            current = folder_map.setdefault(
                folder_key,
                {
                    "category": category,
                    "folder_path": folder_key,
                    "titles": set(),
                    "file_count": 0,
                    "trust_total": 0.0,
                    "trust_count": 0,
                },
            )
            current["category"] = category
            title = str(item.get("title") or "").strip()
            if title:
                current["titles"].add(title)
            trust = item.get("trust_score")
            if trust is not None:
                try:
                    current["trust_total"] += float(trust)
                    current["trust_count"] += 1
                except (TypeError, ValueError):
                    pass

        candidates: list[dict[str, Any]] = []
        for value in folder_map.values():
            titles = sorted(value["titles"])
            average_trust = value["trust_total"] / value["trust_count"] if value["trust_count"] else 0.0
            path_text = value["folder_path"].replace("/", " ")
            label = titles[0] if titles else path_text
            candidates.append(
                {
                    "category": value["category"],
                    "folder_path": value["folder_path"],
                    "label": label,
                    "titles": titles[:8],
                    "file_count": value["file_count"],
                    "average_trust": round(average_trust, 2),
                    "search_text": self._normalize(
                        " ".join([value["category"], value["folder_path"], path_text, label, *titles, *self._aliases(value["category"])])
                    ),
                }
            )
        return candidates

    def _rank(self, query: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        query_text = self._normalize(query)
        query_tokens = set(TOKEN_RE.findall(query_text))
        ranked: list[dict[str, Any]] = []
        for candidate in candidates:
            haystack = str(candidate["search_text"])
            folder = self._normalize(str(candidate["folder_path"]).replace("/", " "))
            category = self._normalize(str(candidate["category"]))
            token_hits = sorted(token for token in query_tokens if len(token) > 2 and token in haystack)
            score = float(len(token_hits))
            matched_terms = list(token_hits)
            if category and category in query_text:
                score += 4.0
                matched_terms.append(category)
            if folder and folder in query_text:
                score += 5.0
                matched_terms.append(folder)
            for alias in self._aliases(str(candidate["category"])):
                alias_norm = self._normalize(alias)
                if alias_norm and alias_norm in query_text:
                    score += 3.5
                    matched_terms.append(alias)
            for title in candidate.get("titles", []):
                title_norm = self._normalize(str(title))
                if title_norm and title_norm in query_text:
                    score += 4.0
                    matched_terms.append(str(title))
            if score <= 0:
                continue
            score += min(1.5, float(candidate.get("file_count", 0)) * 0.08)
            score += min(0.8, float(candidate.get("average_trust", 0.0)) * 0.8)
            confidence = min(1.0, score / 12.0)
            ranked.append(
                {
                    "category": candidate["category"],
                    "folder_path": candidate["folder_path"],
                    "label": candidate["label"],
                    "score": round(score, 2),
                    "confidence": round(confidence, 3),
                    "matched_terms": self._unique(matched_terms)[:8],
                    "file_count": candidate["file_count"],
                    "average_trust": candidate["average_trust"],
                }
            )
        ranked.sort(key=lambda item: (item["score"], item["confidence"], item["file_count"]), reverse=True)
        return ranked

    def _route_context(self, routes: list[dict[str, Any]]) -> str:
        if not routes:
            return ""
        lines = ["Knowledge route candidates:"]
        for route in routes[:5]:
            lines.append(
                f"- {route['folder_path']} | category {route['category']} | score {route['score']} | match {', '.join(route['matched_terms']) or 'n/a'}"
            )
        return "\n".join(lines)

    def _aliases(self, category: str) -> list[str]:
        normalized = self._normalize(category)
        aliases = list(DOMAIN_ALIASES.get(normalized, []))
        if normalized in {"kinh te", "kinhte", "economy"}:
            aliases += DOMAIN_ALIASES["economy"]
        if normalized in {"tai chinh", "taichinh", "finance"}:
            aliases += DOMAIN_ALIASES["finance"]
        if normalized in {"lap trinh", "programming"}:
            aliases += DOMAIN_ALIASES["programming"]
        return aliases

    def _route_folder_key(self, folder: Path) -> str:
        parts = list(folder.parts)
        if parts and parts[-1].lower() == "sources":
            parts = parts[:-1]
        return "/".join(parts).replace("\\", "/")

    def _normalize(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value or "")
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        return normalize_whitespace(re.sub(r"[^a-zA-Z0-9_]+", " ", ascii_text).lower())

    def _unique(self, values: list[str]) -> list[str]:
        output: list[str] = []
        seen: set[str] = set()
        for value in values:
            normalized = self._normalize(value)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            output.append(value)
        return output
