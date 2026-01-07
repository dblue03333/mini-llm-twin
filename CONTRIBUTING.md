# Contributing / Developer Notes

This repo is a learning + portfolio project. The goal is to keep changes small, reproducible, and easy to review.

## Project goals
- Build a small “LLM Twin” service in Python.
- Keep the codebase simple and readable.
- Prefer incremental improvements with clear commits.

## Quick start (macOS)
1) Create and activate a virtual environment:
python3 -m venv .venv
source .venv/bin/activate

2) Upgrade pip and install dependencies:
python -m pip install -U pip
pip install -r requirements.txt

3) Run the server:
uvicorn app.main:app --reload --port 8000

4) Open in your browser:
http://127.0.0.1:8000/health

## Quick start (Windows PowerShell)
1) Create and activate a virtual environment:
py -m venv .venv
.\.venv\Scripts\Activate.ps1

2) Upgrade pip and install dependencies:
py -m pip install -U pip
pip install -r requirements.txt

3) Run the server:
uvicorn app.main:app --reload --port 8000

4) Open in your browser:
http://127.0.0.1:8000/health

## Running tests
pytest -q

## Repo conventions
- API endpoints live in the app/ folder.
- Core logic lives in the src/ folder.
- Tests live in the tests/ folder.
- Keep changes minimal (one feature/bugfix per commit).

## Commit style
Use short, scoped commit messages:
- ch0: add health endpoint
- ingest: load local docs
- rag: add chunking + retrieval

## Configuration & secrets
- Do not commit secrets (API keys).
- Use a local .env file for secrets.
- Ensure .env is included in .gitignore.
