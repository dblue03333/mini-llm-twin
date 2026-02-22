from src.config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION, SILVER_PATH
from pymongo import MongoClient
from src.utils.io import iter_jsonl
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")  
log.info("connected db=%s collection=%s", MONGODB_DB, MONGODB_COLLECTION)

db = client[MONGODB_DB]
collection = db[MONGODB_COLLECTION]

#unique key filder
# {metadata.source, id}

#Creating unique identity key
collection.create_index([('metadata.source', 1), ('id', 1)], unique=True, name='uniq_source_id')
# performance indexes
collection.create_index([("metadata.source", 1)], name="idx_source")
collection.create_index([("type", 1)], name="idx_type")
collection.create_index([("updated_at", -1)], name="idx_updated_at")

documents = iter_jsonl(SILVER_PATH)
failed, inserted, updated, skipped = 0, 0, 0, 0
for doc in documents:
    try:
        if doc.get("_error"):
            failed += 1
            log.error(
                "failed line=%s reason=%s preview=%s",
                doc.get("_line_no"),
                doc.get("_error"),
                doc.get("_raw_preview"),
            )
            continue
        doc_id = doc.get("id")
        source = doc.get("metadata", {}).get("source")
        if not doc_id or not source:
            failed += 1
            continue
        flt = {"metadata.source": source, "id": doc_id}
        incoming_updated_at = doc.get("updated_at") #str
        if not incoming_updated_at: 
            failed += 1
            continue
        try:
            incoming_dt = datetime.fromisoformat(incoming_updated_at.replace("Z", "+00:00"))
        except ValueError:
            failed += 1
            log.error(
                "failed doc_id=%s reason=invalid_updated_at value=%s",
                doc.get("id"),
                incoming_updated_at,
            )
            continue
        existing = collection.find_one(flt, {"updated_at": 1})#str
        if existing and existing.get("updated_at"):
            try:
                existing_dt = datetime.fromisoformat(existing["updated_at"].replace("Z", "+00:00"))
            except ValueError:
                existing_dt = None
            if existing_dt and existing_dt > incoming_dt:
                skipped += 1
                continue
        text = doc.get('text')
        if not isinstance(text,str) or not text.strip():
            failed += 1
            log.error("failed doc_id=%s reason=missing_or_empty_text", doc.get("id"))
            continue
        res = collection.update_one(flt, {"$set": doc}, upsert=True)
        if res.upserted_id:
            inserted += 1
        elif res.modified_count > 0:
            updated += 1
        else:
            skipped += 1
    except Exception as e:
        failed += 1
        log.exception("failed doc_id=%s error=%s", doc.get("id"), e)
        continue
log.info("inserted=%d updated=%d skipped=%d failed=%d", inserted, updated, skipped, failed)
    
