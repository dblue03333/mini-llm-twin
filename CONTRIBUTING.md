# Contributing / Developer Notes

This repo is a learning + portfolio project. The goal is to keep changes small, reproducible, and easy to review.

## Project goals
- Build a small “LLM Twin” service in Python.
- Keep the codebase simple and readable.
- Prefer incremental improvements with clear commits.

---

## Current status (what I'm working on now)
- I am currently building the **Notion crawler** and **normalizing data first**.
- Next, I will likely create an **abstract connector/base class** to orchestrate the flow across multiple sources.

### MongoDB warehouse status (Phase 2)
What exists now:
- MongoDB Silver loader MVP in `src/warehouse/mongodb/load_silver_to_mongodb.py`
- Connect + `ping` check before loading
- Index creation:
  - unique `{metadata.source, id}`
  - query indexes on `metadata.source`, `type`, `updated_at`
- JSONL streaming load from `data/silver/documents.jsonl`
- Idempotent upsert using `{metadata.source, id}` + `updated_at` comparison
- Data quality checks:
  - malformed JSONL line handling (`iter_jsonl`)
  - missing fields / empty text / invalid timestamps
- Run summary logging with counts: `inserted`, `updated`, `skipped`, `failed`

How to run (Windows PowerShell, from repo root):
```bash
py -m src.warehouse.mongodb.load_silver_to_mongodb
```

Phase 2 acceptance checks (MVP):
- First run loads Silver docs into MongoDB
- Rerun on unchanged input is idempotent (no duplicate logical docs)
- Logs show stable summary counts and failures are visible

### MongoDB reliability hardening (Phase 3)
What exists now (hardening in progress):
- `--dry-run` mode in `src/warehouse/mongodb/load_silver_to_mongodb.py`
  - validates and classifies documents without MongoDB writes
  - skips index creation in dry-run mode (read-only behavior)
- `--limit` debug mode for subset processing
- Improved observability:
  - start log includes `run_id`, mode, file path, db/collection, limit
  - end log includes processed count, summary counts, duration
  - failure logs include line/doc context and reason
- Tombstone-ready loader writes active defaults for present docs:
  - `is_deleted=false`, `deleted_at=null`, `deleted_reason=null`

How to run (Phase 3 validation):
```bash
py -m src.warehouse.mongodb.load_silver_to_mongodb --dry-run --limit 3
py -m src.warehouse.mongodb.load_silver_to_mongodb --dry-run
py -m src.warehouse.mongodb.load_silver_to_mongodb
py -m src.warehouse.mongodb.load_silver_to_mongodb
```

Phase 3 smoke-test expectations:
- Dry-run mode reports `would_insert` / `would_update` / `would_skip` / `failed`
- Dry-run does not write to MongoDB
- Normal rerun on unchanged input remains idempotent (mostly `skipped`)
- Logs include enough context to retry/debug failures

Future-proofing decisions (documented approach):
- Keep `documents` as the canonical normalized source collection
- Add a separate `chunks` collection for chunked text + chunk metadata
- Store embeddings on `chunks` for MVP (simpler than a separate embeddings collection)
- Each chunk should reference the source document using stable logical identity:
  - `document_ref.source`
  - `document_ref.id`
  - optional `document_mongo_id`

Delete/tombstone strategy (design only, implementation later):
- Use soft deletes/tombstones (do not hard delete immediately)
- Planned fields on `documents`:
  - `is_deleted` (bool)
  - `deleted_at` (UTC ISO string or null)
  - `deleted_reason` (string or null)
- Retrieval should exclude tombstoned docs by default
- Tombstoning should happen during future source reconciliation (compare current source IDs vs stored docs)
- Current loader behavior already supports future tombstoning by explicitly reactivating documents seen in the current source load.

### Notion ingestion status (scripts/ingest_notes.py)
What exists now:
- End-to-end Notion ingestion: DB query (pagination) -> blocks fetch -> Bronze JSONL + Silver JSONL.
- Env config: `NOTION_TOKEN`, `NOTION_DB_ID`, `TITLE_PROPERTY_NAME` (default "Date"), `NOTION_VERSION` (default "2022-06-28").
- Standardized paths and folder creation:
  - `data/bronze/notion_raw.jsonl`
  - `data/silver/documents.jsonl`
  - `data/state/notion_state.json`

Bronze output (raw-ish JSONL):
- Fields: `id` (page_id), `created_time`, `last_edited_time`, `title`, `text` (joined block text).

Silver output (clean schema JSONL):
- Fields: `id`, `type="article"`, `text` (normalized), `created_at`, `updated_at`, `metadata={source="notion", title}`.

State management (incremental runs):
- `data/state/notion_state.json` schema:
  - `pages_last_edited: {page_id: last_edited_time}`
  - `last_sync` (UTC ISO timestamp)
- Skip logic: if state has same `last_edited_time` for `page_id`, skip; otherwise process.
- State is updated only after successful Bronze + Silver writes.
- State saves atomically: write `.tmp` then replace.

Reliability & dev experience:
- CLI args: `--page-size`, `--max-pages` (debug cap), `--force` (ignore state).
- Logging: INFO/ERROR with counts (`fetched`, `processed`, `skipped`, `errors`).
- HTTP helper `request_json()`:
  - timeout + retry/backoff on 429 and 5xx
  - retry on network errors (`requests.RequestException`)
  - fail-fast on 401/403
  - JSON decode errors -> RuntimeError
  - other 4xx -> RuntimeError

How to run:
```bash
python scripts/ingest_notes.py
python scripts/ingest_notes.py --page-size 2 --max-pages 1
python scripts/ingest_notes.py --force
```

Known gaps / next steps (optional):
- Handle block pagination if `blocks/{page_id}/children` returns `has_more=true`.
- Add `--log-level` and log "processed page_id=...".
- Add small unit tests for `normalize_text()` and `block_to_text()`.

---

## Pipeline (project architecture)
High-level flow (end-to-end):

**Data Collection → ETL/Normalization → Data Warehouse (MongoDB) → ML System (FTI: Feature / Training / Inference)**

Notes:
- **Data Collection** means crawling/syncing raw content from different sources.
- **ETL/Normalization** means cleaning + standardizing content into a consistent schema.
- **MongoDB** acts as the central store for standardized raw documents in this project.
- **FTI** represents the core ML system structure: build features → (optional) train → run inference (RAG).

---

## Content types (project convention)
We standardize content into 3 main content types, independent of URL/platform:

- **article**: long-form knowledge and notes  
  - Sources: **Notion**, **Obsidian**
- **code**: repositories, code snippets, technical docs  
  - Sources: **GitHub**
- **post**: short-form updates / social posts  
  - Sources: **LinkedIn**

Rule:
- Downstream processing (RAG, chunking, retrieval, prompting) should depend on **`type`**, not the `source` platform.

---

## Repo conventions
- API endpoints live in the `app/` folder.
- Core logic lives in the `src/` folder.
- Scripts live in the `scripts/` folder.
- Tests live in the `tests/` folder.
- Keep changes minimal (one feature/bugfix per commit).

## Branch naming (professional rule)

Use short, descriptive branch names with a prefix:

- `feat/*`: new feature work intended to merge
- `fix/*`: bug fixes
- `docs/*`: documentation-only changes
- `refactor/*`: code restructuring without behavior change
- `test/*`: test-only work
- `chore/*`: tooling/dependency/maintenance work
- `spike/*`: short-lived experiments/prototypes (may be discarded)

Examples:

- `spike/rag-intern`
- `feat/notion-block-pagination`
- `fix/mongodb-upsert-filter`

---

## Quick start (macOS)
1) Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
2) Upgrade pip and install dependencies:
```bash
python -m pip install -U pip
pip install -r requirements.txt
```
3) Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```
4) Open in browser:
http://127.0.0.1:8000/health

## Quick start (Windows PowerShell)

1) Create and activate a virtual environment:

```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1

```

2) Upgrade pip and install dependencies:
```bash
py -m pip install -U pip
pip install -r requirements.txt
```

3) Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

4) Open in your browser:
http://127.0.0.1:8000/health

## Commit style (professional rule)

### Commit messages should be:
Atomic: one logical change per commit (avoid mixing unrelated changes)
Scoped: include a clear prefix to show area
Actionable: start with a verb (present tense)
Green: code should run and tests should pass (when applicable)

## Prefixes

ingest: ingestion/crawling/ETL/normalization
feat: new user-visible feature or capability
fix: bug fix
refactor: restructure only (no behavior change)
test: add or update tests
docs: documentation only
chore: tooling, dependencies, formatting

### Examples

ingest: crawl Notion pages and dump raw JSON
ingest: normalize Notion pages to article JSONL
refactor: extract Notion client into src/connectors
fix: handle Notion pagination cursor
test: add unit tests for normalize_text
docs: update pipeline and content type conventions

### When to commit (rule of thumb)
Commit after each meaningful milestone, such as:

a working function + basic test
a script that runs end-to-end for one source
a refactor that keeps behavior the same but improves structure

Avoid committing:

broken code (unless it’s a clearly marked WIP branch)
large unrelated changes in one commit

### Configuration & secrets
Do not commit secrets (API keys/tokens).
Use a local .env file for secrets.
Ensure .env is included in .gitignore.
If a credential is exposed in logs/screenshots/chat, rotate it immediately.
