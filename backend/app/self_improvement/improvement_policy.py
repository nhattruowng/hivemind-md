from dataclasses import dataclass

from app.config import Settings, get_settings


@dataclass(frozen=True)
class ImprovementPolicy:
    auto_save_lessons: bool = True
    auto_save_prompt_versions: bool = True
    allow_auto_prompt_apply: bool = False
    allow_auto_workflow_apply: bool = False
    allow_auto_code_patch: bool = False
    reflection_score_threshold: int = 42

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "ImprovementPolicy":
        settings = settings or get_settings()
        return cls(
            auto_save_lessons=settings.auto_save_lessons,
            auto_save_prompt_versions=settings.auto_save_prompt_versions,
            allow_auto_prompt_apply=settings.allow_auto_prompt_apply,
            allow_auto_workflow_apply=settings.allow_auto_workflow_apply,
            allow_auto_code_patch=settings.allow_auto_code_patch,
            reflection_score_threshold=settings.reflection_score_threshold,
        )

    def can_auto_apply_prompt(self, risk_level: str, requested: bool) -> bool:
        return self.allow_auto_prompt_apply and requested and risk_level == "low"

    def can_auto_apply_workflow(self, risk_level: str, requested: bool) -> bool:
        return self.allow_auto_workflow_apply and requested and risk_level == "low"

    def can_create_code_patch(self) -> bool:
        return self.allow_auto_code_patch


AUTO_SAVE_LESSONS = True
AUTO_SAVE_PROMPT_VERSIONS = True
ALLOW_AUTO_PROMPT_APPLY = False
ALLOW_AUTO_WORKFLOW_APPLY = False
ALLOW_AUTO_CODE_PATCH = False
REFLECTION_SCORE_THRESHOLD = 42
