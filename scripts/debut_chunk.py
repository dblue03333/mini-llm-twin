from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

client = MongoClient(os.environ.get("MONGODB_URI"))
db = client["llm_twin"]
collection = db["chunks"]

sample = collection.find_one({"is_deleted": False})
print(f"--- VERIFICATION ---")
print(f"Chunk ID: {sample.get('chunk_id')}")
print(f"Text Length: {len(sample.get('text'))} chars")
print(f"SHA-256 Hash: {sample.get('content_hash')}")
print(f"Ref Doc ID: {sample.get('document_ref', {}).get('id')}")
