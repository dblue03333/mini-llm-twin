import logging
from typing import Optional
import pymongo
from pymongo import MongoClient, collection
from src.config import MONGODB_URI, MONGODB_DB, MONGODB_CHUNKS_COLLECTION, BATCH_SIZE
from src.utils.mongodb import get_mongo_database, get_mongo_collection
import time
# Orchestration steps:
# 1. Connect to Mongo chunks_collection
# 2. Get un-embedded chunks (stale or missing `embedding`)
# 3. Batch chunks into groups
# 4. Use EmbeddingModelSingleton to embed each batch
# 5. Update MongoDB with embeddings
# 6. Counters & Logging

db = get_mongo_database(MONGODB_URI, MONGODB_DB)
chunk_collection = get_mongo_collection(db, MONGODB_CHUNKS_COLLECTION)

def get_stale_chunks(collection: collection, limit: Optional[int] = None) -> list[dict]:
    """
        Input: collection, limit
        Output: list of cursor
        Goal: Retrieve chunks that need new embeddings.
        Notes: flt -> get cursor of collection by flt -> return list of cursor
    """
    flt = {'embedding': {"$exists":False}}
    cursor = collection.find(flt)
    if limit:
        cursor = cursor.limit(limit)
    return list(cursor)

def batch_chunks(chunks: list[dict], batch_size: int):
    """
        Input: chunks (list of dicts), batch_size (int)
        Output: Iterator yielding lists of dicts
        Goal: Divide a large list of chunks into smaller sub-lists (batches) for API limits.
        Notes: Iterate over chunks list with step size `batch_size` -> yield the sliced sub-list
    """
    for i in range(0, len(chunks), batch_size):
        yield chunks[i:i + batch_size]

if __name__ == '__main__':
    db = get_mongo_database(MONGODB_URI, MONGODB_DB)
    chunk_collection = get_mongo_collection(db, MONGODB_CHUNKS_COLLECTION)
    processed_docs = 0
    chunks_inserted = 0
    chunks_updated = 0
    chunks_skipped = 0
    chunks_failed = 0
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    log = logging.getLogger(__name__)
    start_time = time.time()  # Bắt đầu đo thời gian
    log.info("--- [START] Embedding Pipeline ---")
    log.info(f"Database: {MONGODB_DB} | Collection: {MONGODB_CHUNKS_COLLECTION}")

    # Add orchestration logic here later

    duration = time.time() - start_time
    log.info("--- [COMPLETE] Embedding Pipeline ---")
    log.info(f"Duration: {duration:.2f}s")
    log.info(f"Chunks Processed: {processed_docs}")
    log.info(f"Embeddings Summary:")
    log.info(f"  - Created/Updated: {chunks_inserted}")
    log.info(f"  - Skipped (Already exists): {chunks_skipped}")
    log.info(f"  - Failed: {chunks_failed}")
    log.info("-----------------------------------")
