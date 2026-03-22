from fastapi import FastAPI
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.api import SearchRequest, SearchResponse
from src.rag.retrieval import retrieve_chunks
from src.rag.generation import (
    RAGResponse, 
    GeminiLLMProvider, 
    run_rag_pipeline
)


class RAGRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user question")
    top_k: int = Field(default=5, ge=1, le=10, description="Max context chunks to retrieve")

llm_provider = GeminiLLMProvider()

app = FastAPI(title='mini-llm-twin', version='0.1.0')

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/rag/ask', response_model=RAGResponse)
def ask(request: RAGRequest):
    """
    The final 'Voice' of your AI Twin.
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
