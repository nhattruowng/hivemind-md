from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class DomainProfile:
    id: str
    name: str
    category: str
    description: str
    focus_areas: list[str]
    routing_keywords: list[str]
    worker_count: int = 4
    max_parallel_workers: int = 2
    use_llm_workers: int = 1
    min_trust_score: float = 0.15
    source_limits: dict[str, int] = field(
        default_factory=lambda: {"quick": 4, "standard": 8, "deep": 12}
    )
    trusted_domains: list[str] = field(default_factory=list)
    main_model: str | None = None
    light_model: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_PROFILES = {
    "general": DomainProfile(
        id="general",
        name="Tổng quát",
        category="general",
        description="Profile cân bằng cho chủ đề chưa rõ domain.",
        focus_areas=["overview", "core concepts", "workflow", "risks"],
        routing_keywords=[],
        worker_count=4,
        min_trust_score=0.1,
    ),
    "finance": DomainProfile(
        id="finance",
        name="Tài chính",
        category="finance",
        description="Tập trung thị trường, rủi ro, dữ liệu tài chính và bối cảnh kinh tế.",
        focus_areas=["market context", "financial instruments", "risk and regulation", "personal finance"],
        routing_keywords=[
            "finance",
            "financial",
            "stock",
            "market",
            "investment",
            "bank",
            "tài chính",
            "chứng khoán",
            "đầu tư",
            "ngân hàng",
        ],
        worker_count=4,
        min_trust_score=0.2,
        trusted_domains=[
            "vietnamfinance.vn",
            "cafef.vn",
            "vietstock.vn",
            "sbv.gov.vn",
            "mof.gov.vn",
            "worldbank.org",
            "imf.org",
        ],
    ),
    "economy": DomainProfile(
        id="economy",
        name="Kinh tế",
        category="economy",
        description="Tập trung kinh tế vĩ mô, chính sách, chỉ số, thị trường và bối cảnh Việt Nam/quốc tế.",
        focus_areas=[
            "kinh tế vĩ mô",
            "GDP lạm phát",
            "chính sách tiền tệ tài khóa",
            "thị trường lao động",
            "triển vọng kinh tế Việt Nam",
        ],
        routing_keywords=[
            "economy",
            "economic",
            "macroeconomy",
            "macro",
            "gdp",
            "inflation",
            "kinh tế",
            "kinh te",
            "vĩ mô",
            "vi mo",
            "lạm phát",
            "lam phat",
            "tăng trưởng",
            "tang truong",
        ],
        worker_count=5,
        min_trust_score=0.35,
        trusted_domains=[
            "gso.gov.vn",
            "mof.gov.vn",
            "sbv.gov.vn",
            "vneconomy.vn",
            "vietnamfinance.vn",
            "worldbank.org",
            "imf.org",
            "oecd.org",
            "adb.org",
        ],
    ),
    "programming": DomainProfile(
        id="programming",
        name="Lập trình",
        category="programming",
        description="Tập trung kiến trúc, API, triển khai, testing, security và performance.",
        focus_areas=["architecture", "implementation", "api and tooling", "testing and performance", "security"],
        routing_keywords=[
            "programming",
            "code",
            "software",
            "python",
            "javascript",
            "typescript",
            "backend",
            "frontend",
            "api",
            "lập trình",
            "mã nguồn",
        ],
        worker_count=5,
        min_trust_score=0.15,
    ),
    "ai": DomainProfile(
        id="ai",
        name="AI và tác nhân",
        category="ai",
        description="Tập trung mô hình, agent workflow, RAG, evaluation và vận hành local.",
        focus_areas=["model behavior", "agent workflow", "retrieval and memory", "evaluation", "operations"],
        routing_keywords=["ai", "llm", "agent", "rag", "ollama", "model", "trí tuệ nhân tạo", "tác nhân"],
        worker_count=5,
        min_trust_score=0.15,
    ),
}


class DomainProfileService:
    def list_profiles(self) -> list[dict[str, Any]]:
        return [profile.to_dict() for profile in DEFAULT_PROFILES.values()]

    def get_profile(self, profile_id: str | None = None, topic: str = "") -> DomainProfile:
        requested = (profile_id or "auto").strip().lower()
        if requested and requested != "auto":
            return DEFAULT_PROFILES.get(requested, DEFAULT_PROFILES["general"])

        lowered_topic = topic.lower()
        for profile in DEFAULT_PROFILES.values():
            if profile.id == "general":
                continue
            if any(keyword in lowered_topic for keyword in profile.routing_keywords):
                return profile
        return DEFAULT_PROFILES["general"]
