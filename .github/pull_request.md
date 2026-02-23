## Summary

Phase 1 (RAG chunking pipeline): create the `chunks` collection from canonical `documents`, add deterministic chunking + idempotent upsert behavior, and document validation commands/results.

## Problem

- DE baseline exists (`Notion -> Silver -> Mongo documents`), but RAG cannot start until retrieval-ready chunks are materialized.
- We need deterministic chunking and idempotent reruns so chunk builds are safe and reproducible.
- Retrieval and answer phases depend on stable chunk provenance fields (document reference + chunk index + metadata).

## Scope

- In scope:
  - `src/rag/chunking.py` (chunking logic + chunk record builder)
  - `scripts/build_chunks.py` (chunk build entrypoint)
  - MongoDB `chunks` collection indexes + idempotent upsert flow
  - `.github/pull_request.md`, `README.md`, `docs/dev-workflow.md` (Phase 1 docs updates)
- Out of scope:
  - Embeddings generation (`build_embeddings`)
  - Retrieval API (`/rag/search`)
  - Answer generation API (`/rag/ask`)
  - Deployment changes

## Changes

- [ ] Chunking foundation (deterministic chunking + overlap)
  - Add char-based chunking for MVP (`chunk_size`, `chunk_overlap`)
  - Build stable chunk records with provenance and content hash
- [ ] Mongo chunk materialization (idempotent reruns)
  - Create `chunks` collection indexes
  - Upsert chunks by stable key and skip unchanged chunks
- [ ] Validation + observability
  - Log processed docs and chunk insert/update/skip/fail counters
  - Document rerun-safe validation commands and observed behavior

## Validation

```bash
py scripts/build_chunks.py --limit 3
py scripts/build_chunks.py
py scripts/build_chunks.py
```

Observed behavior (expected for Phase 1):
- First run inserts chunks for active docs in `documents`.
- Rerun on unchanged data is idempotent (mostly `skipped`, no duplicate logical chunks).
- Logs include chunk build counters and failure reasons with context.

## Data/Behavior Impact

- [ ] No behavior change
- [x] Behavior change (adds Phase 1 RAG chunk materialization + `chunks` collection writes)
- [x] Data schema/output change (new `chunks` collection and chunk metadata/provenance records)

## Risk and Rollback

- Risk level: low
- Rollback plan:
  - Revert this PR to remove chunking pipeline and docs updates.
  - Drop the `chunks` collection if needed (documents collection remains canonical).
  - RAG work can resume later without affecting DE baseline.

## Checklist

- [x] PR is one logical change (Phase 1 RAG chunking pipeline)
- [x] Branch name follows convention (`feat/*`, `fix/*`, `docs/*`, `spike/*`, etc.)
- [x] Commit message follows project style
- [ ] No secrets added (verify before merge)
- [ ] Logs/errors are clear for debugging
