from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.api import SearchRequest, SearchResponse, RAGRequest, RAGResponse
from src.rag.retrieval import retrieve_chunks
from src.rag.generation import (
    RAGResponse, 
    GeminiLLMProvider, 
    run_rag_pipeline
)


llm_provider = GeminiLLMProvider()

app = FastAPI(title='mini-llm-twin', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allowing all for now during testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/rag/ask', response_model=RAGResponse)
def ask(request: RAGRequest):
    """
    The final 'Voice' of AI Twin.
    Executes the full RAG pipeline: Retrieval -> Generation.
    """
    # We pass the query, our search function, and our LLM provider
    response = run_rag_pipeline(
        query=request.query,
        retrieval_func=retrieve_chunks,
        llm=llm_provider
    )
    return response

@app.post('/rag/search', response_model=SearchResponse)
def search(request: SearchRequest):
    results = retrieve_chunks(query_text=request.query, top_k=request.top_k)
    return SearchResponse(
        query=request.query,
        results=results,
        count=len(results)
    )
