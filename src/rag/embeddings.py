from typing import List
from abc import ABC, abstractmethod

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

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmbeddingModelSingleton, cls).__new__(cls)
            # Initialize provider here based on config
        return cls._instance
