#notes
#{id: '', source: '', created_at: '', text: '', metadata: {'path':, type :'note'},  }

#IMPORTS
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
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
if not NOTION_TOKEN:
    print("Missing NOTION_TOKEN in .env")
    sys.exit(1)

NOTION_DB_ID = os.environ.get("NOTION_DB_ID")
if not NOTION_DB_ID:
    print("Missing NOTION_DB_ID in .env")
    sys.exit(1)


#NORMALIZE
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
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

link = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
r = requests.post(link, headers=header, json={'page_size':5})
# print(r.text)
print(r.status_code)
print(r.json())

