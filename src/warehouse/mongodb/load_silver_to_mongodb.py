from src.config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION, SILVER_PATH
from pymongo import MongoClient

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")  
# print("MONGODB_DB =", repr(MONGODB_DB))

db = client[MONGODB_DB]
collection = db[MONGODB_COLLECTION]
