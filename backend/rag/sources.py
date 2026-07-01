"""Official source allowlist, tiers, and URL validation."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import yaml

from backend.config import settings

BLOCKED_SOURCE_KINDS = frozenset({"blog", "opinion", "personal", "unofficial"})


@dataclass
class SourceEntry:
    url: str
    document_type: str
    document_name: str = ""
    section_title: str = ""
    institution: str = ""
    language: str = "mixed"
    priority: int = 3
    tier: int = 1
    publication_date: str = ""


@dataclass
class Allowlist:
    entries: list[SourceEntry] = field(default_factory=list)
    allowed_domains: set[str] = field(default_factory=set)
    blocked_patterns: list[str] = field(default_factory=list)


def _yaml_path() -> Path:
    return Path(settings.sources_allowlist_path)


def load_allowlist() -> Allowlist:
    path = _yaml_path()
    if not path.exists():
        return Allowlist()

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    entries: list[SourceEntry] = []
    domains: set[str] = set()

    for tier_key, tier_num in (("tier_1", 1), ("tier_2", 2), ("tier_3", 3)):
        for group in data.get(tier_key, []) or []:
            institution = group.get("institution", group.get("name", ""))
            language = group.get("language", "mixed")
            priority = int(group.get("priority", tier_num))
            for item in group.get("urls", []) or []:
                if not item or not item.get("url"):
                    continue
                url = item["url"].strip()
                parsed = urlparse(url)
                if parsed.netloc:
                    domains.add(parsed.netloc.lower().lstrip("www."))
                entries.append(
                    SourceEntry(
                        url=url,
                        document_type=item.get("document_type", "government_publication"),
                        document_name=item.get("document_name", group.get("name", "")),
                        section_title=item.get("section_title", ""),
                        institution=institution,
                        language=language,
                        priority=priority,
                        tier=tier_num,
                        publication_date=item.get("publication_date", ""),
                    )
                )

    policy = data.get("policy", {})
    never = policy.get("never_use_as_primary", [])
    blocked = [f"*{k}*" for k in never]

    return Allowlist(entries=entries, allowed_domains=domains, blocked_patterns=blocked)


def is_url_allowed(url: str, allowlist: Allowlist | None = None) -> bool:
    """Reject blogs, personal pages, and domains outside the allowlist."""
    allowlist = allowlist or load_allowlist()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False

    host = (parsed.netloc or "").lower().lstrip("www.")
    if not host:
        return False

    # Obvious non-official path patterns
    path_lower = (parsed.path or "").lower()
    blocked_fragments = (
        "/blog/", "/opinion/", "/personal/", "/user/", "/tag/",
        "facebook.com", "instagram.com/personal", "tiktok.com/@",
    )
    if any(b in url.lower() for b in blocked_fragments):
        return False

    if not allowlist.allowed_domains:
        return True

    return any(host == d or host.endswith("." + d) for d in allowlist.allowed_domains)


def lookup_source_entry(url: str, allowlist: Allowlist | None = None) -> SourceEntry | None:
    allowlist = allowlist or load_allowlist()
    normalized = url.rstrip("/")
    for entry in allowlist.entries:
        if entry.url.rstrip("/") == normalized:
            return entry
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower().lstrip("www.")
    for entry in allowlist.entries:
        ep = urlparse(entry.url)
        if (ep.netloc or "").lower().lstrip("www.") == host:
            return entry
    return None


def build_chunk_metadata(
    *,
    document_name: str,
    document_type: str,
    source_url: str = "",
    publication_date: str = "",
    page_number: int = 0,
    section_title: str = "",
    language: str = "mixed",
    government_institution: str = "",
    priority_level: int = 3,
    source_file: str = "",
    source_kind: str = "pdf",
    chunk_index: int = 0,
) -> dict:
    """Unified metadata schema for Chroma (primitive values only)."""
    return {
        "document_name": document_name,
        "document_title": document_name,
        "document_type": document_type,
        "source_url": source_url or "",
        "publication_date": publication_date or "",
        "page_number": int(page_number),
        "page": int(page_number),
        "section_title": section_title or "",
        "language": language,
        "government_institution": government_institution or "",
        "priority_level": int(priority_level),
        "priority": int(priority_level),
        "source_file": source_file or "",
        "source_kind": source_kind,
        "chunk_index": int(chunk_index),
    }
