from typing import List
from abc import ABC, abstractmethod
from src.config import GEMINI_API_KEY
from google import genai

import time
import logging

class EmbeddingProvider(ABC):
    """
    Abstract interface for generating embeddings from text.
    """
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Takes a list of string chunks and returns a list of float arrays (embeddings).
        """
        pass

# TODO: Implement GeminiEmbeddingProvider (and retry/rate limit logic)

class EmbeddingModelSingleton:
    """
    Singleton wrapper over the chosen embedding provider.
    Ensures we only initialize the API client or model weights once.
    """
    _instance = None
    provider = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmbeddingModelSingleton, cls).__new__(cls)
            # Initialize provider here based on config
            cls._instance.provider = GeminiEmbeddingProvider(api_key=GEMINI_API_KEY)
        return cls._instance

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.provider.embed_texts(texts)

class GeminiEmbeddingProvider(EmbeddingProvider):

    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'models/gemini-embedding-001'

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        
        log = logging.getLogger(__name__)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.embed_content(
                    model=self.model_name, 
                    contents=texts
                )
                return [emb.values for emb in response.embeddings]
            except Exception as e:
                log.warning(f"Embedding API error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    log.error("Max retries reached. Failing.")
                    raise
                time.sleep(2 ** attempt)
        return []