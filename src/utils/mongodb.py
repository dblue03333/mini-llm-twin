import sys
import logging

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

from src.config import MONGODB_URI, MONGODB_DB

log = logging.getLogger(__name__)

def get_mongo_database(mongodb_uri: str = MONGODB_URI, mongodb_db: str = MONGODB_DB) -> Database:
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except ConnectionFailure as e:
        log.error(f"Can not return results at {mongodb_uri}. Error: {e}") 
        sys.exit(1)

    return client[mongodb_db]
def get_mongo_collection(database: Database, mongo_collection) -> Collection:
    return database[mongo_collection]