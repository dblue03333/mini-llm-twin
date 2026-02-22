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
- Example:
  - `feat/mongo-loader-mvp`
  - `feat/notion-ingest-hardening`
  - `fix/title-property-fallback`

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
6. Open PR using `.github/pull_request_template.md`.
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

## Quality Gate (Minimum)

Before opening PR:

1. Affected flow runs end-to-end.
2. Logs include meaningful counters and errors.
3. Output files/state are verified for expected changes.
4. Docs/PR notes reflect behavior changes.

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
