#  orchestration:

# connect Mongo
# read documents
# loop over docs
# call build_chunk_records_from_document
# upsert into chunks
# counters/logging

import pymongo
import logging

from typing import Optional
from src.config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION, MONGODB_CHUNKS_COLLECTION
from pymongo import MongoClient, collection
from src.rag.chunking import split_text_into_chunks, build_chunk_records_from_document 

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")  

db = client[MONGODB_DB]
documents_collection = db[MONGODB_COLLECTION]
chunks_collection = db[MONGODB_CHUNKS_COLLECTION]

def upsert_chunk(collection: collection, chunk: dict) -> str:
    """
    Goal: Upsert a chunk record into the MongoDB collection using its chunk_id as the unique identifier.
    Input:
        collection: The MongoDB collection to update.
        chunk: The chunk data dictionary to be upserted.
    Output: str indicating the operation performed ('inserted', 'updated', or 'skipped'). 
    Notes: get index to flt -> content -> update
    """
    flt = {'id': chunk['chunk_id']}
    update_doc = {'$set': chunk}
    res = collection.update_one(flt, update_doc, upsert=True)
    
    if res.upserted_id:
        return 'inserted'
    elif res.modified_count > 0:
        return 'updated'
    else:
        return 'skipped'

def ensure_chunk_indexes(collection: collection) -> None:
    """
        Goal: Ensure that the necessary indexes are created on the MongoDB chunks collection
                (document_ref.source, document_ref.id, is_deleted, and updated_at)
        Input: 
            - collection: MongoDB collection handle for chunk records
        Output: None
        Note: This function ensures that queries on the chunks collection are optimized by creating indexes.
    """
    collection.create_index([("id", pymongo.ASCENDING)],unique=True, name = 'uniq_id')
    collection.create_index([('document_ref.source', pymongo.ASCENDING)], name='idx_document_ref_source_id')
    collection.create_index([('document_ref.id', pymongo.ASCENDING)], name='idx_document_ref')
    collection.create_index([("is_deleted", pymongo.ASCENDING)], name='idx_is_deleted')
    collection.create_index([("updated_at", pymongo.DESCENDING)], name='idx_updated_at')

    return
def get_active_documents(documents_collection, limit: Optional[int]) -> list[dict]:
    """
        Goal: Getting source data from documents collection on MongoDB which
              are active docs for chunking pipeline.
        Input: 
            - documents_collection: source MongoDB collection handle for canonical documents
            - limit: optional max number of documents to fetch
        Output: list of active normalized document dicts from MongoDB
        Note: Get document curcor from MongoDB -> adding to documents + checking limit 
    """
    documents_cursor = documents_collection.find({"is_deleted": False})
    documents = []

    i = 0
    for document in documents_cursor:
        documents.append({
                            "id": document.get("id"),
                            "text": document.get("text"),
                            "type": document.get("type"),
                            "metadata": document.get("metadata"),
                            "updated_at": document.get("updated_at"),
                            "is_deleted": document.get("is_deleted"),
                        })
        i += 1
        if limit and i == limit:
            break

    return documents

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    log = logging.getLogger(__name__)

    log.info("Starting chunking pipeline...")
    ensure_chunk_indexes(chunks_collection)
    
    documents_from_collection = get_active_documents(documents_collection, limit=None)
    log.info(f"Found {len(documents_from_collection)} active documents to chunk.")
    
    processed_docs = 0
    chunks_inserted = 0
    chunks_updated = 0
    chunks_skipped = 0
    chunks_failed = 0

    for document in documents_from_collection:
        try:
            chunks = build_chunk_records_from_document(document)
            for chunk in chunks:
                try:
                    status = upsert_chunk(chunks_collection, chunk)
                    if status == 'inserted':
                        chunks_inserted += 1
                    elif status == 'updated':
                        chunks_updated += 1
                    else:
                        chunks_skipped += 1
                except Exception as e:
                    chunks_failed += 1
                    log.error(f"Failed to upsert chunk {chunk.get('chunk_id')}: {e}")
            processed_docs += 1
        except Exception as e:
            log.error(f"Failed to process document {document.get('id')}: {e}")

    log.info(f"Chunking pipeline complete. Docs processed: {processed_docs} | Chunks Inserted: {chunks_inserted} | Updated: {chunks_updated} | Skipped: {chunks_skipped} | Failed: {chunks_failed}")



