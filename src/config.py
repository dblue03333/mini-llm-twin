from dotenv import load_dotenv
from pathlib import Path
import sys
import os
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT/'data'
SILVER_PATH = DATA_DIR / 'silver' / 'documents.jsonl'
# SILVER_PATH.parent.mkdir(parents=True, exist_ok=True)

MONGODB_URI= os.environ.get('MONGODB_URI')
if not MONGODB_URI:
    print("Missing MONGODB_URI in .env")
    sys.exit(1)
MONGODB_DB= os.environ.get('MONGODB_DB')
if not MONGODB_DB:
    print("Missing MONGODB_DB in .env")
    sys.exit(1)
MONGODB_COLLECTION= os.environ.get('MONGODB_COLLECTION')
if not MONGODB_COLLECTION:
    print("Missing MONGODB_COLLECTION in .env")
    sys.exit(1)