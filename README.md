# ai-twin-lite

A simplified, educational version of an LLM Twin system inspired by the **LLM Engineers Handbook**.  
This project is designed to be internship-ready, demonstrating my skills in **data engineering**(chapter 3),  
**feature pipelines**(chapter 1 & 4), **vector databases**(chapter 4 & 9), and **RAG (Retrieval-Augmented Generation)**(chapter 9).

---

## 🚀 Overview

`ai-twin-lite` is a small, clean implementation of a modern RAG pipeline:

1. **Data Pipeline**  
   - Crawl or load documents  
   - Clean and normalize text  
   - Convert to structured document format

<!-- 2. **Feature Pipeline**  
   - Chunk documents  
   - Generate embeddings  
   - Store in a vector database (Qdrant)

3. **RAG Inference Pipeline**  
   - Query expansion  
   - Self-querying (metadata extraction)  
   - Vector search  
   - Cross-encoder reranking  
   - Return top relevant chunks for an LLM to answer

4. **Deployment**  
   - FastAPI backend or Gradio UI -->

This repo is intentionally lightweight so I can learn, iterate, and showcase my ML engineering skills.

---

## 📁 Project Structure
<!-- │  ├─ feature_pipeline/
│  │  ├─ chunking.py
│  │  ├─ embeddings.py
│  │  └─ vector_store.py
│  │
│  ├─ rag_pipeline/
│  │  ├─ query_expansion.py
│  │  ├─ self_query.py
│  │  ├─ reranker.py
│  │  └─ rag_pipeline.py
│  │
│  └─ config.py
│
├─ app/
│  ├─ api.py
│  └─ ui.py
│
├─ data/
│  ├─ raw/
│  ├─ clean/
│  └─ embedded/
│
├─ notebooks/ -->
```
ai-twin-lite/
├─ src/
│  ├─ data_pipeline/
│  │  ├─ crawler.py
│  │  ├─ cleaning.py
│  │  └─ models.py
│  │

│
├─ requirements.txt
└─ README.md
```

---

## 🔧 Installation

```bash
git clone https://github.com/dblue03333/ai-twin-lite.git
cd ai-twin-lite
python3 -m venv venv
source venv/bin/activate   # or Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🧱 Pipelines

### **1. Data Pipeline**
Implemented in `src/data_pipeline/`:

- `crawler.py` → simple web/data loader  
- `cleaning.py` → remove noise, normalize text  
- `models.py` → Pydantic `ArticleDocument`

<!-- ### **2. Feature Pipeline**
Implemented in `src/feature_pipeline/`:

- `chunking.py` → split documents into chunks  
- `embeddings.py` → convert chunks into vectors  
- `vector_store.py` → save vectors to Qdrant  

### **3. RAG Pipeline**
Implemented in `src/rag_pipeline/`:

- `query_expansion.py` → generate expanded queries  
- `self_query.py` → extract metadata from query  
- `reranker.py` → cross-encoder ranking  
- `rag_pipeline.py` → full inference flow   -->

---

## ▶️ Running the Feature Pipeline
<!-- 
```bash
python feature_pipeline.py
```

(Or create a dedicated runner later.) -->

---
<!-- 
## ▶️ Running the RAG Inference API

```bash
uvicorn app.api:app --reload
``` -->

---

## 🌐 Deployment Targets

- **Hugging Face Spaces (Gradio UI)**
- **Render (FastAPI app)**
- **Vercel (Serverless Python)**

---

## 📚 Inspired By

This project is based on concepts from the  
**LLM Engineers Handbook – Feature Pipelines, RAG Inference, and Data Engineering chapters**.

---

## 💼 For Your Resume

**Tech Used:**  
Python, Pydantic, SentenceTransformers, Qdrant, FastAPI, Gradio

**Highlights:**  
- Designed and implemented an end‑to‑end RAG system  
- Built modular feature + inference pipelines  
- Deployed a lightweight LLM Twin for real usage  
- Demonstrated ML engineering, data engineering, and LLM application skills  

---

## 🤝 Contributions

This is a learning-focused repo—feel free to extend or build your own version of an AI Twin.

