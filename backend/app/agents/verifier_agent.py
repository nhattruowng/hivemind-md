import re
from typing import Any

from app.agents.base_agent import BaseAgent
from app.utils.text_utils import compact_preview, normalize_whitespace


NO_ANSWER_TERMS = (
    "chưa có đủ dữ liệu",
    "không có đủ dữ liệu",
    "knowledge base chưa",
    "kho tri thức chưa",
    "i don't know",
    "not enough context",
)
RISK_TERMS = (
    "xóa",
    "xoá",
    "delete",
    "drop",
    "production",
    "database",
    "db",
    "gửi email",
    "send email",
)
TOKEN_RE = re.compile(r"[a-zA-Z0-9À-ỹ]{3,}")
SENTENCE_RE = re.compile(r"(?<=[.!?。])\s+|\n+")
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "this",
    "that",
    "per",
    "và",
    "của",
    "cho",
    "với",
    "một",
    "các",
    "những",
}


class VerifierAgent(BaseAgent):
    name = "VerifierAgent"
    description = "Verify answer grounding, citations, missing points, and action risk."

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        question = normalize_whitespace(str(kwargs.get("question", "")))
        answer = normalize_whitespace(str(kwargs.get("answer", "")))
        retrieval = kwargs.get("retrieval") if isinstance(kwargs.get("retrieval"), list) else []
        citations = kwargs.get("citations") if isinstance(kwargs.get("citations"), list) else []
        sources = kwargs.get("sources") if isinstance(kwargs.get("sources"), list) else []
        confidence = self._float(kwargs.get("confidence"), default=0.0)
        needs_refresh = bool(kwargs.get("needs_refresh", False))

        evidence_text = self._evidence_text(retrieval, citations)
        no_answer = self._is_no_answer(answer)
        unsupported_claims = [] if no_answer else self._unsupported_claims(answer, evidence_text)
        source_count = len(citations) or len(sources)
        citations_present = source_count > 0 or no_answer
        grounding_score = self._grounding_score(answer, evidence_text, no_answer=no_answer)
        missing_points = self._missing_points(question, answer, citations_present=citations_present)
        risk_level = self._risk_level(question, answer)
        verified = (
            citations_present
            and not unsupported_claims
            and grounding_score >= 0.32
            and risk_level != "high"
        ) or no_answer
        final_action = "answer"
        if no_answer or needs_refresh:
            final_action = "refresh" if needs_refresh else "no_answer"
        if risk_level == "high":
            final_action = "approval_required"

        verifier_confidence = min(1.0, max(0.0, (confidence * 0.55) + (grounding_score * 0.45)))
        return self.success(
            "Verified answer grounding." if verified else "Verifier found answer risks.",
            {
                "verified": verified,
                "confidence": round(verifier_confidence, 4),
                "grounding_score": round(grounding_score, 4),
                "unsupported_claims": unsupported_claims,
                "missing_points": missing_points,
                "risk_level": risk_level,
                "final_action": final_action,
                "citations_present": citations_present,
                "source_count": source_count,
            },
        )

    def _evidence_text(self, retrieval: list[Any], citations: list[Any]) -> str:
        parts: list[str] = []
        for item in retrieval[:8]:
            if isinstance(item, dict):
                parts.append(str(item.get("preview", "")))
                parts.append(str(item.get("file_path", "")))
                for source in item.get("sources", []) or []:
                    parts.append(str(source))
        for item in citations[:8]:
            if isinstance(item, dict):
                parts.append(str(item.get("preview", "")))
                parts.append(str(item.get("file_path", "")))
                for source in item.get("sources", []) or []:
                    parts.append(str(source))
        return normalize_whitespace(" ".join(parts).lower())

    def _unsupported_claims(self, answer: str, evidence_text: str) -> list[str]:
        if not evidence_text:
            return [compact_preview(answer, 220)] if answer else []
        unsupported: list[str] = []
        for sentence in self._sentences(answer):
            if self._is_citation_line(sentence):
                continue
            terms = self._terms(sentence)
            if len(terms) < 3:
                continue
            overlap = sum(1 for term in terms if term in evidence_text)
            if overlap / max(1, len(terms)) < 0.3:
                unsupported.append(compact_preview(sentence, 180))
            if len(unsupported) >= 5:
                break
        return unsupported

    def _grounding_score(self, answer: str, evidence_text: str, *, no_answer: bool) -> float:
        if no_answer:
            return 1.0
        answer_terms = self._terms(answer)
        if not answer_terms:
            return 0.0
        if not evidence_text:
            return 0.0
        overlap = sum(1 for term in answer_terms if term in evidence_text)
        return min(1.0, overlap / max(1, len(answer_terms)))

    def _missing_points(self, question: str, answer: str, *, citations_present: bool) -> list[str]:
        missing: list[str] = []
        lowered_question = question.lower()
        lowered_answer = answer.lower()
        if not citations_present:
            missing.append("citations")
        if any(term in lowered_question for term in ("chi phí", "cost")) and not any(term in lowered_answer for term in ("chi phí", "cost", "giá")):
            missing.append("cost estimate")
        if any(term in lowered_question for term in ("rủi ro", "risk")) and not any(term in lowered_answer for term in ("rủi ro", "risk", "hạn chế")):
            missing.append("risk discussion")
        return missing

    def _risk_level(self, question: str, answer: str) -> str:
        joined = f"{question} {answer}".lower()
        if any(term in joined for term in RISK_TERMS):
            return "high"
        return "low"

    def _is_no_answer(self, answer: str) -> bool:
        lowered = answer.lower()
        return any(term in lowered for term in NO_ANSWER_TERMS)

    def _sentences(self, answer: str) -> list[str]:
        return [normalize_whitespace(item).strip("- ") for item in SENTENCE_RE.split(answer) if normalize_whitespace(item)]

    def _terms(self, value: str) -> set[str]:
        return {
            term.lower()
            for term in TOKEN_RE.findall(value)
            if not term.startswith("http") and term.lower() not in STOPWORDS
        }

    def _is_citation_line(self, sentence: str) -> bool:
        lowered = sentence.lower()
        return lowered.startswith("nguồn") or lowered.startswith("[s") or "source" in lowered[:32]

    def _float(self, value: Any, *, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
