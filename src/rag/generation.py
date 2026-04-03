from typing import List, Dict, Any
import time

from abc import ABC, abstractmethod
from google import genai
from src.config import GEMINI_API_KEY
from pydantic import BaseModel, Field
from typing import List, Optional

from app.api import Citation, RAGResponse

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
        self.model_id = "gemini-flash-lite-latest"  # Speed optimized for RAG

    def generate_response(self, prompt: str) -> str:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # The core inference call
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt
                )
                
                # Safety check: Sometimes models return empty or blocked responses
                if not response.candidates or not response.candidates[0].content.parts:
                    return "The AI was unable to generate a response (it might have been blocked or empty)."

                return response.text
            except Exception as e:
                error_msg = str(e).lower()
                if "timed out" in error_msg or "errno 60" in error_msg:
                    print(f"WARNING: Network Timeout (Attempt {attempt+1}/{max_retries}). Retrying in 2 seconds...")
                    time.sleep(2)
                    if attempt == max_retries - 1:
                        return f"Internal failure in LLM Generation (Gave up after {max_retries} attempts): {str(e)}"
                else:
                    # If it's a different kind of error, return it immediately
                    print(f"ERROR: Gemini LLM Provider failed: {e}")
                    return f"Internal failure in LLM Generation: {str(e)}"


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
    Agentic Prompting: The AI adopts a Persona based on the user's intent.
    """
    instruction = (
        "You are 'Kelvin's AI Twin', an intelligent and friendly assistant acting on behalf of Kelvin Nguyen. "
        "You have two main modes of interaction, and you must seamlessly switch between them based on the user's question:\n\n"
        
        "MODE 1 (Recruiter/Guest interaction): If the user says 'hello', asks 'how are you', or asks about Kelvin's skills, resume, or projects, "
        "be polite, welcoming, and represent Kelvin professionally. "
        "Use the provided context to answer questions about his work. "
        "If they ask 'How are you?', you can say 'I am doing great! I am Kelvin's AI Twin. What would you like to know about his projects?'\n\n"
        "MODE 2 (Learning Assistant): If the user (Kelvin) is asking complex technical questions, asking for summaries, or discussing learning topics, "
        "act as a strict, knowledgeable coding mentor. "
        "Use ONLY the provided context to answer. If the context does not contain the answer, say 'My notes don't cover this, let's learn it together.'\n\n"
        
        "CRITICAL RULES:\n"
        "- Do NOT hallucinate facts about Kelvin's life that are not in the context.\n"
        "- If the retrieved context is completely unrelated to the user's question (e.g., they ask 'How are you?' and the context is about Docker), IGNORE the context and just answer conversatonally."
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
) -> RAGResponse:
    """
    The end-to-end RAG Orchestrator.
    Ties together Retrieval, Context Mapping, Templating, and Generation.
    """

    try:
        start_retrieval = time.time()
        chunks = retrieval_func(query)
        retrieval_time_ms = (time.time() - start_retrieval) * 1000

        citations = [
            Citation(
                source_id=chunk.get("chunk_id", "unknown"),
                text_snippet=chunk.get("text", "")[:200] + "...", # Small preview
                score=chunk.get("score", 0.0), 
                metadata=chunk.get("metadata", {})
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
    except Exception as e:
        print(f"CRITICAL PIPELINE FAILURE: {e}")
        # Return a safe error response so the API doesn't 500
        return RAGResponse(
            answer=f"I encountered a technical error while processing your request: {str(e)}",
            citations=[],
            retrieval_time_ms=0,
            llm_time_ms=0
        )

