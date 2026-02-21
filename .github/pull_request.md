## Summary

MongoDB warehouse MVP

## Problem

The final part of DE, implementing MongoDB as a warehouse before loading into RAG architeture.

## Scope

- In scope:.env.example (MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION)
- Out of scope: RAG, Web UI, Deploy, Extra DE refactors unrelated to Mongo loader

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
- [ ]  Handle data quality and edge cases.
    - Missing fields, empty text, invalid timestamps, duplicates in JSONL, very large docs.
- [ ]  Mongo loader MVP

## Validation

List exact commands or steps you ran.

```bash
# example
python scripts/ingest_notes.py --page-size 2 --max-pages 1
```

## Data/Behavior Impact

- [ ] No behavior change
- [ ] Behavior change (describe)
- [ ] Data schema/output change (describe)

## Risk and Rollback

- Risk level: low / medium / high
- Rollback plan:

## Checklist

- [ ] PR is one logical change
- [ ] Branch name follows convention (`feat/*`, `fix/*`, `docs/*`, etc.)
- [ ] Commit message follows project style
- [ ] No secrets added
- [ ] Logs/errors are clear for debugging
