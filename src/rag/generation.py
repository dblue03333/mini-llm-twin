from typing import List, Dict, Any
from abc import ABC, abstractmethod
from google import genai
from src.config import GEMINI_API_KEY
from pydantic import BaseModel, Field
from typing import List, Optional
class LLMProvider(ABC):
    """
    Interface for any Large Language Model.
    Ensures our RAG system is model-agnostic.
    """
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

class GeminiLLMProvider(LLMProvider):
    """
    Concrete implementation using Google's Gemini API.
    """
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-1.5-flash"  # Speed optimized for RAG

    def generate_response(self, prompt: str) -> str:
        # The core inference call
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text


class Citation(BaseModel):
    """Refers to the specific source used to generate the answer."""
    source_id: str
    text_snippet: str
    score: float

class RAGResponse(BaseModel):
    """The structured output of our Generation pipeline."""
    answer: str
    citations: List[Citation]
    retrieval_time_ms: float
    llm_time_ms: float


def format_chunks_to_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Step 2: Consolidates multiple retrieved chunks into one 'Big Document'.
    Uses clear delimiters (Signals) to separate independent sources.
    """
    if not chunks:
        return "No relevant context found."

    context_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        text = chunk.get("text", "").strip()
        score = chunk.get("score", 0.0)
        
        header = f"--- SOURCE {i} (Similarity: {score:.4f}) ---"
        
        context_parts.append(f"{header}\n{text}")
    
    return "\n\n".join(context_parts)

def create_rag_prompt(query: str, context: str) -> str:
    """
    Step 3: The Prompt Template (Augmentation).
    Combines the user query and the context into a grounded instruction.
    """
    # This is the 'System instruction' within the prompt
    instruction = (
        "You are an AI assistant tasked with answering questions based ONLY "
        "on the provided context. Your goal is to represent the information "
        "accurately and concisely.\n\n"
        "STRICT RULE: If the answer is not contained within the provided context, "
        "simply state that you do not have enough specific information. "
        "Do NOT use your general knowledge to fill in gaps."
    )
    
    # We assemble the final text payload
    prompt = f"""
            {instruction}

            ### CONTEXT:
            {context}

            ---

            ### USER QUESTION:
            {query}

            ### FINAL ANSWER:
            """
    return prompt.strip()



def run_rag_pipeline(
    query: str, 
    retrieval_func, 
    llm: LLMProvider
) -> str:
    """
    The end-to-end RAG Orchestrator.
    Ties together Retrieval, Context Mapping, Templating, and Generation.
    """

    start_retrieval = time.time()
    chunks = retrieval_func(query)
    retrieval_time_ms = (time.time() - start_retrieval) * 1000

    citations = [
        Citation(
            source_id=chunk.get("chunk_id", "unknown"),
            text_snippet=chunk.get("text", "")[:200] + "...", # Small preview
            score=chunk.get("score", 0.0)
        )
        for chunk in chunks
    ]

    context = format_chunks_to_context(chunks)

    full_prompt = create_rag_prompt(query, context)
    
    start_llm = time.time()
    answer = llm.generate_response(full_prompt)
    llm_time = (time.time() - start_llm) * 1000 

    return RAGResponse(
        answer=answer,
        citations=citations,
        retrieval_time_ms=round(retrieval_time_ms, 2),
        llm_time_ms=round(llm_time, 2)
    )

