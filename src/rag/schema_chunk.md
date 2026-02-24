# RAG Phase 1 - Chunking Design Notes (Intern MVP)

## Goal

Build a deterministic, idempotent chunking pipeline that reads active documents from MongoDB `documents` and writes retrieval-ready records to MongoDB `chunks`.

## Scope (Phase 1 only)

In scope:
- Char-based chunking with overlap
- Chunk schema definition
- Idempotent upsert into `chunks`
- Logging counters
- Rerun-safe behavior validation

Out of scope:
- Embeddings
- Retrieval ranking
- `/rag/search` and `/rag/ask`
- Deployment

## MVP Defaults (Draft)

- `CHUNK_SIZE_CHARS = 800`
- `CHUNK_OVERLAP_CHARS = 120`

Why:
- Simple and fast to implement
- Good enough for first retrieval MVP
- Easy to explain and tune later

## Chunking Rules (Draft)

- Input source: MongoDB `documents` collection
- Only process active docs: `is_deleted = false`
- Skip docs with empty/whitespace `text`
- Deterministic slicing (same input => same chunks)
- Overlap is required to reduce boundary information loss

## `chunks` Collection Schema (Draft)

Required fields:
- `chunk_id` (stable)
- `document_ref.source`
- `document_ref.id`
- `chunk_index`
- `text`
- `char_start`
- `char_end`
- `content_hash`
- `type`
- `metadata` (at least source/title if available)
- `is_deleted`
- `created_at`
- `updated_at`

Optional later:
- `embedding`
- `embedding_model`
- `embedded_at`
- `embedding_dim`

## Idempotency Strategy (Draft)

Stable identity:
- `chunk_id = <source>:<doc_id>:<chunk_index>`

Change detection:
- Compute `content_hash` from chunk text
- On rerun:
  - same `chunk_id` + same `content_hash` => `skip`
  - same `chunk_id` + different `content_hash` => `update`
  - missing `chunk_id` => `insert`

Note:
- `documents` remains canonical source of truth
- `chunks` is a derived/materialized collection

## MongoDB Read/Write Plan (Draft)

Read from `documents`:
- Filter: `is_deleted = false`
- Required fields: `id`, `text`, `type`,
