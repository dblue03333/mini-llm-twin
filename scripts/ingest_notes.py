#notes
#{id: '', source: '', created_at: '', text: '', metadata: {'path':, type :'note'},  }

#IMPORTS
import json
import hashlib
import datetime
import re
from pathlib import Path
from datetime import datetime, timezone
import sys

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


# test = """\r\n
#         Title\r\n
#         \r\n
#         Line 1    
#         \r\n
#         \r\n
#         Line 2\r
#         \r\n"""
# print(normalize_text(test))

#PARSE DATETIME

#
