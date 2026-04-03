from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Citation(BaseModel):
    """Refers to the specific source used to generate the answer."""
    source_id: str
    text_snippet: str
    score: float
    metadata: Dict[str, Any] = {}

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

class RAGRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user question")
    top_k: int = Field(default=5, ge=1, le=10, description="Max context chunks to retrieve")

class RAGResponse(BaseModel):
    """The structured output of our Generation pipeline."""
    answer: str
    citations: List[Citation]
    retrieval_time_ms: float
    llm_time_ms: float

