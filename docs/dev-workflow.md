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
