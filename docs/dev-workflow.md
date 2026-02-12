# Development Workflow

This project uses a simple production-style workflow: keep `main` stable, ship in small steps, and review changes through pull requests.

## Branch Strategy

- `main` is always deployable.
- Create short-lived branches per task:
  - `feat/<scope>`
  - `fix/<scope>`
  - `refactor/<scope>`
  - `docs/<scope>`
  - `chore/<scope>`
- Example branch names:
  - `feat/notion-block-pagination`
  - `fix/title-property-fallback`
  - `feat/mongo-upsert-loader`

## Ticket To Merge Flow

1. Pick one ticket with a small scope.
2. Create a branch from latest `main`.
3. Implement and test locally.
4. Open a PR to `main` using the PR template.
5. Keep PR small and focused.
6. Squash merge after checks/review pass.
7. Delete the branch.

## Pull Request Rules

- One logical change per PR.
- Include:
  - Problem statement
  - What changed
  - Evidence (logs/tests/screenshots if relevant)
  - Risk and rollback note
- If behavior changes, update docs in the same PR.

## Commit Message Style

Use concise, scoped commit messages:

- `ingest: add Notion block children pagination`
- `fix: handle missing title property in Notion pages`
- `feat: add MongoDB silver upsert loader`
- `docs: add MVP scope and success metrics`

## Quality Gate (Minimum)

Before opening PR:

1. Script runs end-to-end for affected flow.
2. No obvious crash path on missing env/config.
3. Logs show meaningful counts and failures.
4. Documentation updated when behavior changed.

## Release Note

For now, release directly from `main` after merge.
If release complexity increases later, add `release/*` branches then.
