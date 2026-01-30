#notes
#{id: '', source: '', created_at: '', text: '', metadata: {'path':, type :'note'},  }

# IMPORTS
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

NOTION_VERSION = os.environ.get("NOTION_VERSION", "2025-09-03")
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
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(path: Path, state: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


link = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"

all_pages = []
has_more = True
start_cursor = None

while has_more:
    payload = {'page_size':5}
    if start_cursor:
        payload['start_cursor'] = start_cursor
    
    try:
        r = requests.post(link, headers=header, json=payload)
        r.raise_for_status()
        data = r.json()
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else "unknown"
        body = (e.response.text[:200] if e.response and e.response.text else "")
        print(f"HTTP error: {e} | status={status} | body={body}")
        break
    except ValueError as e:
        print(f"JSON error: {e} | body={r.text[:200]}")
        break

    all_pages.extend(data.get('results', []))
    has_more = data.get('has_more',False)
    start_cursor = data.get('next_cursor')

# PAGE ID
# page_id = r.json().get('results', [])[0]['id']
for page in all_pages:
    page_id = page['id']
    title = "".join(item.get("plain_text","") for item in page['properties'][TITLE_PROPERTY_NAME]['title'])
    created_time = page['created_time']
    last_edited_time = page['last_edited_time']
    # GETTING PAGE CONTENT

    page_link = f'https://api.notion.com/v1/blocks/{page_id}/children'
    try:
        page_r = requests.get(page_link, headers=header)
        page_r.raise_for_status()
        blocks = page_r.json().get("results", [])
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else "unknown"
        print(f"Block HTTP error for page {page_id}: {status}")
        continue
    except ValueError as e:
        print(f"Block JSON error for page {page_id}: {e}")
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
