# mini-llm-twin

Portfolio project: building a small end-to-end LLM Twin system in Python.

Current execution order for internship-ready delivery:
1. Data engineering baseline (`Notion -> Bronze/Silver/State`)
2. MongoDB warehouse MVP (`Silver -> Mongo upsert`)
3. Lightweight retrieval/app layer
4. Deployment

## Current Stage (CV Ready Snapshot)

### Done

- Notion ingestion pipeline in `scripts/ingest_notes.py`:
  - Queries Notion DB with pagination
  - Fetches page blocks
  - Writes Bronze (`data/bronze/notion_raw.jsonl`)
  - Writes Silver (`data/silver/documents.jsonl`)
  - Maintains incremental state (`data/state/notion_state.json`)
- Incremental sync using `page_id + last_edited_time`
- Basic reliability:
  - retry/backoff for 429/5xx
  - auth fail-fast for 401/403
- Development workflow docs and PR template established

### In Progress

- MongoDB warehouse MVP:
  - project config setup in `src/config.py`
  - loader scaffold in `src/warehouse/mongodb/load_silver_to_mongodb.py`
  - packaging setup with `pyproject.toml`

## Quick Start

1) Create and activate a venv

PowerShell:
```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies
```bash
py -m pip install -U pip
pip install -r requirements.txt
```

Optional package-mode install:
```bash
pip install -e .
```

3) Configure environment variables

- Create `.env` from `.env.example`
- Never commit `.env`

4) Run Notion ingestion
```bash
py scripts/ingest_notes.py
py scripts/ingest_notes.py --page-size 2 --max-pages 1
py scripts/ingest_notes.py --force
```

5) Run Mongo loader module (from repo root)
```bash
py -m src.warehouse.mongodb.load_silver_to_mongodb
```

## Data Contracts

Bronze (`data/bronze/notion_raw.jsonl`):
- `id`, `created_time`, `last_edited_time`, `title`, `text`

Silver (`data/silver/documents.jsonl`):
- `id`, `type`, `text`, `created_at`, `updated_at`, `metadata`

State (`data/state/notion_state.json`):
- `pages_last_edited`, `last_sync`

## Project Structure (Current)

```text
mini-llm-twin/
  app/                        # API app layer (next phase)
  scripts/                    # runnable entry scripts
  src/
    config.py                 # shared runtime config
    utils/                    # shared IO helpers
    warehouse/mongodb/        # Mongo loader modules
  data/                       # local bronze/silver/state artifacts
  docs/                       # workflow + architecture notes
```

## Next Milestones

1. Finish Mongo loader MVP:
   - upsert from Silver JSONL
   - unique index on `{metadata.source, id}`
   - query indexes on `metadata.source`, `type`, `updated_at`
2. Add minimal retrieval endpoint
3. Add simple demo UI
4. Deploy intern-ready version
