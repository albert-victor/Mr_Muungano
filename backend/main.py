"""FastAPI application — Mr. Muungano."""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.config import settings
from backend.rag.chat import chat, chat_stream, close_http_client
from backend.rag.ingest import ingest_pdfs
from backend.rag.ingest_web import ingest_web
from backend.rag.ingest_youth import ingest_youth_qa
from backend.rag.prompts import SUGGESTED_QUESTIONS_EN, SUGGESTED_QUESTIONS_SW
from backend.rag.retriever import get_chunk_count, invalidate_retriever_cache, is_retriever_ready, warm_retriever

logger = logging.getLogger("muungano")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pakia embedding model kabla ya kukubali maombi — epuka kusubiri kwa dakika kwenye swali la kwanza
    logger.info("Loading embedding model and knowledge base…")
    chunk_count = await asyncio.to_thread(warm_retriever)
    logger.info("Retriever ready (%s chunks).", chunk_count)
    yield
    await close_http_client()


app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)
    tone: str = Field(default="youth")
    lang: str = Field(default="sw")
    stream: bool = Field(default=True)


class IngestRequest(BaseModel):
    reset: bool = False


class WebIngestRequest(BaseModel):
    urls: list[str] = Field(default_factory=list)
    crawl_all: bool = False


@app.get("/api/health")
async def health():
    chunk_count = get_chunk_count()
    return {
        "status": "ok",
        "app": settings.app_title,
        "knowledge_ready": chunk_count > 0,
        "retriever_ready": is_retriever_ready(),
        "chunk_count": chunk_count,
        "model": settings.openrouter_model,
        "has_api_key": bool(settings.openrouter_api_key),
    }


@app.get("/api/suggestions")
async def suggestions(lang: str = "sw"):
    if lang.lower().startswith("en"):
        return {"questions": SUGGESTED_QUESTIONS_EN, "lang": "en"}
    return {"questions": SUGGESTED_QUESTIONS_SW, "lang": "sw"}


@app.post("/api/chat")
async def chat_endpoint(body: ChatRequest):
    if body.stream:
        return StreamingResponse(
            chat_stream(
                body.message,
                [m.model_dump() for m in body.history],
                body.tone,
                body.lang,
            ),
            media_type="application/x-ndjson",
        )

    try:
        result = await chat(
            body.message,
            [m.model_dump() for m in body.history],
            body.tone,
            body.lang,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/ingest")
async def ingest_endpoint(body: IngestRequest):
    try:
        result = ingest_pdfs(reset=body.reset)
        invalidate_retriever_cache()
        await asyncio.to_thread(warm_retriever)
        return {"status": "success", **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/ingest/youth")
async def ingest_youth_endpoint():
    try:
        result = ingest_youth_qa()
        invalidate_retriever_cache()
        await asyncio.to_thread(warm_retriever)
        return {"status": "success", **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/ingest/web")
async def ingest_web_endpoint(body: WebIngestRequest):
    try:
        result = ingest_web(urls=body.urls or None, crawl_all=body.crawl_all)
        invalidate_retriever_cache()
        await asyncio.to_thread(warm_retriever)
        return {"status": "success", **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/ingest/all")
async def ingest_all_endpoint(body: IngestRequest):
    try:
        pdf_result = ingest_pdfs(reset=body.reset)
        youth_result = ingest_youth_qa()
        web_result = ingest_web(crawl_all=True)
        invalidate_retriever_cache()
        await asyncio.to_thread(warm_retriever)
        return {
            "status": "success",
            "pdf": pdf_result,
            "youth": youth_result,
            "web": web_result,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# Static frontend
frontend_path = Path(settings.static_dir)
if frontend_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")

    @app.get("/")
    async def index():
        return FileResponse(str(frontend_path / "index.html"))
