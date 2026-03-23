# 🎥 3-Minute Recruiter Demo Script

## The Goal
When a recruiter or hiring manager says, *"Walk me through a project you're proud of,"* you will use this exact script to show them your **Mini-LLM Twin**.

## ⏱️ Minute 1: The Spark (The UI)
**Action:** Open your Portfolio website, click the Chat widget, and type: _"Explain Dat's Bronze and Silver data layers."_
**Script:**
> "I built an end-to-end RAG AI Twin to answer questions about my skills and projects. Instead of just using a basic Local LLM, I built an enterprise-grade pipeline. Notice how it didn't just guess the answer—it pulled exactly how I build my Notion data pipelines and provided verifiable citations."

## ⏱️ Minute 2: The Engine (The Backend)
**Action:** Open the Swagger UI at `http://127.0.0.1:8000/docs` (or your deployed URL). Show the `/rag/ask` endpoint.
**Script:**
> "The logic runs on a FastAPI backend. I'm taking unstructured Notion data, cleaning it into a Bronze/Silver data warehouse, and chunking it. But the part I'm most proud of is the Idempotency. I built an MD5 hashing system so that if I run the ingestion pipeline 100 times, it only updates the chunks that have actually changed. It saves massive cloud costs."

## ⏱️ Minute 3: The Proof (The Tests)
**Action:** Open `docs/eval_set.md` in GitHub or VSCode. Show them the table of PASS results.
**Script:**
> "To guarantee production quality, I didn't just assume it worked. I built an evaluation suite. I intentionally asked it trick questions, like my social security number, or about tech stacks I don't use. It successfully blocked those and refused to hallucinate. It respects strict grounding boundaries, which is exactly how enterprise AI needs to operate."

---
*Tip: Keep the answers punchy. If they want to look at the code, show them `src/rag/generation.py` to highlight your Object-Oriented `GeminiLLMProvider` or your Exception handling!*
