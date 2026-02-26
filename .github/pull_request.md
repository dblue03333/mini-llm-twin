## Summary

Phase 1 (RAG chunking foundation, in progress): implement deterministic chunk splitting and chunk record builder logic in `src/rag/chunking.py`, plus schema/design documentation for the `chunks` collection before MongoDB upsert orchestration.

## Problem

- DE baseline exists (`Notion -> Silver -> Mongo documents`), but RAG cannot start until retrieval-ready chunks are materialized.
- We need deterministic chunking and stable chunk record shaping before adding MongoDB upsert/idempotent rerun logic.
- Retrieval and answer phases depend on stable chunk provenance fields (document reference + chunk index + metadata).

## Scope

- In scope:
  - `src/rag/chunking.py` (chunking logic + chunk record builder)
  - `src/rag/schema_chunk.md` (chunk schema + field meanings + idempotency notes)
  - local/manual validation of splitter and chunk record builder behavior
  - `.github/pull_request.md` (Phase 1 PR draft update)
- Out of scope:
  - `build_chunks.py` MongoDB read/write orchestration
  - MongoDB `chunks` indexes and upsert flow
  - Embeddings generation (`build_embeddings`)
  - Retrieval API (`/rag/search`)
  - Answer generation API (`/rag/ask`)
  - Deployment changes

## Changes

Done today:
- [x] Implement deterministic char-based chunk splitting with overlap in `src/rag/chunking.py`
- [x] Add splitter guards (invalid params) and empty/whitespace text handling
- [x] Add chunk boundary metadata (`chunk_index`, `char_start`, `char_end`)
- [x] Implement chunk record builder (`document -> chunk records`)
- [x] Add stable `chunk_id` shape (`<source>:<doc_id>:<chunk_index>`)
- [x] Add `document_ref` provenance and `content_hash` (SHA256 of chunk text)
- [x] Preserve retrieval-relevant fields (`type`, `metadata`, `source_updated_at`) in chunk records
- [x] Document chunk schemas, field meanings, idempotency logic, and function responsibility split in `src/rag/schema_chunk.md`
- [x] Run local/manual function-level validation via `py src/rag/chunking.py`

In progress:
- [ ] Create `build_chunks.py` entrypoint (Mongo read/write orchestration)
- [ ] Create Mongo read function for active documents (`is_deleted=false`)

Next steps:
- [ ] Create Mongo upsert function for chunks (idempotent)
- [ ] Add indexes for `chunks` collection
- [ ] Add logging counters (`processed_docs`, `chunks_inserted`, `updated`, `skipped`, `failed`)
- [ ] Add rerun behavior check (no duplicates on unchanged data)
- [ ] Write chunking run instructions in README/docs after `build_chunks.py` is implemented

## Validation

```bash
py src/rag/chunking.py
```

Observed behavior (today / local function-level validation):
- `split_text_into_chunks(...)` returns deterministic chunk segments with overlap metadata.
- `build_chunk_records_from_document(...)` returns storage-ready chunk records (including `chunk_id`, `document_ref`, `content_hash`).
- Manual fake-document validation confirms chunk record field shaping before MongoDB upsert phase.

Planned validation (next step, after `build_chunks.py`):

```bash
py scripts/build_chunks.py --limit 3
py scripts/build_chunks.py
py scripts/build_chunks.py
```

## Data/Behavior Impact

- [x] No behavior change (no MongoDB writes yet; chunking logic + docs foundation only)
- [ ] Behavior change (adds Phase 1 RAG chunk materialization + `chunks` collection writes)
- [x] Data schema/output change (documented `chunks` schema and chunk record shape for upcoming materialization)

## Risk and Rollback

- Risk level: low
- Rollback plan:
  - Revert this PR to remove chunking foundation code/docs updates.
  - No MongoDB data rollback required yet (no `chunks` materialization in this scope).
  - RAG work can resume later without affecting DE baseline.

## Checklist

- [x] PR is one logical change (Phase 1 RAG chunking foundation)
- [x] Branch name follows convention (`feat/*`, `fix/*`, `docs/*`, `spike/*`, etc.)
- [x] Commit message follows project style
- [ ] No secrets added (verify before merge)
- [ ] Logs/errors are clear for debugging (pending `build_chunks.py` implementation)
