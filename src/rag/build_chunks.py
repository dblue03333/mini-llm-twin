#  orchestration:

# connect Mongo
# read documents
# loop over docs
# call build_chunk_records_from_document
# upsert into chunks
# counters/logging

from typing import Optional

from src.config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION, MONGODB_CHUNKS_COLLECTION
from pymongo import MongoClient, Collection

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")  

db = client[MONGODB_DB]
documents_collection = db[MONGODB_COLLECTION]
chunks_collection = db[MONGODB_CHUNKS_COLLECTION]

def upsert_chunk(collection: Collection, chunk: dict):
    flt = {'id': chunk['id']}

    update_doc = {'$set': chunk}

    collection.update_one(flt, update_doc, upsert=True)

def ensure_chunk_indexes(collection: Collection) -> None:
    """
        Goal: Ensure that the necessary indexes are created on the MongoDB chunks collection
                (document_ref.source, document_ref.id, is_deleted, and updated_at)
        Input: 
            - collection: MongoDB collection handle for chunk records
        Output: None
        Note: This function ensures that queries on the chunks collection are optimized by creating indexes.
    """
    collection.create_index([("id", pymongo.ASCENDING)], unique=True)

    collection.create_index([('document_id', pymongo.ASCENDING)])

    collection.create_index([("is_deleted", pymongo.ASCENDING)])

    collection.create_index([("updated_at", pymongo.DECESDING)])




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
    

