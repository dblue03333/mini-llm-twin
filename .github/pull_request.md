## Summary

Phase 4 (Generation API, In-Progress): Implementing the LLM-driven "Answer Synthesis" layer. This phase transforms the raw document chunks from Phase 3 into a natural language "AI Twin" response, grounded in the retrieved context.

## Problem

- In Phase 3, we retrieved raw document chunks, but users need a natural language answer, not just a list of search results.
- Without a "Grounding" layer, LLMs are prone to hallucinations (making up answers).
- We need a resilient "Orchestrator" that manages the flow from Retrieval → Context Mapping → Prompt Construction → LLM Generation.

## Progress (Phase 4 Tasks)

- [x] Create `src/rag/generation.py`: The core generation module.
- [x] Context Mapping logic (Step 2 - Serialization): Implemented `format_chunks_to_context` with clear delimiters to help the AI distinguish between multiple sources.
- [x] Prompt Templating logic (Step 3 - Grounding): Created a strict system-instruction template that forces the AI to use only provided context.
- [x] Abstract `LLMProvider` interface: Established a model-agnostic strategy pattern for generation.
- [x] `GeminiLLMProvider` implementation: Integrated Google's Gemini API (flash model) as our primary generation engine.
- [x] `run_rag_pipeline` Orchestrator (Step 4 - The Glue): Implemented the end-to-end data flow using Functional Dependency Injection.

## Remaining for Phase 4 Completion

- [ ] Define Pydantic request/response schemas for the `/rag/ask` endpoint (Answer + Trace).
- [ ] Implement Token/Character limits for the context window (Protecting costs and memory).
- [ ] Structured Citation mapping (Linking bits of the answer back to specific document metadata).
- [ ] Add FastAPI `POST /rag/ask` route to expose the generator to the web.
- [ ] Latency & Error logging for the generation pipeline.

## Validation Plan

- [ ] Write integration test script: `scripts/test_rag_generation.py` to verify grounded responses.
- [ ] Perform "Hallucination Stress Test" (Querying topics NOT in the database to ensure the "I don't know" behavior works).

## Checklist

- [x] Logic is decoupled and testable (Strategy pattern used for LLM).
- [x] Code follows the "Elite Engineering" protocol (Docstrings, type hints).
- [x] Branch name follows convention (`feat/rag-generation`).
- [ ] Validation suite complete (Pending).
