#notes
#{id: '', source: '', created_at: '', text: '', metadata: {'path':, type :'note'},  }

# IMPORTS
import argparse
import time
import logging

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone
import requests

import sys
from dotenv import load_dotenv
import os
load_dotenv()


# PATH SETUP
TITLE_PROPERTY_NAME = os.environ.get("TITLE_PROPERTY_NAME", "Date")
if not TITLE_PROPERTY_NAME:
    print("Missing TITLE_PROPERTY_NAME in .env")
    sys.exit(1)

NOTION_VERSION = os.environ.get("NOTION_VERSION", "2022-06-28")
if not NOTION_VERSION:
    print("Missing NOTION_VERSION in .env")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT/'data'

BRONZE_PATH = DATA_DIR / 'bronze' / 'notion_raw.jsonl'
SILVER_PATH = DATA_DIR / 'silver' / 'documents.jsonl'
STATE_PATH = DATA_DIR / "state" / "notion_state.json"

#preventing no missing folder
BRONZE_PATH.parent.mkdir(parents=True, exist_ok=True)
SILVER_PATH.parent.mkdir(parents=True, exist_ok=True)
STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


#NOTION SETUP
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
if not NOTION_TOKEN:
    print("Missing NOTION_TOKEN in .env")
    sys.exit(1)

NOTION_DB_ID = os.environ.get("NOTION_DB_ID")
if not NOTION_DB_ID:
    print("Missing NOTION_DB_ID in .env")
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument('--page-size', type=int, default=5)
parser.add_argument('--max-pages', type=int, default=None)
parser.add_argument('--force', action='store_true')
args = parser.parse_args()

#Time out and retry constant 
HTTP_TIMEOUT = 30
MAX_RETRIES = 3

#Log defining
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | %(message)s',
)
log = logging.getLogger(__name__)

#Log value counts
fetched = 0
processed = 0
skipped = 0
errors = 0

#NORMALIZE TEXT
def normalize_text(text: str) -> str:

    # This will convert win and old mac format to \n
    # \r\n is format from win
    # \r is format from mac
    text = text.replace('\r\n', '\n').replace('\r','\n')

    lines = text.split('\n')

    # delete blank line in top and bottom of content
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    # delete blank line between content
    normalized = []
    blank = False
    for line in lines:
        if line.strip() == "":
            if not blank:
                normalized.append("")
            blank=True
        else:
            normalized.append(line.rstrip())
            blank=False

    return '\n'.join(normalized)



header = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Notion-Version': f'{NOTION_VERSION}',
    'Content-Type': 'application/json'
}

# NORMALIZE CONTENT BY BLOCK TYPE
def join_rich_text(rich_text):
    return "".join(t.get("plain_text", "") for t in rich_text)


def extract_page_title(page: dict, configured_property_name: str) -> str:
    """Return a best-effort page title without crashing on property type mismatches."""
    properties = page.get("properties", {})

    configured_prop = properties.get(configured_property_name)
    if isinstance(configured_prop, dict):
        if configured_prop.get("type") == "title":
            return join_rich_text(configured_prop.get("title", []))
        log.warning(
            "configured title property is not type=title (name=%s, type=%s); falling back",
            configured_property_name,
            configured_prop.get("type"),
        )

    for prop in properties.values():
        if isinstance(prop, dict) and prop.get("type") == "title":
            return join_rich_text(prop.get("title", []))

    return "Untitled"


def block_to_text(block):
    prefix = {
        "heading_1": "# ",
        "heading_2": "## ",
        "heading_3": "### ",
        "bulleted_list_item": "- ",
        "numbered_list_item": "1. ",
        "quote": "> ",
        "paragraph": "",
    }

    block_type = block["type"]

    if block_type == "to_do":
        prefix_text = "[x] " if block["to_do"]["checked"] else "[ ] "
        return prefix_text + join_rich_text(block["to_do"]["rich_text"])

    if block_type == "code":
        lang = block["code"].get("language", "")
        code_text = join_rich_text(block["code"]["rich_text"])
        return f"```{lang}\n{code_text}\n```"

    if block_type in prefix:
        return prefix[block_type] + join_rich_text(block[block_type]["rich_text"])

    return ""


#SAVING CONTENT TO JSON
def write_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_state(path: Path) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(path: Path, state: dict) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    tmp_path.replace(path)

def request_json(method: str, url: str, *, headers: dict, json_body: dict | None = None):
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.request(
                method,
                url,
                headers=headers,
                json=json_body,
                timeout=HTTP_TIMEOUT,
            )
        except requests.RequestException as e:
            last_exc = e
            sleep_s = 2 ** attempt
            log.warning("request error, retrying in %ss: %s %s (%s)", sleep_s, method, url, e)
            time.sleep(sleep_s)
            continue

        status = r.status_code

        if status in (401, 403):
            log.error("auth error status=%s method=%s url=%s body=%s", status, method, url, r.text[:200])
            sys.exit(1)

        if status == 429:
            sleep_s = 2 ** attempt
            log.warning("rate limited (429), sleeping %ss: %s %s", sleep_s, method, url)
            time.sleep(sleep_s)
            continue

        if status >= 500:
            sleep_s = 2 ** attempt
            log.warning("server error status=%s, retrying in %ss: %s %s", status, sleep_s, method, url)
            time.sleep(sleep_s)
            continue

        if status >= 400:
            log.error("http error status=%s method=%s url=%s body=%s", status, method, url, r.text[:200])
            raise RuntimeError(f"http {status} for {method} {url}")

        try:
            return r.json()
        except ValueError as e:
            log.error("json decode error method=%s url=%s body=%s", method, url, r.text[:200])
            raise RuntimeError(f"invalid json for {method} {url}") from e

    log.error("failed after retries method=%s url=%s", method, url)
    raise RuntimeError(f"request failed after {MAX_RETRIES} retries: {method} {url}") from last_exc


link = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"

all_pages = []
has_more = True

start_cursor = None

while has_more:
    payload = {'page_size': args.page_size}
    if start_cursor:
        payload['start_cursor'] = start_cursor
    
    try:
        data = request_json("POST", link, headers=header, json_body=payload)
    except RuntimeError as e:
        log.error("%s", e)
        errors += 1
        break
    all_pages.extend(data.get('results', []))
    has_more = data.get('has_more',False)
    start_cursor = data.get('next_cursor')

fetched = len(all_pages)
log.info("fetched=%d", fetched)

# PAGE ID
# page_id = r.json().get('results', [])[0]['id']
processed_pages = 0
notion_state = load_state(STATE_PATH)
pages_last_edited = notion_state.get('pages_last_edited', {})
for page in all_pages:
    page_id = page['id']
    title = extract_page_title(page, TITLE_PROPERTY_NAME)
    created_time = page['created_time']
    last_edited_time = page['last_edited_time']
    if (not args.force) and page_id in pages_last_edited and pages_last_edited[page_id] == last_edited_time:
        skipped += 1
        log.info('skipped page_id=%s', page_id)
        continue
    # GETTING PAGE CONTENT

    page_link = f'https://api.notion.com/v1/blocks/{page_id}/children'
    try:
        # page_r = requests.get(page_link, headers=header)
        # page_r.raise_for_status()
        # blocks = page_r.json(). get("results", [])
        data = request_json("GET", page_link, headers=header)
        blocks = data.get('results', [])
    except RuntimeError as e:
        log.error("block fetch failed page_id=%s (%s)", page_id, e)
        errors += 1
        continue

    #GETTING LINES BY LINES IN BLOCK
    lines = [block_to_text(b) for b in blocks]
    raw_text = '\n'.join(lines)

    ######BRONZE + SILVER PHASE########
    bronze_record = {
        "id": page_id,
        "created_time": created_time,
        "title": title,
        "text": raw_text,
        "last_edited_time": last_edited_time
    }

    silver_record = {
        "id": page_id,
        "type": "article",
        "text": normalize_text(raw_text),
        "created_at": created_time,
        "updated_at": last_edited_time,
        "metadata": {
            "source": "notion",
            "title": title
        }
    }

    write_jsonl(BRONZE_PATH, bronze_record)
    write_jsonl(SILVER_PATH, silver_record)
    processed += 1
    pages_last_edited[page_id] = last_edited_time
    processed_pages += 1
    if args.max_pages is not None and processed_pages >= args.max_pages:
        break

    

# State Management
#schema: pages_last_edited: {page_id: last_edited_time}
# last_sync: ISO timestamp
# rules:
### not page_id -> process
### last_edited_time differs -> procese
### else -> skip

notion_state['pages_last_edited'] = pages_last_edited
notion_state["last_sync"] = datetime.now(timezone.utc).isoformat()
save_state(STATE_PATH, notion_state)

log.info("processed=%d skipped=%d errors=%d", processed, skipped, errors)
