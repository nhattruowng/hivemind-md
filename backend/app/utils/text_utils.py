import re
import unicodedata
from hashlib import sha256


WHITESPACE_RE = re.compile(r"\s+")


def normalize_whitespace(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text or "").strip()


def clean_text(text: str) -> str:
    lines = []
    for raw_line in (text or "").splitlines():
        line = normalize_whitespace(raw_line)
        if not line:
            continue
        lowered = line.lower()
        if lowered in {"cookie policy", "privacy policy", "terms of service"}:
            continue
        if len(line) < 4:
            continue
        lines.append(line)
    return "\n\n".join(lines)


def slugify(value: str, fallback: str = "knowledge") -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()
    if not slug:
        digest = sha256((value or fallback).encode("utf-8")).hexdigest()[:10]
        slug = f"{fallback}-{digest}"
    return slug[:96].strip("-") or fallback


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.3))


def chunk_text(text: str, target_tokens: int = 800) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in (text or "").split("\n\n") if paragraph.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for paragraph in paragraphs:
        paragraph_tokens = estimate_tokens(paragraph)
        if current and current_tokens + paragraph_tokens > target_tokens:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            current_tokens = paragraph_tokens
        else:
            current.append(paragraph)
            current_tokens += paragraph_tokens

    if current:
        chunks.append("\n\n".join(current))
    return chunks


def compact_preview(text: str, max_chars: int = 900) -> str:
    normalized = normalize_whitespace(text)
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."

