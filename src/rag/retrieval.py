import logging
from typing import List, Dict, Any

from src.rag.embeddings import EmbeddingModelSingleton
from src.utils.mongodb import get_mongo_collection, get_mongo_database
from src.config import MONGODB_CHUNKS_COLLECTION


log = logging.getLogger(__name__)

def retrieve_chunks(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    if not query_text or query_text.strip() == '':
        return []
    if top_k <= 0:
        return []
    try:
        embedding_model = EmbeddingModelSingleton()
        query_text = [query_text[:7000]]
        embeddings = embedding_model.embed_texts(query_text)

        query_vector = embeddings[0]
        db = get_mongo_database()
        chunk_collection = get_mongo_collection(db, MONGODB_CHUNKS_COLLECTION)
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": query_vector,
                    "path": "embedding",
                    "numCandidates" : 50,
                    "index": "vector_index",
                    "limit": top_k,
                    'filter': {
                        'is_deleted': False
                    }
                }
            },
            {
                "$project": 
                {
                    "_id": 0,
                    "chunk_id": 1,
                    "text": 1,
                    "metadata": 1,
                    "score": 
                    {
                        "$meta": "vectorSearchScore"
                    }
                }
            }
            ]
        results = list(chunk_collection.aggregate(pipeline))
        return results
    except Exception as e:
        log.error(f"Retrieval failed: {e}")
    return []