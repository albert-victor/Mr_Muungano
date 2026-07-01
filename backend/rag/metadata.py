"""Classify PDF files and assign metadata."""
from pathlib import Path

from backend.config import DOCUMENT_LABELS, DOCUMENT_PRIORITY
from backend.rag.sources import build_chunk_metadata


def classify_pdf(filename: str) -> tuple[str, str, int, str]:
    """Return (doc_type, title, priority, language)."""
    lower = filename.lower()

    if "articles_of_union" in lower or "articles of union" in lower:
        return "articles_of_union", DOCUMENT_LABELS["articles_of_union"], DOCUMENT_PRIORITY["articles_of_union"], "en"

    if "union_of_tanganyika" in lower or "union of tanganyika" in lower:
        return "union_act", DOCUMENT_LABELS["union_act"], DOCUMENT_PRIORITY["union_act"], "en"

    if "constitution" in lower and "en" in lower:
        return "constitution", DOCUMENT_LABELS["constitution_en"], DOCUMENT_PRIORITY["constitution"], "en"

    if "katiba" in lower or ("cap. 2" in lower and "sw" in lower):
        return "constitution", DOCUMENT_LABELS["constitution_sw"], DOCUMENT_PRIORITY["constitution"], "sw"

    if "muungano_wa_tanganyika" in lower or "muungano wa tanganyika" in lower:
        return (
            "government_publication",
            DOCUMENT_LABELS["government_publication"],
            DOCUMENT_PRIORITY["government_publication"],
            "sw",
        )

    return "government_publication", filename, 4, "mixed"


def pdf_metadata(path: Path, page_number: int = 0, section_title: str = "") -> dict:
    doc_type, title, priority, language = classify_pdf(path.name)
    return build_chunk_metadata(
        document_name=title,
        document_type=doc_type,
        source_url="",
        publication_date="",
        page_number=page_number,
        section_title=section_title,
        language=language,
        government_institution="Government of Tanzania",
        priority_level=priority,
        source_file=path.name,
        source_kind="pdf",
    )
