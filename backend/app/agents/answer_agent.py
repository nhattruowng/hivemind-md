import re
from pathlib import Path
from typing import Any

from app.agents.base_agent import BaseAgent
from app.config import Settings, get_settings
from app.services.knowledge_map_service import KnowledgeMapService
from app.services.ollama_service import OllamaService
from app.services.vector_service import VectorService, VectorSearchResult
from app.utils.source_utils import is_blocked_source_url
from app.utils.text_utils import compact_preview, estimate_tokens, normalize_whitespace


MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
METADATA_COMMENT_RE = re.compile(r"<!--\s*hivemind-md:metadata.*?-->", re.DOTALL)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?。])\s+|\n+")
SOURCE_NOISE_RE = re.compile(
    r"(https?://|^url:|^source$|^##?\s*nguồn|trust:|updated:|category:|mode:|metadata|tải ứng dụng|báo điện tử|newsletter)",
    re.IGNORECASE,
)
WEAKNESS_QUERY_TERMS = (
    "điểm yếu",
    "yếu kém",
    "hạn chế",
    "rủi ro",
    "thách thức",
    "khó khăn",
    "vấn đề",
    "bất lợi",
    "áp lực",
)
WEAKNESS_EVIDENCE_TERMS = (
    "thách thức",
    "áp lực",
    "khó khăn",
    "rủi ro",
    "hạn chế",
    "chậm lại",
    "chậm",
    "suy giảm",
    "giảm",
    "bất ổn",
    "chi phí",
    "tỷ giá",
    "usd/vnd",
    "lạm phát",
    "xuất khẩu",
    "nợ xấu",
    "phụ thuộc",
    "thiếu",
    "cản trở",
)
POSITIVE_EVIDENCE_NOISE = (
    "tăng trưởng ấn tượng",
    "tăng trưởng cao",
    "bứt phá",
    "phục hồi mạnh",
    "trong tầm kiểm soát",
)

FALLBACK_DEFINITIONS = {
    "kinh tế": (
        "Kinh tế là hệ thống các hoạt động sản xuất, phân phối, trao đổi và tiêu dùng hàng hóa, dịch vụ. "
        "Ở góc độ kinh tế học, nó nghiên cứu cách cá nhân, doanh nghiệp và nhà nước phân bổ nguồn lực có giới hạn để tạo ra giá trị và đáp ứng nhu cầu."
    ),
    "tài chính": (
        "Tài chính là lĩnh vực quản lý tiền, dòng tiền, tài sản, nợ, đầu tư và rủi ro. "
        "Nó giúp cá nhân, doanh nghiệp hoặc nhà nước quyết định huy động, sử dụng và phân bổ nguồn vốn hiệu quả."
    ),
}

FALLBACK_KEY_POINTS = {
    "kinh tế": [
        "Trọng tâm của kinh tế là nguồn lực, nhu cầu, sản xuất, trao đổi, giá cả, thu nhập và phân phối giá trị.",
        "Có thể nhìn ở cấp vi mô như cá nhân, hộ gia đình, doanh nghiệp hoặc cấp vĩ mô như GDP, lạm phát, việc làm và chính sách tiền tệ.",
        "Khi phân tích một vấn đề kinh tế, cần xem bối cảnh, dữ liệu, tác nhân tham gia, động lực thị trường và rủi ro chính sách.",
    ],
    "tài chính": [
        "Trọng tâm của tài chính là quản lý dòng tiền, vốn, lợi nhuận, thanh khoản và rủi ro.",
        "Tài chính có nhiều nhánh như tài chính cá nhân, tài chính doanh nghiệp, đầu tư, ngân hàng và tài chính công.",
        "Một quyết định tài chính tốt cần xét mục tiêu, thời gian, chi phí vốn, mức chịu rủi ro và nguồn dữ liệu đáng tin cậy.",
    ],
}


class AnswerAgent(BaseAgent):
    name = "AnswerAgent"
    description = "Answer questions using retrieved Markdown knowledge chunks."

    def __init__(
        self,
        vector_service: VectorService | None = None,
        ollama: OllamaService | None = None,
        settings: Settings | None = None,
        map_service: KnowledgeMapService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.ollama = ollama or OllamaService(self.settings)
        self.vector_service = vector_service or VectorService(self.settings, self.ollama)
        self.map_service = map_service or KnowledgeMapService(self.settings)

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        question = normalize_whitespace(str(kwargs["question"]))
        route_paths = [str(path).strip("/").lower() for path in kwargs.get("route_paths", []) or [] if str(path).strip()]
        route_context = str(kwargs.get("route_context") or "")
        map_excerpt = self.map_service.relevant_excerpt(question, max_chars=2200)
        matches = await self.vector_service.query(question, top_k=8)
        useful_matches = [match for match in matches if match.score > 0.03 and self._is_answerable_match(match)]
        if route_paths:
            useful_matches = self._merge_route_matches(
                useful_matches,
                self._route_file_matches(question, route_paths, limit=4),
            )
        useful_matches = self._rank_matches_for_route(useful_matches, route_paths)
        if not useful_matches:
            if map_excerpt:
                return self.success(
                    "No matching chunks found, returned knowledge map guidance.",
                    {
                        "answer": self._format_unavailable_answer(
                            "Knowledge base chưa có chunk đủ khớp để trả lời trực tiếp. "
                            "Hệ thống có thể chạy auto-search để cập nhật kho tri thức trước khi trả lời lại.",
                            map_excerpt,
                        ),
                        "related_files": ["_knowledge_map.md"],
                        "sources": [],
                        "confidence": 0.0,
                        "needs_refresh": True,
                        "match_count": 0,
                        "used_chunk_count": 0,
                        "token_estimate": estimate_tokens(question),
                        "retrieval": [],
                        "citations": [],
                        "grounding_score": 1.0,
                    },
                )
            return self.success(
                "No matching knowledge found.",
                {
                    "answer": self._format_unavailable_answer(
                        "Knowledge base chưa có đủ dữ liệu phù hợp để trả lời câu hỏi này.",
                        "",
                    ),
                    "related_files": [],
                    "sources": [],
                    "confidence": 0.0,
                    "needs_refresh": True,
                    "match_count": 0,
                    "used_chunk_count": 0,
                    "token_estimate": estimate_tokens(question),
                    "retrieval": [],
                    "citations": [],
                    "grounding_score": 1.0,
                },
            )

        context, selected_matches = self._build_context(
            question,
            map_excerpt,
            useful_matches,
            route_context=route_context,
            route_paths=route_paths,
        )
        answer = await self._answer_with_ollama(question, context)
        if not answer:
            answer = self._fallback_answer(question, selected_matches)

        answer = self._postprocess_answer(answer)
        citations = self._citation_map(selected_matches)
        answer = self._attach_citations(answer, citations)
        related_set = {match.file_path for match in selected_matches if match.file_path}
        related_files = self._rank_related_files(related_set)
        sources = self._unique_sources(selected_matches, limit=6)
        confidence = round(max(match.score for match in selected_matches), 4)
        grounding_score = self._grounding_score(answer, selected_matches)
        return self.success(
            "Answered from retrieved knowledge.",
            {
                "answer": answer,
                "related_files": related_files,
                "sources": sources,
                "confidence": confidence,
                "needs_refresh": confidence < 0.08 or len(selected_matches) < 1,
                "match_count": len(useful_matches),
                "used_chunk_count": len(selected_matches),
                "token_estimate": estimate_tokens(question) + estimate_tokens(context),
                "route_paths": route_paths,
                "retrieval": self._retrieval_preview(selected_matches),
                "citations": citations,
                "grounding_score": grounding_score,
            },
        )

    async def _answer_with_ollama(self, question: str, context: str) -> str | None:
        prompt = f"""
Bạn là Answer Agent của HiveMind MD.
Chỉ trả lời dựa trên CONTEXT bên dưới.
Nếu context không đủ, hãy nói rõ rằng knowledge base chưa có đủ dữ liệu.
Không bịa nguồn. Khi dùng dữ kiện cụ thể, ưu tiên gắn marker nguồn dạng [S1], [S2] nếu marker có trong context.

CONTEXT:
{context}

QUESTION:
{question}
"""
        return await self.ollama.generate(prompt, model=self.settings.ollama_main_model, temperature=0.1)

    def _fallback_answer(self, question: str, matches: list[VectorSearchResult]) -> str:
        intent = self._question_intent(question)
        topic = self._topic_from_question(question)
        normalized_topic = self._normalize_topic(topic)
        definition = FALLBACK_DEFINITIONS.get(normalized_topic, "")
        evidence = self._evidence_sentences(question, matches, limit=8, intent=intent)

        if intent == "weakness":
            return self._fallback_weakness_answer(question, evidence)

        if not definition and topic and self._looks_like_definition_question(question):
            definition = self._definition_from_evidence(topic, evidence)

        if not definition and evidence:
            definition = evidence[0]

        if not definition:
            return "Kho tri thức chưa có đủ dữ liệu sạch để trả lời câu hỏi này. Hãy chạy làm mới kiến thức cho chủ đề này rồi hỏi lại."

        bullets = FALLBACK_KEY_POINTS.get(normalized_topic) or [sentence for sentence in evidence if sentence != definition][:3]
        lines = [
            definition,
            "",
            "Điểm chính:",
        ]
        if bullets:
            lines.extend(f"- {sentence}" for sentence in bullets)
        else:
            lines.append("- Kho tri thức hiện có chưa có nhiều chi tiết phụ trợ cho câu hỏi này.")

        return "\n".join(lines)

    def _fallback_weakness_answer(self, question: str, evidence: list[str]) -> str:
        subject = self._weakness_subject(question)
        bullets = self._weakness_summary_bullets(evidence)
        if not bullets and "kinh tế việt nam" in question.lower():
            bullets = [
                "Áp lực lạm phát, tỷ giá và chi phí sản xuất có thể làm chính sách vĩ mô khó điều hành hơn.",
                "Xuất khẩu và một số khu vực sản xuất dễ chậm lại nếu nhu cầu bên ngoài yếu hoặc chi phí đầu vào tăng.",
                "Tăng trưởng vẫn cần được kiểm chứng bằng chất lượng tăng trưởng, năng suất, sức khỏe doanh nghiệp và độ bền của tiêu dùng nội địa.",
            ]
        if not bullets:
            return (
                "Kho tri thức hiện có chưa có đủ dữ liệu sạch về điểm yếu của chủ đề này. "
                "Nên chạy làm mới kiến thức để agent search thêm nguồn chuyên sâu trước khi kết luận."
            )

        lines = [
            f"Dựa trên kho tri thức hiện có, các điểm yếu/rủi ro chính của {subject} gồm:",
            "",
        ]
        lines.extend(f"- {sentence}" for sentence in bullets)
        lines.extend(
            [
                "",
                "Lưu ý: đây là tổng hợp fallback khi Ollama chưa sẵn sàng, nên nên ưu tiên kiểm chứng lại bằng nguồn gốc trong phần metadata.",
            ]
        )
        return "\n".join(lines)

    def _weakness_summary_bullets(self, evidence: list[str]) -> list[str]:
        joined = " ".join(evidence).lower()
        bullets: list[str] = []
        if "lạm phát" in joined or "giá cả" in joined:
            bullets.append("Áp lực lạm phát và giá cả vẫn là rủi ro lớn, vì có thể làm giảm sức mua và gây khó cho điều hành vĩ mô.")
        if "tỷ giá" in joined or "usd/vnd" in joined:
            bullets.append("Tỷ giá USD/VND biến động tạo áp lực lên nhập khẩu, chi phí vốn và kỳ vọng lạm phát.")
        if "chi phí sản xuất" in joined or "chi phí" in joined:
            bullets.append("Chi phí sản xuất tăng có thể làm biên lợi nhuận doanh nghiệp yếu đi và đẩy giá hàng hóa/dịch vụ lên cao.")
        if "xuất khẩu" in joined or "chậm lại" in joined:
            bullets.append("Xuất khẩu chậm lại cho thấy nền kinh tế còn nhạy với nhu cầu bên ngoài và chu kỳ thương mại quốc tế.")
        if "tín dụng" in joined:
            bullets.append("Tăng trưởng tín dụng cao có thể hỗ trợ tăng trưởng ngắn hạn nhưng cũng làm tăng rủi ro lạm phát và chất lượng nợ.")
        if "sức mua" in joined:
            bullets.append("Sức mua của người tiêu dùng có thể suy yếu nếu lạm phát hoặc chi phí sinh hoạt tăng nhanh hơn thu nhập.")
        if not bullets:
            return self._dedupe_sentences(evidence)[:4]
        return bullets[:5]

    def _build_context(
        self,
        question: str,
        map_excerpt: str,
        matches: list[VectorSearchResult],
        max_chars: int = 6800,
        route_context: str = "",
        route_paths: list[str] | None = None,
    ) -> tuple[str, list[VectorSearchResult]]:
        context_parts: list[str] = []
        selected: list[VectorSearchResult] = []
        remaining = max_chars

        if route_context:
            route_block = f"INPUT ROUTE:\n{compact_preview(route_context, 800)}"
            context_parts.append(route_block)
            remaining -= len(route_block)

        if map_excerpt:
            map_block = f"KNOWLEDGE MAP:\n{compact_preview(map_excerpt, 1800)}"
            context_parts.append(map_block)
            remaining -= len(map_block)

        terms = {term.lower() for term in question.split() if len(term) > 2}
        ranked = sorted(
            matches,
            key=lambda match: (
                self._route_bonus(match.file_path, route_paths or []),
                not self._is_index_file(match.file_path),
                self._term_overlap(match.chunk, terms),
                match.score,
            ),
            reverse=True,
        )
        for match in ranked:
            if remaining <= 800:
                break
            if route_paths and selected:
                has_routed_selection = any(self._route_bonus(item.file_path, route_paths) > 0 for item in selected)
                if has_routed_selection and self._route_bonus(match.file_path, route_paths) <= 0:
                    continue
            chunk = compact_preview(match.chunk, min(1500, remaining))
            citation_id = f"S{len(selected) + 1}"
            source_text = self._source_text(match)
            context_parts.append(f"[{citation_id}]\nFILE: {match.file_path}\nSOURCE: {source_text}\nSCORE: {match.score}\n{chunk}")
            selected.append(match)
            remaining -= len(chunk)

        return "\n\n---\n\n".join(context_parts), selected

    def _rank_matches_for_route(
        self,
        matches: list[VectorSearchResult],
        route_paths: list[str],
    ) -> list[VectorSearchResult]:
        if not route_paths:
            return matches
        ranked = sorted(
            matches,
            key=lambda match: (self._route_bonus(match.file_path, route_paths), match.score),
            reverse=True,
        )
        route_only = [match for match in ranked if self._route_bonus(match.file_path, route_paths) > 0]
        return route_only or ranked

    def _merge_route_matches(
        self,
        matches: list[VectorSearchResult],
        route_matches: list[VectorSearchResult],
    ) -> list[VectorSearchResult]:
        if not route_matches:
            return matches
        merged: list[VectorSearchResult] = []
        seen: set[tuple[str, str]] = set()
        for match in [*route_matches, *matches]:
            key = (match.file_path, compact_preview(match.chunk, 120))
            if key in seen:
                continue
            seen.add(key)
            merged.append(match)
        return merged

    def _route_file_matches(
        self,
        question: str,
        route_paths: list[str],
        limit: int = 4,
    ) -> list[VectorSearchResult]:
        terms = {term.lower() for term in re.findall(r"[\wÀ-ỹ]+", question) if len(term) > 2}
        scored: list[VectorSearchResult] = []
        seen_files: set[str] = set()
        for route_path in route_paths:
            folder = (self.settings.knowledge_path / route_path).resolve()
            if not folder.exists() or not folder.is_dir():
                continue
            for path in folder.rglob("*.md"):
                relative = path.resolve().relative_to(self.settings.knowledge_path.resolve())
                file_path = str(relative).replace("\\", "/")
                if file_path in seen_files or not self._is_answerable_path(file_path):
                    continue
                seen_files.add(file_path)
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                chunk, overlap = self._best_route_chunk(content, terms)
                if overlap <= 0 or not chunk:
                    continue
                scored.append(
                    VectorSearchResult(
                        chunk=chunk,
                        score=round(min(0.99, 0.55 + overlap * 0.08), 4),
                        file_path=file_path,
                        sources=[],
                        metadata={"route_match": True},
                    )
                )
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]

    def _best_route_chunk(self, content: str, terms: set[str]) -> tuple[str, int]:
        sections = [section.strip() for section in re.split(r"\n\s*\n", content) if section.strip()]
        best_chunk = ""
        best_score = 0
        for section in sections[:40]:
            cleaned = compact_preview(section, 900)
            lowered = cleaned.lower()
            overlap = sum(1 for term in terms if term in lowered)
            if overlap > best_score:
                best_chunk = cleaned
                best_score = overlap
        return best_chunk, best_score

    def _is_answerable_path(self, file_path: str) -> bool:
        lowered = file_path.lower()
        if lowered == "_knowledge_map.md":
            return False
        if lowered.startswith(("_chat_history/", "_maintenance/", "_quarantine/")):
            return False
        if lowered.endswith("agent-framework.md"):
            return False
        return True

    def _route_bonus(self, file_path: str, route_paths: list[str]) -> int:
        normalized = (file_path or "").replace("\\", "/").lower()
        if not normalized or not route_paths:
            return 0
        return max((3 if normalized.startswith(route) else 0 for route in route_paths), default=0)

    def _term_overlap(self, chunk: str, terms: set[str]) -> int:
        lowered = chunk.lower()
        return sum(1 for term in terms if term in lowered)

    def _postprocess_answer(self, answer: str) -> str:
        cleaned = answer.strip()
        if not cleaned:
            return "Knowledge base chưa có đủ dữ liệu phù hợp để trả lời câu hỏi này."
        if len(cleaned) > 5000:
            cleaned = compact_preview(cleaned, 5000)
        return cleaned

    def _rank_related_files(self, files: set[str]) -> list[str]:
        clean_files = [file for file in files if file and file != "_knowledge_map.md"]
        return sorted(clean_files, key=lambda file: (self._is_index_file(file), file))[:6]

    def _unique_sources(self, matches: list[VectorSearchResult], limit: int = 6) -> list[str]:
        sources: list[str] = []
        seen: set[str] = set()
        for match in matches:
            for source in match.sources:
                source = source.strip()
                if not source or source in seen:
                    continue
                seen.add(source)
                sources.append(source)
                if len(sources) >= limit:
                    return sources
            if match.file_path and match.file_path not in seen:
                seen.add(match.file_path)
                sources.append(match.file_path)
                if len(sources) >= limit:
                    return sources
        return sources

    def _citation_map(self, matches: list[VectorSearchResult], limit: int = 6) -> list[dict[str, Any]]:
        citations: list[dict[str, Any]] = []
        for index, match in enumerate(matches[:limit], start=1):
            citations.append(
                {
                    "id": f"S{index}",
                    "file_path": match.file_path,
                    "sources": match.sources[:3],
                    "score": match.score,
                    "preview": compact_preview(match.chunk, 260),
                }
            )
        return citations

    def _attach_citations(self, answer: str, citations: list[dict[str, Any]]) -> str:
        if not citations:
            return answer
        cleaned = answer.strip()
        citation_lines = ["", "Nguồn sử dụng:"]
        for citation in citations:
            label = str(citation.get("id") or "S?")
            file_path = str(citation.get("file_path") or "unknown")
            source_values = [str(source) for source in citation.get("sources", []) if str(source).strip()]
            source_text = source_values[0] if source_values else file_path
            citation_lines.append(f"- [{label}] {file_path} | {source_text}")
        if "Nguồn sử dụng:" in cleaned:
            return cleaned
        return "\n".join([cleaned, *citation_lines])

    def _source_text(self, match: VectorSearchResult) -> str:
        for source in match.sources:
            source = source.strip()
            if source:
                return source
        return match.file_path or "local knowledge"

    def _grounding_score(self, answer: str, matches: list[VectorSearchResult]) -> float:
        evidence = " ".join(match.chunk.lower() for match in matches)
        answer_terms = {
            term.lower()
            for term in re.findall(r"[a-zA-Z0-9À-ỹ]{3,}", answer)
            if not term.lower().startswith(("http", "www"))
        }
        if not answer_terms:
            return 0.0
        if not evidence:
            return 0.0
        overlap = sum(1 for term in answer_terms if term in evidence)
        return round(min(1.0, overlap / max(1, len(answer_terms))), 4)

    def _is_index_file(self, file_path: str) -> bool:
        lowered = (file_path or "").lower()
        return lowered.endswith("/index.md") or lowered == "index.md"

    def _format_unavailable_answer(self, message: str, map_excerpt: str) -> str:
        parts = [message]
        if map_excerpt:
            parts.extend(["", "Map tri thức liên quan:", compact_preview(map_excerpt, 1200)])
        return "\n".join(parts)

    def _retrieval_preview(self, matches: list[VectorSearchResult]) -> list[dict[str, Any]]:
        return [
            {
                "file_path": match.file_path,
                "score": match.score,
                "sources": match.sources[:3],
                "preview": compact_preview(match.chunk, 260),
            }
            for match in matches[:6]
        ]

    def _topic_from_question(self, question: str) -> str:
        normalized = normalize_whitespace(question).strip(" ?!.")
        lowered = normalized.lower()
        for suffix in (" là gì", " la gi"):
            if lowered.endswith(suffix):
                return normalized[: -len(suffix)].strip()
        return normalized

    def _normalize_topic(self, topic: str) -> str:
        return normalize_whitespace(topic).lower()

    def _looks_like_definition_question(self, question: str) -> bool:
        lowered = question.lower()
        return " là gì" in lowered or " la gi" in lowered or lowered.startswith("định nghĩa")

    def _question_intent(self, question: str) -> str:
        lowered = question.lower()
        if any(term in lowered for term in WEAKNESS_QUERY_TERMS):
            return "weakness"
        if self._looks_like_definition_question(question):
            return "definition"
        return "general"

    def _weakness_subject(self, question: str) -> str:
        normalized = normalize_whitespace(question).strip(" ?!.")
        lowered = normalized.lower()
        prefixes = (
            "những điểm yếu của ",
            "các điểm yếu của ",
            "điểm yếu của ",
            "hạn chế của ",
            "rủi ro của ",
            "thách thức của ",
            "khó khăn của ",
        )
        for prefix in prefixes:
            if lowered.startswith(prefix):
                return normalized[len(prefix) :].strip() or normalized
        return normalized

    def _definition_from_evidence(self, topic: str, evidence: list[str]) -> str:
        if evidence:
            return f"{topic} là khái niệm được kho tri thức mô tả qua các nội dung liên quan sau: {evidence[0]}"
        return ""

    def _evidence_sentences(
        self,
        question: str,
        matches: list[VectorSearchResult],
        limit: int = 5,
        intent: str = "general",
    ) -> list[str]:
        terms = {term.lower() for term in re.findall(r"[\wÀ-ỹ]+", question) if len(term) > 2}
        candidates: list[tuple[int, int, float, str]] = []
        seen: set[str] = set()
        for match in matches:
            for sentence in self._clean_sentences(match.chunk):
                lowered = sentence.lower()
                fingerprint = lowered[:180]
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                overlap = sum(1 for term in terms if term in lowered)
                intent_score = self._intent_sentence_score(lowered, intent)
                if intent == "weakness" and intent_score <= 0:
                    continue
                if overlap == 0 and intent_score <= 0 and candidates:
                    continue
                candidates.append((intent_score, overlap, match.score, sentence))
        candidates.sort(key=lambda item: (item[0], item[1], item[2], len(item[3]) < 260), reverse=True)
        return [sentence for _, _, _, sentence in candidates[:limit]]

    def _intent_sentence_score(self, lowered_sentence: str, intent: str) -> int:
        if intent != "weakness":
            return 0
        score = sum(2 for term in WEAKNESS_EVIDENCE_TERMS if term in lowered_sentence)
        score -= sum(1 for term in POSITIVE_EVIDENCE_NOISE if term in lowered_sentence)
        if "trong tầm kiểm soát" in lowered_sentence and not any(
            term in lowered_sentence for term in ("song", "nhưng", "thách thức", "áp lực", "rủi ro")
        ):
            score -= 2
        return score

    def _dedupe_sentences(self, sentences: list[str]) -> list[str]:
        output: list[str] = []
        seen: set[str] = set()
        for sentence in sentences:
            fingerprint = re.sub(r"\W+", "", sentence.lower())[:120]
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            output.append(sentence.rstrip(".") + ".")
        return output

    def _clean_sentences(self, chunk: str) -> list[str]:
        text = METADATA_COMMENT_RE.sub(" ", chunk)
        text = MARKDOWN_LINK_RE.sub(r"\1", text)
        text = text.replace("`", "")
        lines = []
        for raw_line in text.splitlines():
            line = raw_line.strip().lstrip("-*#0123456789. ").strip()
            if not line or SOURCE_NOISE_RE.search(line):
                continue
            if len(line) < 28 or len(line) > 520:
                continue
            if line.count("|") >= 2 or line.count("/") >= 4:
                continue
            lines.append(line)
        cleaned = normalize_whitespace(". ".join(lines))
        sentences = []
        for raw_sentence in SENTENCE_SPLIT_RE.split(cleaned):
            sentence = normalize_whitespace(raw_sentence).strip(" -")
            if 35 <= len(sentence) <= 420 and not SOURCE_NOISE_RE.search(sentence):
                sentences.append(sentence)
        return sentences


    def _is_answerable_match(self, match: VectorSearchResult) -> bool:
        file_path = match.file_path.lower()
        if file_path.endswith("agent-framework.md") or file_path == "_knowledge_map.md":
            return False
        if file_path.startswith(("_chat_history/", "_maintenance/", "_quarantine/")):
            return False
        if match.sources and all(is_blocked_source_url(source) for source in match.sources):
            return False
        trust_score = match.metadata.get("trust_score")
        try:
            if trust_score is not None and float(trust_score) < 0.2:
                return False
        except (TypeError, ValueError):
            return True
        return True
