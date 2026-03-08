import logging
from typing import Optional
# import pymongo
from pymongo import MongoClient, collection, UpdateOne
from src.config import MONGODB_URI, MONGODB_DB, MONGODB_CHUNKS_COLLECTION, BATCH_SIZE
from src.utils.mongodb import get_mongo_database, get_mongo_collection
from src.rag.embeddings import EmbeddingModelSingleton
import time
import hashlib
from datetime import datetime, timezone
# Orchestration steps:
# 1. Connect to Mongo chunks_collection
# 2. Get stale chunks (missing `embedding` OR `text_hash` mismatch)
# 3. Batch chunks into groups
# 4. Use EmbeddingModelSingleton to embed each batch
# 5. Update MongoDB with embeddings AND current text_hash
# 6. Counters & Logging

db = get_mongo_database(MONGODB_URI, MONGODB_DB)
chunk_collection = get_mongo_collection(db, MONGODB_CHUNKS_COLLECTION)

def get_stale_chunks(collection: collection, limit: Optional[int] = None) -> list[dict]:
    """
    Goal: Retrieve chunks that need new embeddings.
    Logic: Find chunks where 'embedding' is missing OR 'text_hash' doesn't match current 'text'.
    Note: For this MVP, we simplify to finding chunks missing 'embedding'. 
    To support UPDATES: We check if 'embedding' exists. 
    If we want to force re-embedding on text change, we'd compare hashes.
    """
    # Find chunks missing the embedding field
    flt = {'embedding': {"$exists": False}}
    cursor = collection.find(flt)
    if limit:
        cursor = cursor.limit(limit)
    return list(cursor)

def compute_hash(text: str) -> str:
    """Helper to create a fingerprint of the text."""
    return hashlib.md5(text.encode()).hexdigest()

def batch_chunks(chunks: list[dict], batch_size: int):
    """
        Input: chunks (list of dicts), batch_size (int)
        Output: Iterator yielding lists of dicts
        Goal: Divide a large list of chunks into smaller sub-lists (batches) for API limits.
        Notes: Iterate over chunks list with step size `batch_size` -> yield the sliced sub-list
    """
    for i in range(0, len(chunks), batch_size):
        yield chunks[i:i + batch_size]

def update_batch_embeddings(collection: collection, batch: list[dict]) -> None:
    if not batch: 
        return

    operations = [
        UpdateOne(
            {'chunk_id': chunk['chunk_id']},
            {'$set': {
                'embedding': chunk['embedding'],
                'text_hash': compute_hash(chunk['text']), # Store the fingerprint
                'embedding_model': 'models/gemini-embedding-001',
                'embedding_dim': len(chunk['embedding']),
                'embedded_at': datetime.now(timezone.utc)
            }}
        )
        for chunk in batch if 'embedding' in chunk
    ]
    if operations:
        collection.bulk_write(operations)

    

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
    start_time = time.time()
    log.info("--- [START] Embedding Pipeline ---")
    log.info(f"Database: {MONGODB_DB} | Collection: {MONGODB_CHUNKS_COLLECTION}")
    stale_chunks = get_stale_chunks(chunk_collection)
    log.info(f"Found {len(stale_chunks)} chunks to process.")
    embedding_model = EmbeddingModelSingleton()
    for batch in batch_chunks(stale_chunks, BATCH_SIZE):
        #update the counters
        processed_docs += len(batch)
        text_to_embed = [chunk['text'] for chunk in batch]
        # (future step 4 & 5) Call Embedding API & Update Mongo will be here
        # batch_chunks(batch, BATCH_SIZE)s
        embeddings = embedding_model.embed_texts(text_to_embed)
        #after getting embedding text, update by function update of mongo
        chunks_inserted += len(batch) 
        for chunk, vector in zip(batch, embeddings):
            chunk['embedding'] = vector
            
        update_batch_embeddings(chunk_collection, batch)
    
        log.info(f"Processed a batch of {len(batch)} chunks...")
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
