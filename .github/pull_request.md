## Summary

Phase 2 (MongoDB warehouse MVP): implement a Silver-to-Mongo loader with idempotent upsert, indexes, validation, and run logging.

## Problem

- Silver data exists in documents.jsonl but is not loaded into a warehouse yet.

- Need a repeatable Mongo load step for intern-ready end-to-end pipeline.

- Need idempotent reruns to avoid duplicate logical documents.

## Scope

- In scope:
    - load_silver_to_mongodb.py
    - io.py (iter_jsonl malformed JSON handling)
    - config.py
    - pyproject.toml
    - .env.example (Mongo env vars)
    - requirements.txt (if updated)
    - README.md / dev-workflow.md (if you include docs in this PR)
- Out of scope: 
    - Notion block pagination / ingest hardening
    - RAG retrieval/chunking
    - Deployment
    - Tombstones/delete sync strategy

## Changes

- [x]  Configuration and secrets.
    - MONGODB_URI, database name, collection name in .env / .env.example.
- [x]  Decide the canonical collection + schema.
    - One collection (e.g. documents) with your current Silver fields: id, type, text, created_at, updated_at, metadata.source, metadata.title.
- [x]  Define identity + idempotency rules.
    - What is the unique key (id alone vs {source, id}), and when to update (compare updated_at).
- [x]  Do a small MongoDB slice today:
    - Create a loader that upserts from into Mongo.
    - Add the minimal indexes needing for idempotency and retrieval.
- [x]  Build the loader/upserter.
    - Reads JSONL, validates required fields, upserts, and reports counts.
- [x]  Add indexes.
    - Unique index on the chosen key.
    - Query indexes you’ll actually use soon (at least metadata.source, type, and updated_at).
- [x]  Handle data quality and edge cases.
    - Missing fields, empty text, invalid timestamps, duplicates in JSONL, very large docs.
- [x]  Mongo loader MVP

## Validation

```bash
py -m src.warehouse.mongodb.load_silver_to_mongodb
py -m src.warehouse.mongodb.load_silver_to_mongodb
```

Observed behavior:
- MongoDB connection and `ping` succeeded.
- Index creation is safe on reruns.
- Rerun on unchanged input showed idempotent behavior (example: `inserted=0 updated=0 skipped=29 failed=0`).

## Data/Behavior Impact

- [ ] No behavior change
- [x] Behavior change (adds Phase 2 MongoDB warehouse load step from `data/silver/documents.jsonl`)
- [ ] Data schema/output change (describe)

## Risk and Rollback

- Risk level: low
- Rollback plan:
  - Revert this PR to remove MongoDB loader/config changes.
  - Drop MongoDB collection/indexes created by this phase if test data rollback is needed.
  - No rollback required for Notion Bronze/Silver generation logic.

## Checklist

- [x] PR is one logical change (Phase 2 MongoDB warehouse MVP)
- [x] Branch name follows convention (`feat/*`, `fix/*`, `docs/*`, etc.)
- [x] Commit message follows project style
- [ ] No secrets added (verify before merge)
- [x] Logs/errors are clear for debugging
