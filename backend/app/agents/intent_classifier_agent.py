from typing import Any

from app.agents.base_agent import BaseAgent
from app.utils.text_utils import normalize_whitespace


BUILD_TERMS = ("build knowledge", "refresh", "crawl", "index", "xây tri thức", "cập nhật tri thức")
CODE_TERMS = ("code", "bug", "debug", "test", "refactor", "api", "lỗi", "sửa code", "review")
WORKFLOW_TERMS = ("workflow", "pipeline", "quy trình", "automation", "tự động hóa")
DOCUMENT_TERMS = ("document", "markdown", "doc", "viết tài liệu", "tài liệu")
SETTINGS_TERMS = ("settings", "config", "model", "ollama", "cấu hình")
ACTION_TERMS = ("delete", "xóa", "xoá", "apply", "archive", "send", "gửi", "ghi")
QUESTION_TERMS = ("?", "là gì", "what", "why", "how", "vì sao", "tại sao", "như thế nào")


class IntentClassifierAgent(BaseAgent):
    name = "IntentClassifierAgent"
    description = "Classify user requests for routing, planning, and policy checks."

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        message = normalize_whitespace(str(kwargs.get("message") or kwargs.get("request") or ""))
        page_context = normalize_whitespace(str(kwargs.get("page_context") or ""))
        lowered = f"{message} {page_context}".lower()
        intent, confidence, reason = self._classify(lowered)
        requires_tools = intent in {"research", "build_knowledge", "code", "debug", "workflow", "automation", "settings"}
        requires_knowledge = intent in {"chat", "research", "build_knowledge", "document", "unknown"}
        requires_approval = any(term in lowered for term in ACTION_TERMS)
        data = {
            "intent": intent,
            "confidence": confidence,
            "requires_tools": requires_tools,
            "requires_knowledge": requires_knowledge,
            "requires_approval": requires_approval,
            "reason": reason,
        }
        risk_level = "medium" if requires_approval else "low"
        return self.success("Classified request intent.", data, confidence=confidence, risk_level=risk_level)

    def _classify(self, lowered: str) -> tuple[str, float, str]:
        if any(term in lowered for term in BUILD_TERMS):
            return "build_knowledge", 0.86, "Request asks to refresh, crawl, index, or build knowledge."
        if any(term in lowered for term in CODE_TERMS):
            if "debug" in lowered or "lỗi" in lowered:
                return "debug", 0.84, "Request mentions debugging or errors."
            return "code", 0.8, "Request mentions code or developer workflow."
        if any(term in lowered for term in WORKFLOW_TERMS):
            if "automation" in lowered or "tự động hóa" in lowered:
                return "automation", 0.82, "Request mentions automation."
            return "workflow", 0.82, "Request mentions workflow or pipeline."
        if any(term in lowered for term in DOCUMENT_TERMS):
            return "document", 0.72, "Request mentions documents or Markdown."
        if any(term in lowered for term in SETTINGS_TERMS):
            return "settings", 0.74, "Request mentions configuration or runtime settings."
        if any(term in lowered for term in QUESTION_TERMS):
            return "chat", 0.7, "Request looks like a question."
        return "unknown", 0.35, "No strong intent signal matched."
