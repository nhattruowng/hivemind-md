from pydantic import BaseModel, Field

from app.schemas.agent_schema import AgentLog, BuildMode


class KnowledgeItem(BaseModel):
    title: str
    category: str
    file_path: str
    updated_at: str
    trust_score: float | None = None


class KnowledgeReadResponse(BaseModel):
    content: str


class KnowledgeDeleteRequest(BaseModel):
    file_path: str
    approved: bool = False


class KnowledgeDeleteResponse(BaseModel):
    status: str
    deleted: str


class KnowledgeRefreshRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    category: str = Field(default="general", min_length=1)
    mode: BuildMode = "standard"


class KnowledgeRefreshResponse(BaseModel):
    status: str
    topic: str
    category: str
    files: list[str]
    map_file: str
    agent_logs: list[AgentLog]


class KnowledgeMapResponse(BaseModel):
    map_file: str
    content: str


class KnowledgeCleanupRequest(BaseModel):
    dry_run: bool = False
    min_trust: float = Field(default=0.2, ge=0.0, le=1.0)
    approved: bool = False


class KnowledgeCleanupResponse(BaseModel):
    status: str
    dry_run: bool
    scanned_files: int
    duplicate_groups: int
    noise_files: int
    quarantined_files: list[str]
    report_file: str
    map_file: str
    agent_logs: list[AgentLog]
