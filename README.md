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

### Done (Phase 1: Chunking Pipeline - Core RAG foundation)

- Chunking logic built (`src/rag/chunking.py`) with configurable overlap and size.
- MongoDB interaction implemented in `src/rag/build_chunks.py`:
  - Enforces `uniq_id` idempotent constraint on individual chunks.
  - Adds optimal read-heavy indexes (`idx_document_ref_id`, `idx_is_deleted`, `idx_updated_at`).
  - Implements safely rerunnable updates via `update_one(upsert=True)`.
  - Orchestration pipeline loop logs correct processed, inserted, and skipped chunks to avoid data duplication.

### Done (Phase 3: Reliability Hardening / DE baseline complete)

- MongoDB loader hardening in `src/warehouse/mongodb/load_silver_to_mongodb.py`:
  - `--dry-run` mode (read/validate/classify without writes)
  - `--limit` for fast subset validation
  - improved observability:
    - start/end logs with mode, file, db/collection, run_id
    - failure logs with line/doc context
    - duration + processed count in summary
  - tombstone-ready write behavior for active source docs (`is_deleted=false`, delete fields cleared)

### DE Baseline Closeout (Pre-Phase 0)

Validation commands (run from repo root):

```bash
py -m src.warehouse.mongodb.load_silver_to_mongodb --dry-run --limit 3
py -m src.warehouse.mongodb.load_silver_to_mongodb --dry-run
py -m src.warehouse.mongodb.load_silver_to_mongodb
py -m src.warehouse.mongodb.load_silver_to_mongodb
```

Expected/recorded behavior for DE closeout:
- Dry-run reports classification counters (`would_insert`, `would_update`, `would_skip`, `failed`) without MongoDB writes.
- Normal mode writes/updates documents in `documents` and logs summary counts.
- Rerun on unchanged input is idempotent (mostly `skipped`, no duplicate logical docs by `{metadata.source, id}`).

### RAG Storage Decisions (MVP)

- `documents` remains the canonical normalized source collection.
- Add a separate `chunks` collection for retrieval-ready chunked text + chunk metadata.
- Store embeddings on `chunks` for MVP (simpler than a separate embeddings collection).
- Retrieval should exclude tombstoned/deleted documents by default.

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

7) Run Chunking Pipeline (Phase 1)
```bash
py src/rag/build_chunks.py
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

1. Phase 1 (RAG): build chunking pipeline (`documents` -> `chunks`) with idempotent reruns
2. Phase 2 (RAG): generate/store embeddings on `chunks`
3. Phase 3-4 (RAG): add `/rag/search` and `/rag/ask` endpoints with citations
4. Phase 5 (RAG): validation, docs, and recruiter demo polish
5. Deploy intern-ready version
