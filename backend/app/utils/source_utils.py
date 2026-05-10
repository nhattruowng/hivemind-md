from urllib.parse import urlparse


HIGH_TRUST_SUFFIXES = (".gov", ".edu")
MEDIUM_TRUST_HOST_HINTS = (
    "wikipedia.org",
    "github.com",
    "docs.",
    "developer.",
    "research.",
    "arxiv.org",
    "worldbank.org",
    "imf.org",
    "oecd.org",
    "adb.org",
    "gso.gov.vn",
    "mof.gov.vn",
    "sbv.gov.vn",
    "vneconomy.vn",
    "vietnamfinance.vn",
    "cafef.vn",
    "vietstock.vn",
)
BLOCKED_HOST_HINTS = (
    "bookmarktune.com",
    "opensocialfactory.com",
    "ohiobitcoin.com",
    "blogspot.",
    "tumblr.",
)
BLOCKED_PATH_HINTS = (
    "/story",
    "/stories",
    "/bookmark",
    "/classified",
    "/directory",
)
LOW_VALUE_TITLE_HINTS = (
    "miễn phí",
    "free download",
    "rumored buzz",
    "story",
    "bookmark",
)


def source_host(url: str) -> str:
    parsed = urlparse(url)
    return (parsed.netloc or parsed.path).lower().removeprefix("www.")


def is_blocked_source_url(url: str) -> bool:
    parsed = urlparse(url)
    host = source_host(url)
    path = parsed.path.lower()
    return any(hint in host for hint in BLOCKED_HOST_HINTS) or any(hint in path for hint in BLOCKED_PATH_HINTS)


def is_low_value_source(source: dict[str, str]) -> bool:
    title = str(source.get("title", "")).lower()
    snippet = str(source.get("snippet", "")).lower()
    url = str(source.get("url", ""))
    return is_blocked_source_url(url) or any(hint in title or hint in snippet for hint in LOW_VALUE_TITLE_HINTS)


def score_source(url: str, content_length: int) -> tuple[float, str, str]:
    host = source_host(url)
    score = 0.45
    reasons = []

    if is_blocked_source_url(url):
        return 0.0, "blocked", "blocked low-quality or spam-like source"
    if url.startswith("local://"):
        score = 0.25
        reasons.append("fallback local source, not a crawled web page")
    if any(host.endswith(suffix) for suffix in HIGH_TRUST_SUFFIXES):
        score += 0.35
        reasons.append("institutional domain")
    if any(hint in host for hint in MEDIUM_TRUST_HOST_HINTS):
        score += 0.2
        reasons.append("recognized documentation or reference host")
    if content_length > 3000:
        score += 0.15
        reasons.append("substantial extracted content")
    elif content_length < 600:
        score -= 0.15
        reasons.append("limited content extracted")

    score = max(0.0, min(1.0, round(score, 2)))
    if score >= 0.8:
        level = "high"
    elif score >= 0.5:
        level = "medium"
    else:
        level = "low"

    if not reasons:
        reasons.append("general web source with basic metadata")
    return score, level, "; ".join(reasons)
