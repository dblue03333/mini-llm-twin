# AITwin / Learning Assistant

Portfolio project: building a small end-to-end LLM Twin system in Python.

Current execution order for internship-ready delivery:
1. Data engineering baseline (`Notion -> Bronze/Silver/State`)
2. MongoDB warehouse MVP (`Silver -> Mongo upsert`)
3. Lightweight retrieval/app layer
4. Deployment

## Current Stage

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

### Done (Phase 2: MongoDB Warehouse MVP)

- MongoDB warehouse loader in `src/warehouse/mongodb/load_silver_to_mongodb.py`:
  - Connects to MongoDB and validates connectivity (`ping`)
  - Creates indexes for idempotency and retrieval:
    - unique `{metadata.source, id}`
    - `metadata.source`, `type`, `updated_at`
  - Loads Silver JSONL (`data/silver/documents.jsonl`) into MongoDB
  - Uses idempotent upsert with `updated_at` comparison
  - Validates required fields and handles malformed JSONL lines
  - Logs `inserted/updated/skipped/failed` summary counts
- Shared helpers in `src/utils/io.py` (including `iter_jsonl`)
- Packaging/config setup for module-based execution (`src/config.py`, `pyproject.toml`)

### In Progress (Phase 3: Reliability Hardening)

- MongoDB loader hardening in `src/warehouse/mongodb/load_silver_to_mongodb.py`:
  - `--dry-run` mode (read/validate/classify without writes)
  - `--limit` for fast subset validation
  - improved observability:
    - start/end logs with mode, file, db/collection, run_id
    - failure logs with line/doc context
    - duration + processed count in summary
  - tombstone-ready write behavior for active source docs (`is_deleted=false`, delete fields cleared)
- Next hardening items:
  - smoke-test procedure documentation
  - future-proofing decisions (chunks/embeddings storage + tombstones)

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

6) Dry-run / subset validation (Phase 3)
```bash
py -m src.warehouse.mongodb.load_silver_to_mongodb --dry-run
py -m src.warehouse.mongodb.load_silver_to_mongodb --dry-run --limit 3
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

1. Build minimal retrieval layer (RAG-lite MVP)
   - chunk documents into a separate `chunks` collection
   - generate embeddings (store on chunks for MVP)
   - retrieve top-k chunks with source attribution
2. Add minimal API endpoint for query/retrieval
3. Add simple demo UI
4. Deploy intern-ready version
