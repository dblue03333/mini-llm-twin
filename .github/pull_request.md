## Summary

Phase 3 (Reliability hardening): add dry-run and subset validation to the MongoDB loader, improve observability, and document future-proofing decisions (including delete/tombstone strategy).

## Problem

- Phase 2 MongoDB loading works, but reliability hardening is still needed before moving fully into the next phase.
- We need a safe way to validate loader behavior without writes (`--dry-run`) and a fast debug path (`--limit`).
- Loader runs should produce better operational logs (run metadata, duration, failure context).
- Future RAG and delete handling need a documented storage/tombstone approach to avoid redesign later.

## Scope

- In scope:
  - `src/warehouse/mongodb/load_silver_to_mongodb.py` (Phase 3 reliability hardening)
  - `.github/pull_request.md` (Phase 3 PR draft)
  - `README.md`, `docs/dev-workflow.md`, `CONTRIBUTING.md` (Phase 3 docs updates)
- Out of scope:
  - Full delete/tombstone reconciliation implementation
  - RAG chunking/embeddings implementation
  - API/query endpoint implementation
  - Deployment changes

## Changes

- [x] Minimal tests or at least a “dry run” mode.
  - Added `--dry-run` and `--limit` for safe subset validation and behavior checks.
  - Dry-run skips Mongo writes and index creation, and reports `would_insert` / `would_update` / `would_skip`.
- [x] Basic observability.
  - Added start/end run logs with `run_id`, mode, file, limit, db/collection, duration, and summary counts.
  - Added clearer failure logs with line/doc context and reason.
- [x] Future-proofing (don’t do all today, but decide the approach).
  - Documented `documents` + `chunks` collection strategy and embeddings-on-chunks MVP approach.
  - Documented delete/tombstone strategy (soft delete design) and retrieval exclusion rule.
- [x] Delete/tombstone strategy (optional)
  - Design documented (soft delete / tombstones).
  - Loader updated to write tombstone-ready active defaults for present docs: `is_deleted=false`, `deleted_at=null`, `deleted_reason=null`.

## Validation

```bash
py -m src.warehouse.mongodb.load_silver_to_mongodb --dry-run --limit 3
py -m src.warehouse.mongodb.load_silver_to_mongodb --dry-run
py -m src.warehouse.mongodb.load_silver_to_mongodb
py -m src.warehouse.mongodb.load_silver_to_mongodb
```

Observed behavior (expected for Phase 3):
- Dry-run reports `would_insert/would_update/would_skip/failed` without writes.
- Start/end logs include run metadata and duration.
- Normal rerun on unchanged input remains idempotent (mostly `skipped`, no duplicate logical docs).

## Data/Behavior Impact

- [ ] No behavior change
- [x] Behavior change (adds Phase 3 loader reliability hardening: dry-run/limit, enhanced observability, tombstone-ready active defaults)
- [ ] Data schema/output change (describe)

## Risk and Rollback

- Risk level: low
- Rollback plan:
  - Revert this PR to remove Phase 3 loader hardening and docs changes.
  - Loader will return to Phase 2 behavior.
  - Tombstone fields written in Mongo can remain harmlessly, or be removed in a future migration if needed.

## Checklist

- [x] PR is one logical change (Phase 3 reliability hardening)
- [x] Branch name follows convention (`feat/*`, `fix/*`, `docs/*`, etc.)
- [x] Commit message follows project style
- [ ] No secrets added (verify before merge)
- [x] Logs/errors are clear for debugging
