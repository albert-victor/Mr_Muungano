"""OpenRouter LLM integration for RAG chat."""
from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator

import httpx

from backend.config import max_tokens_for_tone, settings
from backend.rag.language import (
    FALLBACK_CHUNK_FORMAL,
    FALLBACK_CHUNK_YOUTH,
    FALLBACK_NO_CONTEXT,
    LANGUAGE_REMINDER,
    LANGUAGE_RULES,
    NO_CONTEXT_HINT,
    resolve_response_language,
)
from backend.rag.prompts import SYSTEM_PROMPT, get_tone_hint
from backend.rag.retriever import RetrievedChunk, format_context, retrieve

_http_client: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=90.0)
    return _http_client


async def close_http_client() -> None:
    global _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None


def _build_messages(
    question: str,
    context: str,
    history: list[dict],
    tone: str = "default",
    lang: str = "sw",
    has_chunks: bool = False,
) -> list[dict]:
    response_lang = resolve_response_language(question, lang, history)
    tone_hint = get_tone_hint(tone, response_lang)
    lang_rule = LANGUAGE_RULES[response_lang]

    if context:
        context_block = f"CONTEXT FROM OFFICIAL SOURCES:\n{context}"
    else:
        context_block = NO_CONTEXT_HINT[response_lang]

    system = (
        f"{SYSTEM_PROMPT}\n\n"
        f"LANGUAGE: {lang_rule}\n"
        f"TONE: {tone_hint}"
    )

    user_content = f"""{context_block}

QUESTION:
{question}

{LANGUAGE_REMINDER[response_lang]}"""

    messages: list[dict] = [{"role": "system", "content": system}]

    for msg in history[-settings.history_messages :]:
        role = msg.get("role", "user")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": msg.get("content", "")})

    messages.append({"role": "user", "content": user_content})
    return messages


async def chat(
    question: str,
    history: list[dict] | None = None,
    tone: str = "default",
    lang: str = "sw",
) -> dict:
    history = history or []
    response_lang = resolve_response_language(question, lang, history)
    chunks = await asyncio.to_thread(retrieve, question, None, tone, response_lang)
    context = format_context(chunks)

    if not settings.openrouter_api_key:
        return _fallback_response(question, chunks, context, tone, lang, history)

    messages = _build_messages(question, context, history, tone, lang, has_chunks=bool(chunks))
    client = _get_http_client()
    max_tokens = max_tokens_for_tone(tone)

    response = await client.post(
        f"{settings.openrouter_base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": settings.app_title,
        },
        json={
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": max_tokens,
        },
    )
    response.raise_for_status()
    data = response.json()

    answer = data["choices"][0]["message"]["content"]
    return {
        "answer": answer,
        "citations": [c.to_citation() for c in chunks],
        "model": settings.openrouter_model,
        "has_context": bool(chunks),
        "lang": response_lang,
    }


async def chat_stream(
    question: str,
    history: list[dict] | None = None,
    tone: str = "default",
    lang: str = "sw",
) -> AsyncIterator[str]:
    history = history or []
    yield json.dumps({"type": "status", "data": "preparing"}) + "\n"

    response_lang = resolve_response_language(question, lang, history)
    yield json.dumps({"type": "status", "data": "searching"}) + "\n"
    chunks = await asyncio.to_thread(retrieve, question, None, tone, response_lang)
    context = format_context(chunks)
    citations = [c.to_citation() for c in chunks]
    max_tokens = max_tokens_for_tone(tone)

    if not settings.openrouter_api_key:
        fallback = _fallback_response(question, chunks, context, tone, lang, history)
        yield json.dumps({"type": "citations", "data": citations}) + "\n"
        yield json.dumps({"type": "token", "data": fallback["answer"]}) + "\n"
        yield json.dumps({"type": "done", "data": {"has_context": bool(chunks)}}) + "\n"
        return

    messages = _build_messages(question, context, history, tone, lang, has_chunks=bool(chunks))

    yield json.dumps({"type": "status", "data": "generating"}) + "\n"
    yield json.dumps({"type": "citations", "data": citations}) + "\n"

    client = _get_http_client()
    truncated = False
    async with client.stream(
        "POST",
        f"{settings.openrouter_base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": settings.app_title,
        },
        json={
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": max_tokens,
            "stream": True,
        },
    ) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            if not line.startswith("data: "):
                continue
            payload = line[6:].strip()
            if payload == "[DONE]":
                break
            try:
                parsed = json.loads(payload)
                choice = parsed["choices"][0]
                delta = choice.get("delta", {})
                token = delta.get("content", "")
                if choice.get("finish_reason") == "length":
                    truncated = True
                if token:
                    yield json.dumps({"type": "token", "data": token}) + "\n"
            except (json.JSONDecodeError, KeyError, IndexError):
                continue

    yield json.dumps(
        {
            "type": "done",
            "data": {
                "has_context": bool(chunks),
                "model": settings.openrouter_model,
                "lang": response_lang,
                "truncated": truncated,
            },
        }
    ) + "\n"


def _fallback_response(
    question: str,
    chunks: list[RetrievedChunk],
    context: str,
    tone: str,
    lang: str,
    history: list[dict] | None = None,
) -> dict:
    response_lang = resolve_response_language(question, lang, history)

    if chunks:
        top = chunks[0]
        page = f" (page {top.page})" if top.page else ""
        if tone in ("youth", "simple", "student"):
            answer = FALLBACK_CHUNK_YOUTH[response_lang].format(excerpt=top.text[:400])
        else:
            answer = FALLBACK_CHUNK_FORMAL[response_lang].format(
                title=top.document_name,
                page=page,
                excerpt=top.text[:500],
            )
    else:
        answer = FALLBACK_NO_CONTEXT[response_lang]

    return {
        "answer": answer,
        "citations": [c.to_citation() for c in chunks],
        "model": "retrieval-only",
        "has_context": bool(chunks),
        "lang": response_lang,
    }
