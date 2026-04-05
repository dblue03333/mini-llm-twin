# Development Workflow

This repo follows a production-style workflow: stable `main`, short-lived branches, small PRs, and clear rollback paths.

## Branch Strategy

- `main` is always releasable.
- Use short-lived branches by scope:
  - `feat/<scope>`
  - `fix/<scope>`
  - `refactor/<scope>`
  - `docs/<scope>`
  - `chore/<scope>`
  -  `spike/<scope>`
- Example:
  - `feat/mongo-loader-mvp`
  - `feat/notion-ingest-hardening`
  - `fix/title-property-fallback`
  - `spike/rag-intern`
  - `feat/base-ingestor-scaffold` ← Junior Phase 1
  - `feat/notion-ingestor-class`
  - `feat/obsidian-ingestor`
  - `feat/github-ingestor`
  - `feat/ingest-orchestrator`

### Parallel Branches

- Two short-lived branches can exist at the same time if scopes are independent.
- Keep one branch per logical change.
- Merge priority branch first, then sync the other branch from `main`.

## Ticket To Merge Flow

1. `git checkout main`
2. `git pull`
3. `git checkout -b <type/scope>`
4. Implement only one logical change.
5. Validate locally with reproducible commands.
6. Open PR using `.github/pull_request.md`.
7. Squash merge after review/checks.
8. Delete branch after merge.

## Pull Request Rules

- One logical change per PR.
- Required in PR body:
  - Problem
  - Scope (`In scope` / `Out of scope`)
  - Validation evidence (exact commands + observed result)
  - Data/Behavior impact
  - Risk and rollback plan
- If behavior changes, update docs in the same PR.
- For data/warehouse jobs, include idempotency evidence in PR validation (rerun result + count behavior).

## Commit Message Style

- `ingest: add run manifest for ingestion run tracking`
- `fix: make Notion title extraction resilient`
- `feat: add mongodb silver loader scaffold`
- `docs: update mvp scope and workflow`

## Python Execution Rule

This project uses package-style imports (`from src...`), so run modules from repo root:

```bash
py -m src.warehouse.mongodb.load_silver_to_mongodb
```

Why: running file paths directly can fail with `ModuleNotFoundError: No module named 'src'`.

## Secrets and Data Safety

- Never commit `.env`.
- Use `.env.example` for variable names only.
- Treat exposed credentials as compromised and rotate immediately.
- Keep local artifacts in `data/` and do not commit generated JSONL/state files.

## RAG Phase 3 Validation (Retrieval API Pattern)

For the API implementation phase, validate the "Web -> DB" bridge:

1. **Server Test:** `uvicorn app.main:app` (Verify startup logs)
2. **Schema Test:** Visit `/docs` and verify the `SearchRequest` model has `ge=1, le=50` constraints on `top_k`.
3. **End-to-End Test:** `python scripts/smoke_test_retrieval.py`
4. **Resilience Test:** Send a query while MongoDB or Gemini is disconnected (manually simulate via env removal) to confirm the API returns `[]` instead of `500 Internal Server Error`.

PR evidence should show:
- Smoke test output identifying `Status: 200` for multiple queries.
- Latency measurements (averages < 1s for embedding + search).
- Correct semantic relevance (e.g., query about "Notion" returns Notion chunks).

## Quality Gate (Minimum)

Before opening PR:

1. Affected flow runs end-to-end.
2. Logs include meaningful counters and errors.
3. Output files/state are verified for expected changes.
4. Docs/PR notes reflect behavior changes.
5. **API Layer:** New endpoints have Pydantic validation and consistent response schemas.
6. **AI Quality:** Retrieval "makes sense" (relevant chunks are in the top 3).

## Warehouse Job Validation (Phase 2 Pattern)

For MongoDB loader changes, validate with:

1. `py -m src.warehouse.mongodb.load_silver_to_mongodb`
2. Rerun same command on unchanged input
3. Confirm idempotent behavior:
   - no duplicate logical docs (`{metadata.source, id}`)
   - rerun is mostly `skipped`
4. Record summary counts in PR (`inserted/updated/skipped/failed`)

## Warehouse Job Validation (Phase 3 Hardening Pattern)

For reliability-hardening changes (dry-run/observability), include:

1. `py -m src.warehouse.mongodb.load_silver_to_mongodb --dry-run --limit 3`
2. `py -m src.warehouse.mongodb.load_silver_to_mongodb --dry-run`
3. `py -m src.warehouse.mongodb.load_silver_to_mongodb` (normal mode)
4. Rerun normal mode on unchanged input to confirm idempotency

PR evidence should show:
- dry-run `would_insert/would_update/would_skip/failed`
- normal summary `inserted/updated/skipped/failed`
- start/end logs include run metadata (`mode`, `file`, `limit`, `db/collection`, `duration`)

## Future-Proofing Rule (Before RAG Phase)

Before implementing retrieval/RAG, document storage decisions in docs/PR notes:

1. Where chunks will be stored (`chunks` collection)
2. Where embeddings will be stored (on chunks for MVP)
3. How chunk records reference canonical documents
4. How tombstoned/deleted source docs will be excluded from retrieval

## RAG Phase 1 Validation (Chunking Pattern)

For the first RAG implementation phase (chunking), validate with:

1. `py scripts/build_chunks.py --limit 3`
2. `py scripts/build_chunks.py`
3. Rerun `py scripts/build_chunks.py` on unchanged data

PR evidence should show:
- first run inserts chunks into the `chunks` collection
- rerun is idempotent (mostly `skipped`, no duplicate logical chunks)
- logs include chunk build counters (for example: `processed_docs`, `inserted`, `updated`, `skipped`, `failed`)
- chunk records include stable provenance (`document_ref`, `chunk_index`) and are filterable for active docs only

## RAG Phase 2 Validation (Embedding Pattern)

For the second RAG implementation phase (embedding), validate with:

1. `py src/rag/build_embeddings.py`
2. Rerun `py src/rag/build_embeddings.py` on unchanged data

PR evidence should show:
- first run calls Gemini API efficiently in batches, handling rate limits with backoff
- embeddings and hashes are added via `$set` (keeps previous text data intact)
- rerun is idempotent (0 chunks processed if nothing changed since last hash)
- logs include embedding summary (`Created/Updated`, `Skipped`, `Failed`)

---

## Junior Level — Phase 1: Multi-Source Data Engineering

### Architecture Contract (Define Before Coding)

Before implementing any ingestor, the shared Silver Schema **must be locked** as a Pydantic model:

```python
# src/warehouse/ingestion/schemas.py
class SilverRecord(BaseModel):
    id: str
    type: str           # "article", "note", "readme"
    text: str
    created_at: str
    updated_at: str
    metadata: dict      # {source, title, path?, url?}
```

This model is the single source of truth. Each ingestor's `normalize()` must return a `SilverRecord`. If the schema drifts between ingestors, the RAG chunker downstream will break silently.

### Bronze Path Convention

Each source writes to its own Bronze file to keep runs independent:

```
data/bronze/notion_raw.jsonl
data/bronze/obsidian_raw.jsonl
data/bronze/github_raw.jsonl
```

All sources write to the shared Silver file:

```
data/silver/documents.jsonl
```

The Silver file is append-plus-dedup — each ingestor must guard against duplicate `id` entries on re-run.

### Ingestor Validation Pattern

For each new ingestor (`NotionIngestor`, `ObsidianIngestor`, `GitHubIngestor`), validate with:

```bash
# Run one ingestor in isolation first
python -m src.warehouse.ingestion.<source>_ingestor

# Rerun on unchanged data
python -m src.warehouse.ingestion.<source>_ingestor
```

PR evidence must show:
- `fetched / processed / skipped / errors` counters
- Bronze file written with raw format (source-specific fields intact)
- Silver records conform to `SilverRecord` schema (spot-check 2–3 records)
- Rerun is idempotent — `processed=0, skipped=N` on unchanged data

### Orchestrator Validation Pattern (`ingest_all.py`)

For the final orchestration step, validate with:

```bash
# Full run
python scripts/ingest_all.py

# Rerun on unchanged data
python scripts/ingest_all.py
```

PR evidence must show:
- All 3 ingestors complete (including any that encounter 0 new records)
- Per-ingestor counters logged separately (not merged into one number)
- One ingestor failing does **not** stop the others (graceful isolation)
- Final Silver JSONL contains records from all 3 sources
- Rerun is idempotent across all sources

### Quality Gate — Junior Phase 1 (Minimum)

Before opening any Phase 1 PR:

1. `BaseIngestor` is an `ABC` — `fetch_raw()`, `normalize()`, `export_silver()` raise `NotImplementedError` if not overridden.
2. Each ingestor has its own state file (e.g., `data/state/notion_state.json`, `data/state/github_state.json`).
3. State management lives **inside** each ingestor, not in the orchestrator.
4. No global-level `argparse` in ingestor modules (script-level argparse only in `ingest_all.py`).
5. All ingestors produce Silver records with the **same field names and types** as `SilverRecord`.
6. Logs use structured counters consistent with existing patterns (`fetched`, `processed`, `skipped`, `errors`).
