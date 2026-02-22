from src.config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION, SILVER_PATH
from pymongo import MongoClient
from src.utils.io import iter_jsonl
from datetime import datetime
import logging
import argparse
import time

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true", help="Validate and classify docs without writing to MongoDB")
parser.add_argument("--limit", type=int, default=None, help="Process only the first N records (for debugging)")
args = parser.parse_args()
dry_run = args.dry_run
limit = args.limit
run_id = datetime.utcnow().isoformat() + "Z"
started_at = time.monotonic()
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")  
log.info("connected db=%s collection=%s", MONGODB_DB, MONGODB_COLLECTION)

db = client[MONGODB_DB]
collection = db[MONGODB_COLLECTION]

#unique key filder
# {metadata.source, id}

#Creating unique identity key
if dry_run:
    log.info("dry-run mode: skipping index creation")
else:
    collection.create_index([('metadata.source', 1), ('id', 1)], unique=True, name='uniq_source_id')
    # performance indexes
    collection.create_index([("metadata.source", 1)], name="idx_source")
    collection.create_index([("type", 1)], name="idx_type")
    collection.create_index([("updated_at", -1)], name="idx_updated_at")

documents = iter_jsonl(SILVER_PATH)
failed, inserted, updated, skipped = 0, 0, 0, 0
would_insert, would_update, would_skip = 0, 0, 0
processed = 0
log.info(
    "start run_id=%s mode=%s file=%s limit=%s db=%s collection=%s",
    run_id,
    "dry-run" if dry_run else "write",
    SILVER_PATH,
    limit,
    MONGODB_DB,
    MONGODB_COLLECTION,
)

for processed, doc in enumerate(documents, start=1):
    if limit is not None and processed > limit:
        break
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
            log.error("failed doc_id=%s reason=missing_id_or_source source=%s", doc_id, source)
            continue
        flt = {"metadata.source": source, "id": doc_id}
        incoming_updated_at = doc.get("updated_at") #str
        if not incoming_updated_at: 
            failed += 1
            log.error("failed doc_id=%s reason=missing_updated_at", doc_id)
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
                if dry_run:
                    would_skip += 1
                else: skipped += 1
                continue
        text = doc.get('text')
        if not isinstance(text,str) or not text.strip():
            failed += 1
            log.error("failed doc_id=%s reason=missing_or_empty_text", doc.get("id"))
            continue
        # Tombstone-ready behavior: any document present in the current source snapshot is active.
        # Future reconciliation can mark missing docs as deleted without changing loader contract.
        doc_to_write = {
            **doc,
            "is_deleted": False,
            "deleted_at": None,
            "deleted_reason": None,
        }
        if dry_run:
            if existing is None:
                would_insert += 1
            else: would_update += 1
        else:
            res = collection.update_one(flt, {"$set": doc_to_write}, upsert=True)
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
duration_s = time.monotonic() - started_at
if dry_run:
    log.info(
        "end run_id=%s mode=dry-run processed=%d would_insert=%d would_update=%d would_skip=%d failed=%d duration_s=%.3f",
        run_id, processed, would_insert, would_update, would_skip, failed, duration_s
    )
else:
    log.info(
        "end run_id=%s mode=write processed=%d inserted=%d updated=%d skipped=%d failed=%d duration_s=%.3f",
        run_id, processed, inserted, updated, skipped, failed, duration_s
    )
    
