import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings
from app.services.metadata_service import MetadataService
from app.utils.file_utils import ensure_inside, relative_to_base


MAP_FILE_NAME = "_knowledge_map.md"
TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")
SYSTEM_DIRS = {"_chat_history", "_maintenance", "_quarantine"}


class KnowledgeMapService:
    def __init__(
        self,
        settings: Settings | None = None,
        metadata_service: MetadataService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.metadata_service = metadata_service or MetadataService()

    @property
    def map_path(self) -> Path:
        return ensure_inside(self.settings.knowledge_path, self.settings.knowledge_path / MAP_FILE_NAME)

    def rebuild(self) -> dict[str, Any]:
        self.settings.knowledge_path.mkdir(parents=True, exist_ok=True)
        items = [
            item
            for item in self.metadata_service.list_items()
            if str(item.get("file_path", "")) != MAP_FILE_NAME
        ]
        files = sorted(
            path
            for path in self.settings.knowledge_path.rglob("*.md")
            if path.name != MAP_FILE_NAME and path.is_file()
            and not any(part in SYSTEM_DIRS for part in path.relative_to(self.settings.knowledge_path).parts)
        )
        now = datetime.now(timezone.utc).isoformat()
        content = self._compose_map(items, files, now)
        self.map_path.write_text(content, encoding="utf-8")
        return {
            "map_file": relative_to_base(self.settings.knowledge_path, self.map_path),
            "absolute_path": str(self.map_path),
            "content": content,
            "item_count": len(items),
            "file_count": len(files),
            "updated_at": now,
        }

    def read(self) -> str:
        if not self.map_path.exists():
            return self.rebuild()["content"]
        return self.map_path.read_text(encoding="utf-8")

    def relevant_excerpt(self, query: str, max_chars: int = 3500) -> str:
        content = self.read()
        if len(content) <= max_chars:
            return content

        terms = {token.lower() for token in TOKEN_RE.findall(query)}
        if not terms:
            return content[:max_chars]

        lines = content.splitlines()
        selected: list[str] = []
        for line in lines:
            lowered = line.lower()
            if line.startswith("#") or any(term in lowered for term in terms):
                selected.append(line)
            if len("\n".join(selected)) >= max_chars:
                break
        excerpt = "\n".join(selected).strip()
        return excerpt[:max_chars] if excerpt else content[:max_chars]

    def _compose_map(self, items: list[dict[str, Any]], files: list[Path], now: str) -> str:
        category_groups: dict[str, list[dict[str, Any]]] = {}
        for item in items:
            category_groups.setdefault(str(item.get("category") or "general"), []).append(item)

        lines = [
            "# Knowledge Map",
            "",
            "File này là bản đồ tri thức để agent định tuyến truy vấn nhanh trước khi đọc hoặc retrieve các shard Markdown chi tiết.",
            "",
            "## Cập nhật",
            "",
            now,
            "",
            "## Cây thư mục Markdown",
            "",
            "```txt",
        ]
        lines.extend(self._directory_tree(files))
        lines.extend(
            [
                "```",
                "",
                "## Tri thức đã index",
                "",
            ]
        )

        if not category_groups:
            lines.append("- Chưa có metadata tri thức.")
        else:
            for category in sorted(category_groups):
                lines.extend(["", f"### {category}", ""])
                for item in sorted(category_groups[category], key=lambda value: str(value.get("file_path", ""))):
                    title = str(item.get("title") or "Untitled")
                    file_path = str(item.get("file_path") or "")
                    trust = item.get("trust_score")
                    updated_at = str(item.get("updated_at") or "")
                    trust_text = f"{float(trust):.2f}" if trust is not None else "N/A"
                    lines.append(f"- `{file_path}` | {title} | trust {trust_text} | updated {updated_at}")

        lines.extend(
            [
                "",
                "## Gợi ý định tuyến",
                "",
                "- Đọc map này trước để chọn category, topic folder, hoặc file shard gần nhất.",
                "- Ưu tiên `index.md` trong thư mục topic để lấy tổng quan.",
                "- Sau đó đọc các file trong `sources/` khi cần bằng chứng hoặc chi tiết nguồn.",
                "- Nếu vector search trả ít kết quả, dùng cây thư mục ở trên để đề xuất topic cần làm mới.",
                "",
            ]
        )
        return "\n".join(lines)

    def _directory_tree(self, files: list[Path]) -> list[str]:
        if not files:
            return ["knowledge/", "  (empty)"]

        tree: dict[str, Any] = {}
        for path in files[:300]:
            relative = path.resolve().relative_to(self.settings.knowledge_path.resolve())
            node = tree
            for part in relative.parts:
                node = node.setdefault(part, {})

        tree_lines = ["knowledge/"]
        self._render_tree(tree, tree_lines, depth=1)
        if len(files) > 300:
            tree_lines.append(f"  ... {len(files) - 300} more files")
        return tree_lines

    def _render_tree(self, node: dict[str, Any], lines: list[str], depth: int) -> None:
        for name, child in sorted(node.items()):
            connector = "+ " if child else "- "
            lines.append(f"{'  ' * depth}{connector}{name}")
            if child:
                self._render_tree(child, lines, depth + 1)
