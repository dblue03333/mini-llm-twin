from fastapi import FastAPI
from typing import List, Dict, Any

from app.api import SearchRequest, SearchResponse
from src.rag.retrieval import retrieve_chunks

app = FastAPI(title='mini-llm-twin', version='0.1.0')

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/rag/search', response_model=SearchResponse)
def search(request: SearchRequest):
    results = retrieve_chunks(query_text=request.query, top_k=request.top_k)
    return SearchResponse(
        query=request.query,
        results=results,
        count=len(results)
    )
