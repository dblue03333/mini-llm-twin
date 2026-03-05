import logging
from typing import Optional
import pymongo
from pymongo import collection

# Orchestration steps:
# 1. Connect to Mongo chunks_collection
# 2. Get un-embedded chunks (stale or missing `embedding`)
# 3. Batch chunks into groups
# 4. Use EmbeddingModelSingleton to embed each batch
# 5. Update MongoDB with embeddings
# 6. Counters & Logging

def get_stale_chunks(collection: collection, limit: Optional[int] = None) -> list[dict]:
    """Retrieve chunks that need new embeddings."""
    pass

def batch_chunks(chunks: list[dict], batch_size: int):
    """Yield chunks in chunks of `batch_size`."""
    for i in range(0, len(chunks), batch_size):
        yield chunks[i:i + batch_size]

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    log = logging.getLogger(__name__)

    log.info("Starting embedding pipeline...")
    # TODO: Implement orchestration
    pass
