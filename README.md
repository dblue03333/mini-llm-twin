# mini-llm-twin

Learning + portfolio repo: a small "LLM Twin" pipeline in Python.

Current focus: data engineering first (crawl/sync sources -> Bronze/Silver), then load into storage (MongoDB), then build RAG features on top.

## What Works Today

Notion ingestion (Bronze -> Silver -> State) in `scripts/ingest_notes.py`:
- Queries a Notion database (pagination supported)
- Fetches each page's blocks
- Writes:
  - Bronze: `data/bronze/notion_raw.jsonl` (raw-ish text + metadata)
  - Silver: `data/silver/documents.jsonl` (normalized text + stable schema)
  - State: `data/state/notion_state.json` (incremental sync using `last_edited_time`)

## Quick Start

1) Create and activate a venv

PowerShell:
```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

CMD:
```bash
py -m venv .venv
.\.venv\Scripts\activate.bat
```

2) Install dependencies
```bash
py -m pip install -U pip
pip install -r requirements.txt
```

3) Configure environment variables
- Create `.env` (do not commit it). See `.env.example`.

4) Run Notion ingestion
```bash
python scripts/ingest_notes.py
python scripts/ingest_notes.py --page-size 2 --max-pages 1
python scripts/ingest_notes.py --force
```

## Outputs

Bronze (`data/bronze/notion_raw.jsonl`):
- `id`, `created_time`, `last_edited_time`, `title`, `text`

Silver (`data/silver/documents.jsonl`):
- `id`, `type`, `text`, `created_at`, `updated_at`, `metadata`

State (`data/state/notion_state.json`):
- `pages_last_edited` map and `last_sync`

## Project Structure (high level)

```text
mini-llm-twin/
  app/                  # FastAPI entrypoints (later)
  scripts/              # runnable scripts (ingestion lives here)
  src/                  # pipeline modules (data/feature/rag)
  data/                 # local outputs (bronze/silver/state)
```

## Roadmap

- Add block pagination for long Notion pages (`blocks/{page_id}/children` can be paginated)
- Add more sources (GitHub, LinkedIn) behind a shared connector pattern
- Load Silver into MongoDB
- Build chunking + embeddings + retrieval (RAG)
