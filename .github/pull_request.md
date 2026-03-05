## Summary

Phase 2 (Embedding Pipeline, in progress): setup embedding provider interface, batching logic, and MongoDB orchestration `build_embeddings.py` to convert chunked text into vector embeddings.

## Problem

- Phase 1 successfully chopped documents into text chunks, but finding relevant information through text-matching is slow and ignores semantic meaning.
- In order to perform Retrieval-Augmented Generation (RAG), the text must be translated into mathematical vector embeddings.
- These embeddings must be generated via an external provider (like Gemini) and stored back into the `chunks` collection for vector search.

## Scope

- In scope:
  - `src/rag/embeddings.py` (Embedding provider interface, rate-limit handling, batching logic)
  - `src/rag/build_embeddings.py` (Mongo orchestration, finding missing/stale embeddings, updating records)
  - Config updates for API keys
  - Local validation of embedding generation
- Out of scope:
  - Phase 3 (Retrieval API implementation)
  - Phase 4 (Answer generation API)
  - Deployment changes

## Changes

In progress:
- [ ] Define embedding provider interface (`embed_texts`)
- [ ] Choose MVP provider default (Gemini) + fallback strategy
- [ ] Add embedding config/envs (`GEMINI_API_KEY`, provider/model names)
- [ ] Create `embeddings.py`
- [ ] Implement chunk selection query (missing/stale embeddings only)
- [ ] Implement batching logic
- [ ] Implement retry/backoff/rate-limit handling
- [ ] Persist embedding fields (`embedding`, `embedding_model`, `embedded_at`, `embedding_dim`)
- [ ] Add embedding consistency checks (`embedding_dim` stable per model)
- [ ] Create `build_embeddings.py`
- [ ] Add logs/counters (`embedded`, `skipped`, `failed`, `batches`)
- [ ] Add rerun skip behavior (unchanged chunks not re-embedded)
- [ ] Add quota-safe failure messages
- [ ] Document embedding provider tradeoff in README

## Validation

Planned validation:

```bash
py src/rag/build_embeddings.py --limit 3
py src/rag/build_embeddings.py
```

## Data/Behavior Impact

- [x] Behavior change (adds Phase 2 RAG embedding matrix + external API calls)
- [x] Data schema change (adds `embedding`, `embedding_model`, and `embedded_at` to chunks collection)

## Risk and Rollback

- Risk level: medium (introduces external API dependency and rate limits)
- Rollback plan: Revert PR and strip embedding fields from `chunks` if necessary.

## Checklist

- [ ] PR is one logical change (Phase 2 RAG embedding pipeline)
- [x] Branch name follows convention (`feat/*`, `fix/*`, `docs/*`, `spike/*`, etc.)
- [ ] Commit message follows project style
- [ ] No secrets added (verify `.env` is ignored)
- [ ] Logs/errors are clear for debugging
