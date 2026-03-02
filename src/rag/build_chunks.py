#  orchestration:

# connect Mongo
# read documents
# loop over docs
# call build_chunk_records_from_document
# upsert into chunks
# counters/logging

from typing import Optional

from src.config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION, MONGODB_CHUNKS_COLLECTION
from pymongo import MongoClient

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")  

db = client[MONGODB_DB]
documents_collection = db[MONGODB_COLLECTION]
chunks_collection = db[MONGODB_CHUNKS_COLLECTION]

def ensure_chunk_indexes(chunks_collection):
    """
        Goal: Preparing the target collection you will write into, indexes we want:
            - Unique index on chunk_id
            - Index on document_ref.source, document_ref.id
            - index on is_deleted
            - Index on updated_at
        Input:
        Output:
        Note:
    """
    return
def get_active_documents(documents_collection, limit: Optional[int]) -> list[dict]:
    """
        Goal: Getting source data from documents collection on MongoDB which
              are active docs for chunking pipeline.
        Input: 
            - documents_collection: source MongoDB collection handle for canonical documents
            - limit: optional max number of documents to fetch
        Output: list of active normalized document dicts from MongoDB
        Note:
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
    

