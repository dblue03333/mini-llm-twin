#  orchestration:

# connect Mongo
# read documents
# loop over docs
# call build_chunk_records_from_document
# upsert into chunks
# counters/logging

from src.config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION, MONGODB_CHUNKS_COLLECTION
from pymongo import MongoClient

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")  

db = client[MONGODB_DB]
documents_collection = db[MONGODB_COLLECTION]
chunks_collection = db[MONGODB_CHUNKS_COLLECTION]

def ensure_chunk_indexes(chunks_collection):

    

