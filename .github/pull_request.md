<!--
  ╔══════════════════════════════════════════════════════════╗
  ║  LEVEL HISTORY                                           ║
  ║  ✅ Intern  — DE → RAG → Deploy (Ngrok HomeLab, done)   ║
  ║  🔄 Junior  — Phase 1: Multi-Source Data Engineering     ║
  ╚══════════════════════════════════════════════════════════╝
-->

## Summary — Junior Level · Phase 1: Multi-Source Data Engineering

This PR introduces the **Multi-Source Ingestion Architecture** — a scalable, object-oriented ETL pipeline that funnels data from Notion, Obsidian, and GitHub into a unified Silver layer following the Medallion Architecture.

> **Why this matters for the AI Twin:** The Intern version was single-source (Notion only). This phase upgrades the knowledge base to multi-source, giving the twin a richer, more complete context about its owner across all three primary knowledge surfaces.

---

## Problem

The current `scripts/ingest_notes.py` is a top-level procedural script. It cannot be instantiated, reused, or extended without code duplication. Adding Obsidian or GitHub ingestion would require copy-pasting the entire script, breaking the DRY principle and making the Silver layer impossible to unify programmatically.

---

## Scope

**In scope:**
- `BaseIngestor` abstract class (`fetch_raw`, `normalize`, `export_silver`)
- `NotionIngestor` refactored from `ingest_notes.py`
- `ObsidianIngestor` using `pathlib` for local `.md` files
- `GitHubIngestor` using GitHub REST API for READMEs and docs
- `scripts/ingest_all.py` orchestrator
- `SilverRecord` Pydantic schema shared across all ingestors

**Out of scope:**
- RAG chunking or embedding changes
- MongoDB loader changes
- Frontend or API changes

---

## Key Deliverables

### 1. Ingestion Architecture (`src/warehouse/ingestion/`)

- **`BaseIngestor` (ABC):** Enforces `fetch_raw()` → `normalize()` → `export_silver()` contract. Prevents silent drift between ingestors.
- **`SilverRecord` (Pydantic):** Single schema for `{id, type, text, created_at, updated_at, metadata}`. Locked before any ingestor is written.
- **Separate Bronze paths:** Each source writes to its own Bronze file (`notion_raw.jsonl`, `obsidian_raw.jsonl`, `github_raw.jsonl`).
- **Shared Silver path:** All sources merge into `data/silver/documents.jsonl` with dedup by `id`.

### 2. NotionIngestor (Refactor)

- All logic from `scripts/ingest_notes.py` migrated into a class.
- State management (`data/state/notion_state.json`) lives inside the ingestor — not at module level.
- `argparse` removed from module level; controlled by `ingest_all.py` only.

### 3. ObsidianIngestor

- Reads local `.md` files via `pathlib.Path.rglob("*.md")`.
- Extracts YAML frontmatter (if present) as metadata.
- State: file `mtime` or content hash to detect changes.

### 4. GitHubIngestor

- Uses GitHub REST API (`/repos/{owner}/{repo}/contents/`) to list repos and pull Markdown files.
- Handles pagination and 429 rate limits with exponential backoff (consistent with existing `request_json` pattern).
- State: file `sha` from GitHub API response (already provided, no extra hashing needed).

### 5. Orchestrator (`scripts/ingest_all.py`)

- Loops through `[NotionIngestor(), ObsidianIngestor(), GitHubIngestor()]`.
- Each ingestor runs inside a `try/except` — one failure does **not** abort the others.
- Logs per-ingestor summary (`fetched / processed / skipped / errors`) and a final unified total.

---

## Validation Evidence

### Per-Ingestor (run each independently)

```bash
python -m src.warehouse.ingestion.notion_ingestor
python -m src.warehouse.ingestion.obsidian_ingestor
python -m src.warehouse.ingestion.github_ingestor
```

Expected output format:
```
INFO | [NotionIngestor] fetched=12 processed=3 skipped=9 errors=0
```

Rerun on unchanged data:
```
INFO | [NotionIngestor] fetched=12 processed=0 skipped=12 errors=0
```

### Orchestrator

```bash
python scripts/ingest_all.py
python scripts/ingest_all.py  # rerun for idempotency check
```

Expected final log:
```
INFO | [Orchestrator] notion: processed=3 skipped=9 | obsidian: processed=5 skipped=2 | github: processed=8 skipped=0 | total_new=16
```

### Silver Record Spot-Check

Paste 2–3 records from `data/silver/documents.jsonl` to confirm schema compliance:
```json
{"id": "...", "type": "note", "text": "...", "created_at": "...", "updated_at": "...", "metadata": {"source": "notion", "title": "..."}}
```

---

## Data / Behavior Impact

- `data/silver/documents.jsonl` will grow with new records from Obsidian and GitHub.
- Existing Notion records: **unchanged** (same IDs, same logic, just refactored).
- MongoDB Silver collection: **not touched in this PR** — loader is a separate step.
- RAG chunker: **no impact** — Silver schema is backward-compatible.

---

## Risk & Rollback

| Risk | Mitigation |
|------|-----------|
| GitHub API rate limit (60 req/hr unauthenticated) | Use `GITHUB_TOKEN` env var; exponential backoff already in `request_json` |
| Obsidian vault path not configured | Read from `.env` / config; fail fast with clear error message |
| Silver file corruption on concurrent writes | Single-process orchestrator; sequential not parallel |
| Schema drift between ingestors | `SilverRecord` Pydantic model enforces at `normalize()` return |

**Rollback:** Delete new Bronze files and the new entries in `data/silver/documents.jsonl`. Rerun `scripts/ingest_notes.py` (the old script, kept until this PR is fully verified).

---

## Tasks Completed

- [ ] Define `SilverRecord` Pydantic schema
- [ ] Implement `BaseIngestor` abstract class
- [ ] Refactor `NotionIngestor` from `ingest_notes.py`
- [ ] Implement `ObsidianIngestor`
- [ ] Implement `GitHubIngestor`
- [ ] Build `scripts/ingest_all.py` orchestrator
- [ ] Validate each ingestor independently (first run + rerun)
- [ ] Validate orchestrator (full run + rerun)
- [ ] Update `docs/dev-workflow.md`

---

## Checklist

- [ ] PR is one logical change (Multi-Source Ingestion Architecture)
- [ ] Branch follows convention (`feat/base-ingestor-scaffold` → merge → next branch)
- [ ] No global-level `argparse` in ingestor modules
- [ ] Each ingestor has its own state file
- [ ] `SilverRecord` schema is defined and used by all ingestors
- [ ] Rerun idempotency verified for all 3 sources
- [ ] PR evidence includes counter logs and spot-checked Silver records

---

<details>
<summary>📦 Intern Level — Completed Milestone (click to expand)</summary>

**Phase 6 — Deployment & Portfolio Integration**

Transitioned from local dev to Live Production:
- **Medallion Architecture:** Bronze/Silver layers for Notion ingestion
- **SHA-256 Hashing:** Content-based dedup
- **MongoDB Atlas Vector Search:** HNSW indexing with metadata pre-filtering
- **Singleton + Strategy Patterns** for LLM/Embedding providers
- **Exponential Backoff** for TCP timeouts and 429s
- **Docker + Ngrok Static Domain:** HomeLab deployment on Mac Mini
- **Portfolio Integration:** `chat.js` wired to live Ngrok endpoint

All 10 evaluation questions passed. Zero-downtime deployment. ✅

</details>
