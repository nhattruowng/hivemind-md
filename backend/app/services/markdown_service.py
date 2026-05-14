import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings
from app.utils.file_utils import ensure_inside, relative_to_base
from app.utils.text_utils import slugify


class MarkdownService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def compose(
        self,
        topic: str,
        category: str,
        extracted: list[dict[str, Any]],
        critiques: list[dict[str, Any]],
        sources: list[dict[str, str]],
    ) -> str:
        now = datetime.now(timezone.utc).isoformat()
        critique_by_url = {item.get("url"): item for item in critiques}
        average_trust = self.average_trust(critiques)

        key_points = self._collect_unique(extracted, "key_points")
        concepts = self._collect_unique(extracted, "concepts")
        risks = self._collect_unique(extracted, "risks")
        summaries = [item.get("summary", "") for item in extracted if item.get("summary")]

        if not summaries:
            summaries = [
                "Chưa có dữ liệu đủ mạnh để tổng hợp sâu. Hãy kiểm tra kết nối internet, cấu hình Ollama, "
                "hoặc thêm nguồn knowledge thủ công rồi index lại."
            ]

        markdown = [
            f"# {topic}",
            "",
            "## 1. Tóm tắt ngắn",
            "",
            "\n\n".join(f"- {summary}" for summary in summaries[:6]),
            "",
            "## 2. Kiến thức chính",
            "",
            self._bullet_list(key_points or summaries),
            "",
            "## 3. Chi tiết kỹ thuật",
            "",
            self._bullet_list(concepts or ["Chưa có chi tiết kỹ thuật được rút trích rõ ràng từ nguồn đã crawl."]),
            "",
            "## 4. Quy trình hoặc kiến trúc",
            "",
            (
                "Search -> Crawl -> Clean -> Extract -> Critic -> Compose -> Index. "
                "Nội dung được lưu thành Markdown và đưa vào vector database để phục vụ RAG."
            ),
            "",
            "## 5. Ví dụ ứng dụng",
            "",
            (
                f"- Xây dựng knowledge note về `{topic}` trong category `{category}`.\n"
                "- Dùng Chat API để hỏi đáp dựa trên file Markdown đã index."
            ),
            "",
            "## 6. Rủi ro và hạn chế",
            "",
            self._bullet_list(risks or ["Chất lượng phụ thuộc vào nguồn crawl được và model Ollama local."]),
            "",
            "## 7. Nguồn tham khảo",
            "",
            self._format_sources(sources, critique_by_url),
            "",
            "## 8. Đánh giá độ tin cậy",
            "",
            f"Điểm tin cậy trung bình: **{average_trust:.2f}**.",
            "",
            self._format_critique(critiques),
            "",
            "## 9. Ngày cập nhật",
            "",
            now,
            "",
            "<!-- hivemind-md:metadata",
            json.dumps(
                {
                    "title": topic,
                    "category": category,
                    "sources": sources,
                    "trust_score": average_trust,
                    "updated_at": now,
                },
                ensure_ascii=True,
            ),
            "-->",
            "",
        ]
        return "\n".join(markdown)

    def save(self, topic: str, category: str, content: str) -> dict[str, str]:
        category_slug = slugify(category, fallback="general")
        topic_slug = slugify(topic)
        directory = ensure_inside(self.settings.knowledge_path, self.settings.knowledge_path / category_slug)
        directory.mkdir(parents=True, exist_ok=True)
        file_path = ensure_inside(self.settings.knowledge_path, directory / f"{topic_slug}.md")
        file_path.write_text(content, encoding="utf-8")
        return {
            "absolute_path": str(file_path),
            "relative_path": relative_to_base(self.settings.knowledge_path, file_path),
            "slug": topic_slug,
            "category": category_slug,
        }

    def resolve(self, file_path: str) -> Path:
        candidate = Path(file_path)
        if not candidate.is_absolute():
            candidate = self.settings.knowledge_path / candidate
        return ensure_inside(self.settings.knowledge_path, candidate)

    def average_trust(self, critiques: list[dict[str, Any]]) -> float:
        scores = [float(item.get("trust_score", 0.0)) for item in critiques if item.get("trust_score") is not None]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)

    def _collect_unique(self, extracted: list[dict[str, Any]], key: str) -> list[str]:
        values: list[str] = []
        seen: set[str] = set()
        for item in extracted:
            for value in item.get(key, []) or []:
                normalized = str(value).strip()
                fingerprint = normalized.lower()
                if normalized and fingerprint not in seen:
                    seen.add(fingerprint)
                    values.append(normalized)
        return values[:12]

    def _bullet_list(self, items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items if item) or "- Chưa có dữ liệu."

    def _format_sources(self, sources: list[dict[str, str]], critique_by_url: dict[str, dict[str, Any]]) -> str:
        if not sources:
            return "- Chưa có nguồn tham khảo."
        lines = []
        for source in sources:
            url = source.get("url", "")
            critique = critique_by_url.get(url, {})
            level = critique.get("trust_level", "unknown")
            title = source.get("title") or url
            lines.append(f"- [{title}]({url}) - trust: {level}")
        return "\n".join(lines)

    def _format_critique(self, critiques: list[dict[str, Any]]) -> str:
        if not critiques:
            return "- Chưa có đánh giá nguồn."
        return "\n".join(
            f"- {item.get('url')}: {item.get('trust_level')} ({item.get('trust_score')}) - {item.get('reason')}"
            for item in critiques
        )
