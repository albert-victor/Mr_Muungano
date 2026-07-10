# MuunganoAi

**An AI educator for the Union of Tanganyika and Zanzibar**  
*Grounded in official sources — the Constitution, Articles of Union, and government publications.*

---

MuunganoGPT is a RAG (Retrieval-Augmented Generation) system that answers questions about the structure, history, and law of the Tanzanian Union. Responses are drawn from verified documents — not from the model's imagination alone.

Whether you're a young person, a student, or anyone trying to understand why Tanzania has two governments, when the Union was formed, or what *Union Matters* actually means — without wading through hundreds of PDF pages.

---

## Why MuunganoAi?

| Challenge | Solution |
|-----------|----------|
| Constitutions and Union documents are long and dense | Clear answers in language you can follow |
| Online information mixes facts with opinion | Crawler uses an **allowlist** of official sources only |
| Everyone learns differently | Pick a tone: youth, simple, student, or official |
| Swahili and English speakers | Full bilingual UI and responses — switch instantly |

---

## How it works

```
  User question
        │
        ▼
  ┌─────────────┐     ┌──────────────────┐
  │  Retriever  │────▶│  ChromaDB        │
  │  (semantic) │     │  + embeddings    │
  └─────────────┘     └──────────────────┘
        │                      ▲
        │   top 5–6 chunks     │ PDFs · official sites · youth Q&A
        ▼                      │
  ┌─────────────┐     ┌──────────────────┐
  │  OpenRouter │◀────│  Context +       │
  │  (LLM)      │     │  tone prompts    │
  └─────────────┘     └──────────────────┘
        │
        ▼
  Streaming response in Swahili or English
```

**Knowledge sources** are ranked by priority: Constitution and Articles of Union first, then government publications, official FAQs, academic papers, and finally general knowledge (clearly labelled as such).

**Embedding model:** `paraphrase-multilingual-MiniLM-L12-v2` — handles Swahili and English in one pass.

**LLM:** OpenRouter (default: `google/gemini-2.5-flash`) — swap models via `.env` without touching code.

---

## Quick start

### Requirements

- Python 3.10+
- An [OpenRouter](https://openrouter.ai/keys) API key — **required** for AI responses
- (Optional) Hugging Face token — faster embedding model download

### Setup

```bash
# Copy environment file
cp .env.example .env

# Edit .env — add your OPENROUTER_API_KEY
```

```bash
# Install dependencies
pip install -r requirements.txt
```

### Load knowledge (first run)

Place Constitution, Articles of Union, and other PDFs in the `pdf/` folder, then:

```bash
# PDFs + youth Q&A + official website crawl
python scripts/crawl_sources.py --crawl-all
```

Or ingest one source at a time:

```bash
python ingest.py                              # PDFs only
python scripts/crawl_sources.py --youth       # youth Q&A
python scripts/crawl_sources.py --crawl-all   # full allowlist
```

### Run

```bash
python run.py
```

Open **http://127.0.0.1:8000** in your browser.  
*(Do not use `localhost/muunganoGPT` via XAMPP — this server runs directly through Uvicorn.)*

On first launch, the embedding model loads in 5–30 seconds. Wait until the status pill shows *Ready*.

---

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | System status, chunk count, model |
| `GET /api/suggestions?lang=sw` | Suggested starter questions |
| `POST /api/chat` | Chat — `message`, `history`, `tone`, `lang`, `stream` |
| `POST /api/ingest` | Ingest PDFs |
| `POST /api/ingest/youth` | Ingest `data/youth_qa.json` |
| `POST /api/ingest/web` | Crawl URL(s) or full allowlist |
| `POST /api/ingest/all` | Ingest everything |

**Response tones (`tone`):** `youth` · `simple` · `default` · `student` · `official`

---

## Project structure

```
muunganoGPT/
├── backend/
│   ├── main.py              # FastAPI — chat, ingest, static files
│   ├── config.py            # Settings and document priority
│   └── rag/
│       ├── chat.py          # LLM + streaming
│       ├── retriever.py     # Semantic search
│       ├── chroma_store.py  # Vector store
│       ├── crawl.py         # Official website crawler
│       ├── ingest*.py       # PDF, web, youth Q&A
│       └── prompts.py       # MuunganoAi system prompts
├── frontend/                # UI — HTML, CSS, JS (no framework)
├── data/
│   ├── sources/allowlist.yaml   # Approved sources
│   ├── youth_qa.json            # Plain-language youth Q&A
│   └── chroma/                  # Vector store (auto-generated)
├── pdf/                     # Drop source PDFs here
├── scripts/                 # Crawl CLI + nightly scheduler (Windows)
├── run.py                   # Start the server
└── requirements.txt
```

---

## Nightly crawl (Windows)

To refresh knowledge sources automatically each night:

```powershell
.\scripts\schedule_nightly_crawl.ps1
```

This creates a Windows Task Scheduler job that re-ingests sources on a schedule.

---

## Optional configuration

Set in `.env` — see `.env.example` for the full list:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_MODEL` | `google/gemini-2.5-flash` | LLM model |
| `EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | Embedding model |
| `RETRIEVAL_K` | `5` | Chunks passed to the LLM |
| `CHROMA_DIR` | `data/chroma` | Vector store path |
| `PDF_DIR` | `pdf` | PDF source folder |

---

## Trust principles

MuunganoAi is not built to invent facts. Core rules:

- Answers are grounded in context retrieved from approved sources
- Specific dates and facts — never model guesses
- `official` tone includes document references at the end
- Unverified sources (blogs, personal accounts) are **excluded** from the allowlist

---

## Disclaimer

MuunganoAi is an educational tool. It does not represent any government body. For formal legal matters, refer to the original documents on official government websites.

---

<p align="center">
  <strong>MuunganoAi</strong> — understand the Union, in your language, from sources you can trust.
</p>
