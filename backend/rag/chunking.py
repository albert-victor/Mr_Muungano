"""Token-based semantic text chunking for Muungano knowledge base."""
from __future__ import annotations

import re
from dataclasses import dataclass

import tiktoken

from backend.config import settings

_ENC: tiktoken.Encoding | None = None


def get_token_encoder() -> tiktoken.Encoding:
    global _ENC
    if _ENC is None:
        try:
            _ENC = tiktoken.get_encoding(settings.chunk_token_encoding)
        except Exception:
            _ENC = tiktoken.get_encoding("cl100k_base")
    return _ENC


def count_tokens(text: str) -> int:
    return len(get_token_encoder().encode(text))


@dataclass
class TextChunk:
    text: str
    section_title: str = ""
    token_count: int = 0


_HEADING_RE = re.compile(
    r"^(?:#{1,6}\s+|[A-Z][A-Z0-9\s\-–—]{4,}[:\.]?\s*$|\d+\.\s+[A-Z])",
    re.MULTILINE,
)


def _split_semantic_units(text: str) -> list[tuple[str, str]]:
    """Split into (section_title, paragraph) units preserving headings."""
    text = text.strip()
    if not text:
        return []

    units: list[tuple[str, str]] = []
    current_heading = ""

    blocks = re.split(r"\n{2,}", text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split("\n")
        first = lines[0].strip()

        if _HEADING_RE.match(first) or (len(first) < 120 and first.isupper()):
            current_heading = first.lstrip("#").strip()
            body = "\n".join(lines[1:]).strip()
            if body:
                units.append((current_heading, body))
            elif len(first) > 3:
                units.append((current_heading, first))
            continue

        units.append((current_heading, block))

    if not units and text:
        units.append(("", text))

    return units


def _take_overlap_tokens(text: str, overlap_tokens: int) -> str:
    enc = get_token_encoder()
    tokens = enc.encode(text)
    if len(tokens) <= overlap_tokens:
        return text
    return enc.decode(tokens[-overlap_tokens:])


def semantic_chunk_text(
    text: str,
    min_tokens: int | None = None,
    max_tokens: int | None = None,
    overlap_tokens: int | None = None,
    section_title: str = "",
) -> list[TextChunk]:
    """
    Merge semantic units into chunks of min_tokens–max_tokens with overlap.
    Never uses arbitrary character cuts — respects paragraphs and headings.
    """
    min_tokens = min_tokens or settings.chunk_min_tokens
    max_tokens = max_tokens or settings.chunk_max_tokens
    overlap_tokens = overlap_tokens or settings.chunk_overlap_tokens
    target_tokens = (min_tokens + max_tokens) // 2

    units = _split_semantic_units(text)
    if not units:
        return []

    chunks: list[TextChunk] = []
    buffer_parts: list[str] = []
    buffer_heading = section_title
    buffer_tokens = 0

    def flush_buffer() -> None:
        nonlocal buffer_parts, buffer_tokens, buffer_heading
        if not buffer_parts:
            return
        joined = "\n\n".join(buffer_parts).strip()
        if joined:
            chunks.append(
                TextChunk(
                    text=joined,
                    section_title=buffer_heading,
                    token_count=count_tokens(joined),
                )
            )
        buffer_parts = []
        buffer_tokens = 0

    for unit_heading, paragraph in units:
        heading = unit_heading or buffer_heading or section_title
        para_tokens = count_tokens(paragraph)

        if para_tokens > max_tokens:
            flush_buffer()
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            sent_buf: list[str] = []
            sent_tokens = 0
            for sent in sentences:
                st = count_tokens(sent)
                if sent_tokens + st > max_tokens and sent_buf:
                    piece = " ".join(sent_buf)
                    chunks.append(
                        TextChunk(text=piece, section_title=heading, token_count=count_tokens(piece))
                    )
                    overlap = _take_overlap_tokens(piece, overlap_tokens)
                    sent_buf = [overlap, sent] if overlap else [sent]
                    sent_tokens = count_tokens(" ".join(sent_buf))
                else:
                    sent_buf.append(sent)
                    sent_tokens += st
            if sent_buf:
                piece = " ".join(sent_buf)
                chunks.append(
                    TextChunk(text=piece, section_title=heading, token_count=count_tokens(piece))
                )
            buffer_heading = heading
            continue

        if buffer_tokens + para_tokens > max_tokens and buffer_parts:
            flush_buffer()
            if chunks and overlap_tokens > 0:
                overlap = _take_overlap_tokens(chunks[-1].text, overlap_tokens)
                if overlap:
                    buffer_parts = [overlap]
                    buffer_tokens = count_tokens(overlap)
                    buffer_heading = chunks[-1].section_title or heading

        if not buffer_parts:
            buffer_heading = heading

        buffer_parts.append(paragraph)
        buffer_tokens += para_tokens

        if buffer_tokens >= target_tokens:
            flush_buffer()

    flush_buffer()
    return chunks
