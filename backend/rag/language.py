"""Detect and enforce response language consistency."""
from __future__ import annotations

import re

_EN_WORDS = frozenset({
    "what", "when", "why", "how", "who", "where", "which", "explain",
    "the", "is", "are", "was", "were", "does", "do", "did", "can", "could",
    "union", "established", "government", "difference", "between", "mainland",
    "zanzibar", "signed", "matters", "simple", "tell", "about", "unite", "united",
    "decide", "decided", "reason", "join", "joining", "they", "their",
    "english", "please", "answer", "reply", "details", "more", "continue",
    "yes", "constitution", "articles", "parliament", "president", "vice",
    "independence", "revolution", "matters", "governments",
})

_SW_MARKERS = (
    " nini", " lini", " kwa nini", " vipi", " wapi", " nani", " gani",
    " eleza", " muungano", " serikali", " tofauti",
    " kwa ", " je ", "ulianzishwa", "ulisaini", "baraza", "katiba",
    "kiswahili", "kiingereza",
)

# Avoid false Swahili hits inside English ("Tanzania", "and", etc.)
_SW_MARKERS_STRICT = (
    " nini", " lini", " kwa nini", " vipi", " wapi", " nani", " gani",
    " eleza", " muungano", " serikali", " tofauti",
    " je ", "ulianzishwa", "ulisaini", "baraza", "katiba",
    "kiswahili", "jibu kwa",
)

_EXPLICIT_EN = re.compile(
    r"(?:\b(in\s+)?english\b|"
    r"\b(?:answer|reply|respond|speak|write|use)\b[^.?!\n]{0,40}\benglish\b|"
    r"kwa\s+kiingereza|"
    r"kiingereza\s+tu)",
    re.I,
)

_EXPLICIT_SW = re.compile(
    r"(?:\b(in\s+)?(?:swahili|kiswahili)\b|"
    r"\b(?:answer|reply|respond|speak|write|use|jibu)\b[^.?!\n]{0,40}\b(?:swahili|kiswahili)\b|"
    r"jibu\s+kwa\s+kiswahili|"
    r"kiswahili\s+tu)",
    re.I,
)


def detect_explicit_language_request(text: str) -> str | None:
    """Detect direct requests like 'answer in English'."""
    if not text or not text.strip():
        return None
    if _EXPLICIT_SW.search(text):
        return "sw"
    if _EXPLICIT_EN.search(text):
        return "en"
    return None


def detect_question_language(text: str) -> str | None:
    """Return 'en', 'sw', or None if ambiguous."""
    if not text or not text.strip():
        return None

    explicit = detect_explicit_language_request(text)
    if explicit:
        return explicit

    lower = f" {text.lower()} "
    words = set(re.findall(r"[a-z']+", lower))

    en_score = len(words & _EN_WORDS)
    for w in _EN_WORDS:
        if f" {w} " in lower:
            en_score += 1

    sw_score = sum(1 for m in _SW_MARKERS_STRICT if m in lower)
    # Common short particles only count when several Swahili cues exist
    if sw_score >= 1:
        sw_score += sum(1 for m in (" ni ", " na ", " ya ", " kwa ") if m in lower)

    if en_score >= 2 and en_score > sw_score:
        return "en"
    if sw_score >= 1 and sw_score > en_score:
        return "sw"
    if en_score >= 1 and sw_score == 0:
        return "en"
    if sw_score >= 1 and en_score == 0:
        return "sw"
    return None


def infer_language_from_history(history: list[dict] | None) -> str | None:
    """Reuse the language of earlier user turns for short follow-ups."""
    if not history:
        return None

    for msg in reversed(history):
        if msg.get("role") != "user":
            continue
        content = msg.get("content", "")
        explicit = detect_explicit_language_request(content)
        if explicit:
            return explicit
        detected = detect_question_language(content)
        if detected:
            return detected
    return None


def resolve_response_language(
    question: str,
    ui_lang: str = "sw",
    history: list[dict] | None = None,
) -> str:
    """UI toggle is the fallback; question text and chat history override when clear."""
    ui = "en" if (ui_lang or "sw").lower().startswith("en") else "sw"

    explicit = detect_explicit_language_request(question)
    if explicit:
        return explicit

    detected = detect_question_language(question)
    if detected:
        return detected

    from_history = infer_language_from_history(history)
    if from_history:
        return from_history

    return ui


LANGUAGE_RULES = {
    "en": (
        "CRITICAL: Reply in English only. Every sentence must be English. "
        "Do not use Swahili words or phrases, even if the source context is in Swahili — translate the facts."
    ),
    "sw": (
        "MUHIMU: Jibu kwa Kiswahili tu. Kila sentensi iwe Kiswahili. "
        "Usichanganye Kiingereza, hata kama vyanzo viko kwa Kiingereza — tafsiri ukweli."
    ),
}

LANGUAGE_REMINDER = {
    "en": "REMINDER: Write your entire answer in English only.",
    "sw": "UKUMBUSHO: Andika jibu lako lote kwa Kiswahili tu.",
}

NO_CONTEXT_HINT = {
    "en": (
        "No specific source chunks matched. Use safe Union facts if relevant "
        "(26 April 1964, one nation two governments). Never mention an empty library."
    ),
    "sw": (
        "Hakuna vipande maalum vilivyopatikana. Tumia maarifa salama ya Muungano ikiwa yanahusika "
        "(26 Aprili 1964, nchi moja serikali mbili). Usiseme maktaba haina taarifa."
    ),
}

FALLBACK_NO_CONTEXT = {
    "en": (
        "The Union of Tanganyika and Zanzibar came together on 26 April 1964 — "
        "one country, but Tanganyika (Mainland) and Zanzibar each kept their own government structures. "
        "What part of that story interests you most?"
    ),
    "sw": (
        "Muungano wa Tanganyika na Zanzibar ulifanyika 26 Aprili 1964 — "
        "nchi moja, lakini Bara na Zanzibar kila moja ilibaki na muundo wake wa serikali. "
        "Sehemu gani ya hii historia ungependa kujua zaidi?"
    ),
}

FALLBACK_CHUNK_YOUTH = {
    "en": "From what I have: {excerpt}…",
    "sw": "Kwa kifupi kutoka vyanzo: {excerpt}…",
}

FALLBACK_CHUNK_FORMAL = {
    "en": "Based on **{title}**{page}:\n\n{excerpt}…",
    "sw": "Kulingana na **{title}**{page}:\n\n{excerpt}…",
}
