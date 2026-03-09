import logging
from typing import List, Dict, Any

from src.rag.embeddings import EmbeddingModelSingleton
from src.utils.mongodb import get_mongo_collection
from src.config import MONGO_CHUNKS_COLLECTION


log = logging.getLogger(__name__)

def retrieve_chunks(query_text: str, top_k: int = 5) -> List(Dict[str, Any]):
    embedding_model = EmbeddingModelSingleton()

    
