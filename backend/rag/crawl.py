"""Fetch and extract content from allowlisted official sources."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from urllib.parse import urljoin, urlparse

import httpx
import trafilatura
from pypdf import PdfReader

from backend.rag.sources import SourceEntry, is_url_allowed, load_allowlist, lookup_source_entry

_FETCH_HEADERS = {
    "User-Agent": "MuunganoGPT/1.0 (Official Tanzania Union Educator; +https://tanzania.go.tz)",
    "Accept": "text/html,application/xhtml+xml,application/pdf",
    "Accept-Language": "sw,en;q=0.9",
}

_MUUNGANO_KEYWORDS = re.compile(
    r"muungano|union|tanganyika|zanzibar|articles of union|mambo ya muungano|"
    r"jamhuri ya muungano|united republic",
    re.IGNORECASE,
)

_MUUNGANO_DOC_TYPES = frozenset({
    "articles_of_union",
    "union_act",
    "official_faq",
    "government_publication",
    "constitution",
})


@dataclass
class CrawledPage:
    url: str
    title: str
    text: str
    document_name: str
    document_type: str
    section_title: str
    institution: str
    language: str
    priority: int
    publication_date: str
    fetched_at: str


def _is_pdf_url(url: str) -> bool:
    return urlparse(url).path.lower().endswith(".pdf")


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def _extract_title(html: str, fallback: str) -> str:
    meta = trafilatura.extract_metadata(html)
    if meta and meta.title:
        return meta.title.strip()
    m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
    return m.group(1).strip() if m else fallback


def _is_muungano_relevant(text: str, entry: SourceEntry | None) -> bool:
    if entry and entry.document_type in _MUUNGANO_DOC_TYPES:
        return len(text) >= 80
    return bool(_MUUNGANO_KEYWORDS.search(text))


def fetch_page(url: str, timeout: float = 45.0) -> CrawledPage | None:
    if not is_url_allowed(url):
        return None

    entry = lookup_source_entry(url)
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers=_FETCH_HEADERS) as client:
            response = client.get(url)
            response.raise_for_status()
            content_type = (response.headers.get("content-type") or "").lower()
            is_pdf = _is_pdf_url(url) or "pdf" in content_type

            if is_pdf:
                text = _extract_pdf_text(response.content)
                html = ""
            else:
                html = response.text
                text = trafilatura.extract(html, include_comments=False, include_tables=True) or ""
                text = re.sub(r"\s+", " ", text).strip()
    except Exception:
        return None

    if len(text) < 80:
        return None

    if not _is_muungano_relevant(text, entry):
        return None

    title = entry.document_name if entry and entry.document_name else url
    if html:
        title = _extract_title(html, title)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return CrawledPage(
        url=url,
        title=title or (entry.document_name if entry else "Government Page"),
        text=text,
        document_name=entry.document_name if entry and entry.document_name else title,
        document_type=entry.document_type if entry else "official_faq",
        section_title=entry.section_title if entry else "",
        institution=entry.institution if entry else "",
        language=entry.language if entry else "mixed",
        priority=entry.priority if entry else 3,
        publication_date=entry.publication_date if entry and entry.publication_date else now,
        fetched_at=now,
    )


def discover_links(html: str, base_url: str, max_links: int = 30) -> list[str]:
    """Find same-domain links that may contain Muungano content."""
    host = urlparse(base_url).netloc
    found: list[str] = []
    for match in re.finditer(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE):
        href = match.group(1).split("#")[0].strip()
        if not href or href.startswith(("mailto:", "javascript:", "tel:")):
            continue
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.netloc != host:
            continue
        if not is_url_allowed(absolute):
            continue
        path = (parsed.path or "").lower()
        if any(k in path for k in ("muungano", "union", "katiba", "constitution", "faq", "publications")):
            if absolute not in found:
                found.append(absolute)
        if path.endswith(".pdf") and ("muungano" in path.lower() or "union" in path.lower()):
            if absolute not in found:
                found.append(absolute)
        if len(found) >= max_links:
            break
    return found


def crawl_allowlist(max_pages_per_seed: int = 5) -> list[CrawledPage]:
    """Crawl seed URLs from allowlist; optionally follow Muungano-related links."""
    allowlist = load_allowlist()
    pages: list[CrawledPage] = []
    seen: set[str] = set()

    for entry in allowlist.entries:
        seeds = [entry.url]
        try:
            with httpx.Client(timeout=20.0, follow_redirects=True, headers=_FETCH_HEADERS) as client:
                resp = client.get(entry.url)
                if resp.status_code == 200:
                    seeds.extend(discover_links(resp.text, entry.url, max_links=max_pages_per_seed))
        except Exception:
            pass

        for url in seeds:
            norm = url.rstrip("/")
            if norm in seen:
                continue
            seen.add(norm)
            page = fetch_page(url)
            if page:
                pages.append(page)

    return pages
