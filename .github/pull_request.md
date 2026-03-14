## Summary

Phase 3 (Retrieval API, completed): Implemented the semantic search layer using FastAPI, Pydantic, and MongoDB Atlas Vector Search. This turns the embedded "memory" from Phase 2 into an accessible web service.

## Problem

- In Phase 2, we successfully embedded chunks into MongoDB, but there was no way for an external system (frontend/mobile) to query them.
- Raw database queries are dangerous and lack validation. We need an "API Contract" that enforces data types and provides a clean interface for search.
- The retrieval must be resilient—handling missing data, large search volumes, and API failures gracefully.

## Scope

- In scope:
  - `app/api.py` (Pydantic request/response schemas, contract enforcement)
  - `app/main.py` (FastAPI initialization and `/rag/search` route)
  - `src/rag/retrieval.py` (The "Search Engine": query embedding + Atlas Vector Search orchestration)
  - Validation: Smoke tests for latency and schema accuracy.
- Out of scope:
  - Phase 4 (LLM Generation and Answer synthesis)
  - Phase 5 (Production deployment/Dockerization)

## Changes

- [x] Create Pydantic schemas in `api.py` (SearchRequest, SearchResponse, SearchResult)
- [x] Implement Input Validation (Min query length, `top_k` bounds 1-50)
- [x] Implement FastAPI `POST /rag/search` route
- [x] Refactor `retrieval.py` with "Fail Fast" logic for empty queries
- [x] Integrate `EmbeddingModelSingleton` for query vectorization
- [x] Orchestrate MongoDB Atlas `$vectorSearch` with score metadata projection
- [x] Add structured error handling (Try/Except) to keep the API alive during provider outages
- [x] Add `scripts/smoke_test_retrieval.py` for automated verification

## Validation

Verified with the following flow:
1. Start server: `uvicorn app.main:app`
2. Run health check: `Invoke-RestMethod -Uri http://127.0.0.1:8000/health`
3. Run smoke test suite: `python scripts/smoke_test_retrieval.py`

Evidence shows:
- Queries are successfully vectorized via Gemini.
- Atlas returns correct chunks based on semantic meaning (not just keywords).
- Invalid inputs (empty strings, large `top_k`) are correctly rejected by Pydantic (422 status).

## Data/Behavior Impact

- [x] New API Layer: The project is now a runnable web service, not just a script pipeline.
- [x] No side-effects on data (Read-only phase).

## Checklist

- [x] PR is one logical change (Phase 3 Retrieval API)
- [x] Branch name follows convention (`feat/rag-retrieval`)
- [x] Code includes docstrings (Google/Custom format)
- [x] Validation results attached to the PR
