from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = Field(default="HiveMind MD", alias="APP_NAME")
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_main_model: str = Field(default="qwen2.5:7b", alias="OLLAMA_MAIN_MODEL")
    ollama_light_model: str = Field(default="qwen2.5:3b", alias="OLLAMA_LIGHT_MODEL")
    ollama_embed_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL")

    database_url: str = Field(default="sqlite:///./hivemind.db", alias="DATABASE_URL")
    knowledge_dir: str = Field(default="./knowledge", alias="KNOWLEDGE_DIR")
    vector_store_dir: str = Field(default="./vector_store", alias="VECTOR_STORE_DIR")

    default_search_limit: int = Field(default=5, alias="DEFAULT_SEARCH_LIMIT")
    default_chunk_size: int = Field(default=800, alias="DEFAULT_CHUNK_SIZE")

    request_timeout_seconds: int = Field(default=20, alias="REQUEST_TIMEOUT_SECONDS")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", alias="CORS_ORIGINS")

    self_improvement_enabled: bool = Field(default=True, alias="SELF_IMPROVEMENT_ENABLED")
    auto_save_lessons: bool = Field(default=True, alias="AUTO_SAVE_LESSONS")
    auto_save_prompt_versions: bool = Field(default=True, alias="AUTO_SAVE_PROMPT_VERSIONS")
    allow_auto_prompt_apply: bool = Field(default=False, alias="ALLOW_AUTO_PROMPT_APPLY")
    allow_auto_workflow_apply: bool = Field(default=False, alias="ALLOW_AUTO_WORKFLOW_APPLY")
    allow_auto_code_patch: bool = Field(default=False, alias="ALLOW_AUTO_CODE_PATCH")
    reflection_score_threshold: int = Field(default=42, alias="REFLECTION_SCORE_THRESHOLD")

    model_config = SettingsConfigDict(
        env_file=(BACKEND_ROOT.parent / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )

    @property
    def knowledge_path(self) -> Path:
        return self._resolve_backend_path(self.knowledge_dir)

    @property
    def vector_store_path(self) -> Path:
        return self._resolve_backend_path(self.vector_store_dir)

    @property
    def database_path(self) -> Path:
        if not self.database_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// DATABASE_URL values are supported in the MVP.")
        raw_path = self.database_url.replace("sqlite:///", "", 1)
        return self._resolve_backend_path(raw_path)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def _resolve_backend_path(self, value: str) -> Path:
        candidate = Path(value)
        if candidate.is_absolute():
            return candidate
        return (BACKEND_ROOT / candidate).resolve()


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.knowledge_path.mkdir(parents=True, exist_ok=True)
    settings.vector_store_path.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
