# RAG Phase 1 - Chunking Schema Notes (Intern MVP)

## Goal

Build a deterministic, idempotent chunking pipeline that reads active documents from MongoDB `documents` and prepares retrieval-ready chunk records for MongoDB `chunks`.

## Scope (Phase 1 only)

In scope:
- Char-based chunking with overlap
- Chunk schema definition
- Chunk record builder (`document` -> chunk records)
- Idempotent upsert strategy design (`chunk_id` + `content_hash`)
- Logging/counters design for `build_chunks.py`

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

- Input source (pipeline): MongoDB `documents` collection
- Only process active docs: `is_deleted = false`
- Skip docs with empty/whitespace `text`
- Deterministic slicing (same input => same chunks)
- Overlap reduces boundary information loss
- `chunk_overlap` must be `< chunk_size`

## Function Output Schemas (Current `chunking.py`)

## 1) `split_text_into_chunks(text, chunk_size, chunk_overlap)`

### Goal
Split one text string into deterministic overlapping chunks.

### Returns
`list[dict]` where each item is a chunk segment:

```python
{
  "chunk_index": 0,
  "char_start": 0,
  "char_end": 800,
  "text": "chunk text here..."
}
```

### Field meaning
- `chunk_index`: position of chunk within one document (`0, 1, 2, ...`)
- `char_start`: start offset in original document text (inclusive)
- `char_end`: end offset in original document text (exclusive)
- `text`: actual chunk text slice (`text[char_start:char_end]`)

### Behavior notes
- Returns `[]` for empty/whitespace text
- Raises `ValueError` for invalid chunk params (`chunk_size <= 0`, `chunk_overlap < 0`, `chunk_overlap >= chunk_size`)
- Does not know anything about MongoDB, hashing, or chunk IDs

## 2) `build_chunk_records_from_document(document)`

### Goal
Convert one normalized document into storage-ready chunk records (for later upsert in `build_chunks.py`).

### Expected input (normalized document)

```python
{
  "id": "abc123",
  "type": "article",
  "text": "full normalized document text...",
  "updated_at": "2026-02-26T10:00:00Z",
  "metadata": {
    "source": "notion",
    "title": "Test Note"
  }
}
```

### Returns
`list[dict]` where each item is a chunk record:

```python
{
  "chunk_id": "notion:abc123:0",
  "document_ref": {"source": "notion", "id": "abc123"},
  "type": "article",
  "chunk_index": 0,
  "char_start": 0,
  "char_end": 800,
  "text": "chunk text here...",
  "content_hash": "<sha256 hex>",
  "metadata": {"source": "notion", "title": "Test Note"},
  "source_updated_at": "2026-02-26T10:00:00Z",
  "updated_at": null,
  "is_deleted": false
}
```

### Field meaning (chunk record)

#### Identity / provenance
- `chunk_id`
  - Stable logical identity for one chunk
  - Format (MVP): `<source>:<document_id>:<chunk_index>`
  - Used later as Mongo upsert key
- `document_ref`
  - Provenance reference back to source document
  - Contains `source` and source document `id`

#### Chunk position / content
- `chunk_index`
  - Order within the source document
- `char_start`, `char_end`
  - Original text offsets for debugging/traceability
- `text`
  - Chunk text (used later for embeddings/retrieval)

#### Idempotency / change detection
- `content_hash`
  - SHA256 hash of chunk `text`
  - Used later to compare existing Mongo chunk content vs new chunk content
  - Rerun behavior target:
    - same `chunk_id` + same `content_hash` => `skip`
    - same `chunk_id` + different `content_hash` => `update`

#### Metadata / retrieval context
- `type`
  - Normalized content type (`article`, `code`, `post`)
- `metadata`
  - Source metadata dict (ex: `source`, `title`)

#### Timestamps / deletion state
- `source_updated_at`
  - Timestamp from source normalized document (`documents.updated_at`)
  - Means source content update time (not chunk write time)
- `updated_at`
  - Placeholder for chunk record write/update timestamp
  - Intended to be set during MongoDB upsert in `build_chunks.py`
- `is_deleted`
  - Tombstone-ready flag for chunk records
  - `False` for active chunks built from active documents

### Validation / guard behavior (current design)
- Raises `ValueError` if:
  - `document` is malformed (or missing required fields once guarded)
  - `document.id` is missing
  - `document.metadata` is not a dict
  - `document.metadata.source` is missing
- Returns `[]` if source text is empty/whitespace (through splitter behavior)

## `chunks` Collection Schema (Phase 1 Draft)

Required fields (MVP):
- `chunk_id` (stable)
- `document_ref.source`
- `document_ref.id`
- `type`
- `chunk_index`
- `char_start`
- `char_end`
- `text`
- `content_hash`
- `metadata`
- `source_updated_at`
- `updated_at` (set during upsert)
- `is_deleted`

Optional later:
- `created_at`
- `embedding`
- `embedding_model`
- `embedded_at`
- `embedding_dim`

## Idempotency Strategy (Phase 1 Draft)

Stable identity:
- `chunk_id = <source>:<doc_id>:<chunk_index>`

Change detection:
- `content_hash = sha256(chunk_text)`

Target rerun behavior in `build_chunks.py`:
- missing `chunk_id` => insert
- existing `chunk_id` + same `content_hash` => skip
- existing `chunk_id` + different `content_hash` => update

Notes:
- `documents` remains canonical source of truth
- `chunks` is a derived/materialized collection

## MongoDB Read/Write Plan (for next file: `build_chunks.py`)

Read from `documents`:
- Filter: `is_deleted = false`
- Required fields: `id`, `text`, `type`, `metadata`, `updated_at`

Write to `chunks`:
- Upsert by `chunk_id`
- Set `updated_at` (chunk write time) during upsert
- Compare `content_hash` for `skip` vs `update`
- Keep counters:
  - `processed_docs`
  - `chunks_inserted`
  - `chunks_updated`
  - `chunks_skipped`
  - `failed`

## Planned Indexes for `chunks` (Draft)

- Unique index on `chunk_id`
- Index on `document_ref.source`, `document_ref.id`
- Index on `is_deleted`
- Index on `updated_at`
- Optional later (retrieval phase): index on `type`

## Function Responsibility Split (Important)

### `src/rag/chunking.py`
- Pure chunking logic
- Chunk record shaping
- No MongoDB writes

### `src/rag/build_chunks.py`
- MongoDB connection + reads
- Index creation
- Upsert chunk records
- Counters/logging
- Rerun-safe behavior

## Validation Plan (Phase 1)

Chunking function checks:
- Empty/whitespace text => `[]`
- Short text => one chunk
- Overlap behavior correct (`stride = chunk_size - chunk_overlap`)
- Invalid params raise `ValueError`

Builder checks:
- Valid document => chunk records with stable `chunk_id` and `content_hash`
- Missing `document.id` => `ValueError`
- Missing `metadata.source` => `ValueError`
- `metadata` not dict => `ValueError`

Pipeline checks (next file):
```bash
py scripts/build_chunks.py --limit 3
py scripts/build_chunks.py
py scripts/build_chunks.py
```

Expected pipeline behavior:
- First run inserts chunks into `chunks`
- Rerun on unchanged data is mostly `skipped`
- No duplicate logical chunks (`chunk_id` unique)
