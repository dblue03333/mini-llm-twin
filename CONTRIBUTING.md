# Contributing / Developer Notes

This repo is a learning + portfolio project. The goal is to keep changes small, reproducible, and easy to review.

## Project goals
- Build a small “LLM Twin” service in Python.
- Keep the codebase simple and readable.
- Prefer incremental improvements with clear commits.

---

## Current status (what I'm working on now)
- I am currently building the **Notion crawler** and **normalizing data first**.
- Next, I will likely create an **abstract connector/base class** to orchestrate the flow across multiple sources.

---

## Pipeline (project architecture)
High-level flow (end-to-end):

**Data Collection → ETL/Normalization → Data Warehouse (MongoDB) → ML System (FTI: Feature / Training / Inference)**

Notes:
- **Data Collection** means crawling/syncing raw content from different sources.
- **ETL/Normalization** means cleaning + standardizing content into a consistent schema.
- **MongoDB** acts as the central store for standardized raw documents in this project.
- **FTI** represents the core ML system structure: build features → (optional) train → run inference (RAG).

---

## Content types (project convention)
We standardize content into 3 main content types, independent of URL/platform:

- **article**: long-form knowledge and notes  
  - Sources: **Notion**, **Obsidian**
- **code**: repositories, code snippets, technical docs  
  - Sources: **GitHub**
- **post**: short-form updates / social posts  
  - Sources: **LinkedIn**

Rule:
- Downstream processing (RAG, chunking, retrieval, prompting) should depend on **`type`**, not the `source` platform.

---

## Repo conventions
- API endpoints live in the `app/` folder.
- Core logic lives in the `src/` folder.
- Scripts live in the `scripts/` folder.
- Tests live in the `tests/` folder.
- Keep changes minimal (one feature/bugfix per commit).

---

## Quick start (macOS)
1) Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
2) Upgrade pip and install dependencies:
```bash
python -m pip install -U pip
pip install -r requirements.txt
```
3) Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```
4) Open in browser:
http://127.0.0.1:8000/health

## Quick start (Windows PowerShell)

1) Create and activate a virtual environment:

```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1

```

2) Upgrade pip and install dependencies:
```bash
py -m pip install -U pip
pip install -r requirements.txt
```

3) Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

4) Open in your browser:
http://127.0.0.1:8000/health

## Commit style (professional rule)

### Commit messages should be:
Atomic: one logical change per commit (avoid mixing unrelated changes)
Scoped: include a clear prefix to show area
Actionable: start with a verb (present tense)
Green: code should run and tests should pass (when applicable)

## Prefixes

ingest: ingestion/crawling/ETL/normalization
feat: new user-visible feature or capability
fix: bug fix
refactor: restructure only (no behavior change)
test: add or update tests
docs: documentation only
chore: tooling, dependencies, formatting

### Examples

ingest: crawl Notion pages and dump raw JSON
ingest: normalize Notion pages to article JSONL
refactor: extract Notion client into src/connectors
fix: handle Notion pagination cursor
test: add unit tests for normalize_text
docs: update pipeline and content type conventions

### When to commit (rule of thumb)
Commit after each meaningful milestone, such as:

a working function + basic test
a script that runs end-to-end for one source
a refactor that keeps behavior the same but improves structure

Avoid committing:

broken code (unless it’s a clearly marked WIP branch)
large unrelated changes in one commit

### Configuration & secrets
Do not commit secrets (API keys/tokens).
Use a local .env file for secrets.
Ensure .env is included in .gitignore.