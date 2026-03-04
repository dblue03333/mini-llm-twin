## Summary

Phase 1 (Chunking Pipeline) Complete: implemented deterministic chunk splitting and chunk record builder logic in `src/rag/chunking.py`, designed the schema documentation, and fully built the `build_chunks.py` MongoDB orchestration. The pipeline now successfully reads active documents, chunks them, and idempotently upserts them into the `chunks` collection with proper indexing.

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

- [x] Create `build_chunks.py` entrypoint (Mongo read/write orchestration)
- [x] Create Mongo read function for active documents (`is_deleted=false`)
- [x] Create Mongo upsert function for chunks (idempotent)
- [x] Add indexes for `chunks` collection (`uniq_id`, `idx_document_ref_id`, `idx_is_deleted`, `idx_updated_at`)
- [x] Add logging counters (`processed_docs`, `chunks_inserted`, `updated`, `skipped`, `failed`)
- [x] Add rerun behavior check (no duplicates on unchanged data via `$set` upsert)
- [x] Write chunking run instructions in README/docs

## Validation

```bash
py src/rag/build_chunks.py
```

Observed behavior (today / full pipeline validation):
- Pipeline successfully processes active documents and creates expected chunk records.
- Repeated executions yield identical chunk results with 0 `inserted` and N `skipped` records (idempotency verified).
- Logging correctly displays processing metrics to the console.

## Data/Behavior Impact

- [ ] No behavior change (no MongoDB writes yet; chunking logic + docs foundation only)
- [x] Behavior change (adds Phase 1 RAG chunk materialization + `chunks` collection writes)
- [x] Data schema/output change (documented `chunks` schema and chunk record shape for materialization)

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
- [x] Logs/errors are clear for debugging
