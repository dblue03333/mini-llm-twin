from pydantic import BaseModel, Field
from typing import List, Dict, Any

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The search query text")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")

class SearchResult(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    count: int
