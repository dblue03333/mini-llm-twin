## Summary

Run ingest_notes.py end-to-end and the data in file json repeated 4 times, that means I have run it four times.

## Problem

- notion_state.json is the skip gate.
- Bronze/Silver are append-only logs.
- If state exists but Bronze/Silver are lost, pages get skipped and you keep missing data.
- If state is lost but Bronze/Silver exist, pages are reprocessed and duplicated.


## Scope

- In scope:
    - ingest_notes.py
    - data/bronze/*
    - data/silver/*
    - data/state/notion_state.json
- Out of scope: MongoDB, RAG...

## Changes

- [ ]  Add a run manifest/checkpoint file
- [ ]  Make writes transactional-ish per run (temp files then swap).
- [ ]  Move truth to Mongo upserts ({source,id} unique) so reruns are idempotent.
- [ ]  Add integrity check at startup (warn/fail if state/data mismatch).

## Validation



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
