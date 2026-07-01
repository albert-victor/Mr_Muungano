"""Mr. Muungano — configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemini-2.5-flash"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    chroma_dir: Path = ROOT_DIR / "data" / "chroma"
    pdf_dir: Path = ROOT_DIR / "pdf"
    static_dir: Path = ROOT_DIR / "frontend"
    sources_allowlist_path: Path = ROOT_DIR / "data" / "sources" / "allowlist.yaml"
    youth_qa_path: Path = ROOT_DIR / "data" / "youth_qa.json"

    collection_name: str = "muungano_knowledge"
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # Chunking: 600–800 tokens, 100 overlap (semantic splitting in chunking.py)
    chunk_min_tokens: int = 600
    chunk_max_tokens: int = 800
    chunk_overlap_tokens: int = 100
    chunk_token_encoding: str = "cl100k_base"

    retrieval_k: int = 5
    context_chunk_max_chars: int = 550
    history_messages: int = 4
    llm_max_tokens: int = 1024

    app_title: str = "Mr. Muungano"
    app_description: str = "Msaidizi wa AI wa Elimu ya Muungano wa Tanganyika na Zanzibar"


settings = Settings()

# Document priority (lower number = higher trust)
DOCUMENT_PRIORITY: dict[str, int] = {
    "constitution": 1,
    "articles_of_union": 1,
    "union_act": 2,
    "government_publication": 3,
    "official_faq": 3,
    "official_speech": 4,
    "academic_paper": 4,
    "verified_gov_social": 5,
    "youth_plain": 2,
    "general_knowledge": 9,
}

DOCUMENT_LABELS: dict[str, str] = {
    "constitution": "Katiba / Constitution",
    "articles_of_union": "Articles of Union (1964)",
    "union_act": "Union of Tanganyika and Zanzibar Act, 1964",
    "constitution_en": "Constitution of the United Republic of Tanzania (English)",
    "constitution_sw": "Katiba ya Jamhuri ya Muungano wa Tanzania (Kiswahili)",
    "government_publication": "Machapisho Rasmi ya Serikali",
    "official_faq": "Maswali ya Kawaida — Tovuti Rasmi",
    "official_speech": "Hotuba Rasmi",
    "academic_paper": "Makala ya Kitaaluma",
    "verified_gov_social": "Mitandao ya Kijamii (Serikali — ya ziada)",
    "youth_plain": "Elimu Rahisi kwa Vijana",
}

SOURCE_KIND_BOOST: dict[str, float] = {
    "youth": 0.85,
    "web": 1.0,
    "pdf": 1.05,
    "academic": 1.1,
}

TONE_SOURCE_KIND: dict[str, list[str]] = {
    "youth": ["youth", "web", "pdf"],
    "simple": ["youth", "web", "pdf"],
    "student": ["youth", "pdf", "web"],
    "official": ["pdf", "web", "academic"],
    "default": ["youth", "pdf", "web"],
}

TONE_RETRIEVAL_K: dict[str, int] = {
    "youth": 4,
    "simple": 4,
    "default": 5,
    "student": 5,
    "official": 6,
}

TONE_MAX_TOKENS: dict[str, int] = {
    "youth": 768,
    "simple": 640,
    "default": 1024,
    "student": 1024,
    "official": 1536,
}


def retrieval_k_for_tone(tone: str) -> int:
    return TONE_RETRIEVAL_K.get(tone, settings.retrieval_k)


def max_tokens_for_tone(tone: str) -> int:
    return min(TONE_MAX_TOKENS.get(tone, settings.llm_max_tokens), settings.llm_max_tokens)
