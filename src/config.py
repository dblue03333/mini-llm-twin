from dotenv import load_dotenv
from pathlib import Path
import sys
import os
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT/'data'
SILVER_PATH = DATA_DIR / 'silver' / 'documents.jsonl'
# SILVER_PATH.parent.mkdir(parents=True, exist_ok=True)
# print("SILVER_PATH =", PROJECT_ROOT)
# print("EXISTS =", SILVER_PATH.exists())

def require_env(name: str) ->str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing {name} in .env")
    return value
MONGODB_URI= require_env('MONGODB_URI')
if not MONGODB_URI:
    print("Missing MONGODB_URI in .env")
    sys.exit(1)
MONGODB_DB= require_env('MONGODB_DB')
if not MONGODB_DB:
    print("Missing MONGODB_DB in .env")
    sys.exit(1)
MONGODB_COLLECTION= require_env('MONGODB_COLLECTION')
if not MONGODB_COLLECTION:
    print("Missing MONGODB_COLLECTION in .env")
    sys.exit(1)
MONGODB_CHUNKS_COLLECTION= require_env('MONGODB_CHUNKS_COLLECTION')
if not MONGODB_CHUNKS_COLLECTION:
    print("Missing MONGODB_CHUNKS_COLLECTION in .env")
    sys.exit(1)

assert MONGODB_DB is not None
assert MONGODB_COLLECTION is not None

CHUNK_SIZE_CHARS = int(require_env('CHUNK_SIZE_CHARS'))
CHUNK_OVERLAP_CHARS = int(require_env('CHUNK_OVERLAP_CHARS'))