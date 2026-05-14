from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ApprovalDecision:
    action: str
    risk_level: str
    approval_required: bool
    approved: bool
    reason: str

    @property
    def allowed(self) -> bool:
        return not self.approval_required or self.approved

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed"] = self.allowed
        return data


class ApprovalPolicy:
    HIGH_RISK_ACTIONS = {
        "delete_knowledge": "Deleting knowledge removes local source material, metadata, and vector entries.",
        "cleanup_knowledge": "Cleanup can quarantine files and remove them from metadata/vector indexes.",
        "apply_prompt_version": "Prompt changes can alter production agent behavior.",
        "apply_workflow_suggestion": "Workflow changes can alter production orchestration.",
        "external_api_write": "External writes can affect systems outside the local workspace.",
        "production_db_write": "Production database writes can permanently alter business data.",
    }

    LOW_RISK_ACTIONS = {
        "local_search": "Local search/crawl only gathers knowledge.",
        "build_local_knowledge": "Local knowledge build writes Markdown inside the configured knowledge base.",
        "read_knowledge": "Read-only knowledge access.",
    }

    def evaluate(self, action: str, *, approved: bool = False) -> ApprovalDecision:
        normalized = action.strip().lower()
        if normalized in self.HIGH_RISK_ACTIONS:
            return ApprovalDecision(
                action=normalized,
                risk_level="high",
                approval_required=True,
                approved=approved,
                reason=self.HIGH_RISK_ACTIONS[normalized],
            )
        reason = self.LOW_RISK_ACTIONS.get(normalized, "No high-risk policy matched.")
        return ApprovalDecision(
            action=normalized,
            risk_level="low",
            approval_required=False,
            approved=approved,
            reason=reason,
        )
